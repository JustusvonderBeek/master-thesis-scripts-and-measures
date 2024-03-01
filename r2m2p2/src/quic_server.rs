/* The server implementation of quic sending and receiving STUN */

use std::net::SocketAddr;

use anyhow::Error;
use ring::rand::SystemRandom;

use crate::common::{bind_mio_socket, bind_socket, create_quic_conf, generate_cid_and_reset_token, send_to, send_to_mio, Client, ClientIdMap, ClientMap, STUN_TEST_ALPN};

const MAX_BUF_SIZE: usize = 65507;
const MAX_DATAGRAM_SIZE: usize = 1350;

fn create_new_token(hdr: &quiche::Header, from: &SocketAddr) -> Vec<u8> {
    let mut token = Vec::new();
    token.extend_from_slice(b"quiche");

    let addr = match from.ip() {
        std::net::IpAddr::V4(a) => a.octets().to_vec(),
        std::net::IpAddr::V6(a) => a.octets().to_vec(),
    };

    token.extend_from_slice(&addr);
    token.extend_from_slice(&hdr.dcid);

    token
}

fn validate_token<'a>(from: &SocketAddr, token: &'a [u8]) -> Option<quiche::ConnectionId<'a>> {
    if token.len() < 6 {
        return None;
    }

    if &token[..6] != b"quiche" {
        return None;
    }

    let token = &token[6..];
    let addr = match from.ip() {
        std::net::IpAddr::V4(a) => a.octets().to_vec(),
        std::net::IpAddr::V6(a) => a.octets().to_vec(),
    };
    if token.len() < addr.len() || &token[..addr.len()] != addr.as_slice() {
        return None;
    }

    Some(quiche::ConnectionId::from_ref(&token[addr.len()..]))
}

fn handle_path_events(client: &mut Client) {
    while let Some(qe) = client.conn.path_event_next() {
        match qe {
            quiche::PathEvent::New(local_addr, peer_addr) => {
                info!(
                    "{} Seen new path ({}, {})",
                    client.conn.trace_id(),
                    local_addr,
                    peer_addr
                );

                // Directly probe the new path.
                client
                    .conn
                    .probe_path(local_addr, peer_addr)
                    .map_err(|e| error!("cannot probe: {}", e))
                    .ok();
            },

            quiche::PathEvent::Validated(local_addr, peer_addr) => {
                info!(
                    "{} Path ({}, {}) is now validated",
                    client.conn.trace_id(),
                    local_addr,
                    peer_addr
                );
                if client.conn.is_multipath_enabled() {
                    client
                        .conn
                        .set_active(local_addr, peer_addr, true)
                        .map_err(|e| error!("cannot set path active: {}", e))
                        .ok();
                }
            },

            quiche::PathEvent::FailedValidation(local_addr, peer_addr) => {
                info!(
                    "{} Path ({}, {}) failed validation",
                    client.conn.trace_id(),
                    local_addr,
                    peer_addr
                );
            },

            quiche::PathEvent::Closed(local_addr, peer_addr, err, reason) => {
                info!(
                    "{} Path ({}, {}) is now closed and unusable; err = {} reason = {:?}",
                    client.conn.trace_id(),
                    local_addr,
                    peer_addr,
                    err,
                    reason,
                );
            },

            quiche::PathEvent::ReusedSourceConnectionId(cid_seq, old, new) => {
                info!(
                    "{} Peer reused cid seq {} (initially {:?}) on {:?}",
                    client.conn.trace_id(),
                    cid_seq,
                    old,
                    new
                );
            },

            quiche::PathEvent::PeerMigrated(local_addr, peer_addr) => {
                info!(
                    "{} Connection migrated to ({}, {})",
                    client.conn.trace_id(),
                    local_addr,
                    peer_addr
                );
            },

            quiche::PathEvent::PeerPathStatus(addr, path_status) => {
                info!("Peer asks status {:?} for {:?}", path_status, addr,);
                client
                    .conn
                    .set_path_status(addr.0, addr.1, path_status, false)
                    .map_err(|e| error!("cannot follow status request: {}", e))
                    .ok();
            },
        }
    }
}

pub fn start_server() -> Result<(), Error> {
    // TODO: Add some termination token to cancel the server
    // gracefully

    let mut socket = bind_mio_socket(Some("0.0.0.0:12345")).unwrap();

    let mut buf = [0; MAX_BUF_SIZE];
    let mut out = [0; MAX_BUF_SIZE];

    info!("Listening on: {:}", socket.local_addr().unwrap());

    let mut config = quiche::Config::new(quiche::PROTOCOL_VERSION).unwrap();

    config.load_cert_chain_from_pem_file("resources/cert.crt").unwrap();
    config.load_priv_key_from_pem_file("resources/cert.key").unwrap();
    create_quic_conf(&mut config);

    debug!("Config created and cert loaded");

    let rng = SystemRandom::new();
    let conn_id_seed =
        ring::hmac::Key::generate(ring::hmac::HMAC_SHA256, &rng).unwrap();

    let mut next_client_id = 0;
    let mut clients_ids = ClientIdMap::new();
    let mut clients = ClientMap::new();

    let mut pkt_count = 0;

    let mut continue_write = false;

    let local_addr = socket.local_addr().unwrap();

    // TODO: Using mio's polling because it's faster and more universal than tokio
    // Converting from tokio to mio is also easier possible than the other way around
    let mut poll = mio::Poll::new().unwrap();
    let mut events = mio::Events::with_capacity(1024);

    // Allow polling in case we have a read event
    poll.registry().register(&mut socket, mio::Token(0), mio::Interest::READABLE).unwrap();

    loop {

        // Continue write
        let timeout = match continue_write {
            true => Some(std::time::Duration::from_secs(0)),
            false => clients.values().filter_map(|c| c.conn.timeout()).min(),
        };

        poll.poll(&mut events, timeout).unwrap();

        'read: loop {

            // Using the polling way of reading from the socket
            if events.is_empty() && !continue_write {
                // Timed out
                trace!("timed out");

                clients.values_mut().for_each(|c| c.conn.on_timeout());

                break 'read;
            }

            let (len, from) = match socket.recv_from(&mut buf) {
                Ok(v) => v,
                Err(e) => {
                    if e.kind() == std::io::ErrorKind::WouldBlock {
                        trace!("recv() would block");
                        break 'read;
                    }
                    panic!("recv_from() failed: {:?}", e);
                }
            };

            trace!("Got {} bytes", len);
            pkt_count += 1;
            let pkt_buf = &mut buf[..len];

            // Parsing the header
            let hdr = match quiche::Header::from_slice(
                pkt_buf,
                quiche::MAX_CONN_ID_LEN,
            ) {
                Ok(v) => v,
                Err(e) => {
                    error!("Parsing packet header failed: {:?}", e);
                    continue 'read;
                },
            };

            trace!("Got packet: {:?}", hdr);

            let conn_id = ring::hmac::sign(&conn_id_seed, &hdr.dcid);
            let conn_id = &conn_id.as_ref()[..quiche::MAX_CONN_ID_LEN];
            let conn_id = conn_id.to_vec().into();

            let client = if !clients_ids.contains_key(&hdr.dcid) &&
                !clients_ids.contains_key(&conn_id)
            {
                if hdr.ty != quiche::Type::Initial {
                    error!("Packet is not Initial");
                    continue 'read;
                }

                if !quiche::version_is_supported(hdr.version) {
                    warn!("Doing version negotiation");

                    let len =
                        quiche::negotiate_version(&hdr.scid, &hdr.dcid, &mut out)
                            .unwrap();

                    let out = &out[..len];

                    if let Err(e) = socket.send_to(out, from) {
                        if e.kind() == std::io::ErrorKind::WouldBlock {
                            trace!("send() would block");
                            break;
                        }

                        panic!("send() failed: {:?}", e);
                    }
                    continue 'read;
                }

                let mut scid = [0; quiche::MAX_CONN_ID_LEN];
                scid.copy_from_slice(&conn_id);

                let mut odcid = None;

                // Retrying
                // Token is always present in Initial packets.
                let token = hdr.token.as_ref().unwrap();

                // Do stateless retry if the client didn't send a token.
                if token.is_empty() {
                    warn!("Doing stateless retry");

                    let scid = quiche::ConnectionId::from_ref(&scid);
                    let new_token = create_new_token(&hdr, &from);

                    let len = quiche::retry(
                        &hdr.scid,
                        &hdr.dcid,
                        &scid,
                        &new_token,
                        hdr.version,
                        &mut out,
                    )
                    .unwrap();

                    let out = &out[..len];

                    if let Err(e) = socket.send_to(out, from) {
                        if e.kind() == std::io::ErrorKind::WouldBlock {
                            trace!("send() would block");
                            break;
                        }

                        panic!("send() failed: {:?}", e);
                    }
                    continue 'read;
                }

                odcid = validate_token(&from, token);

                // The token was not valid, meaning the retry failed, so
                // drop the packet.
                if odcid.is_none() {
                    error!("Invalid address validation token");
                    continue;
                }

                if scid.len() != hdr.dcid.len() {
                    error!("Invalid destination connection ID");
                    continue 'read;
                }

                // Reuse the source connection ID we sent in the Retry
                // packet, instead of changing it again.
                scid.copy_from_slice(&hdr.dcid);

                // Finished retry

                let scid = quiche::ConnectionId::from_vec(scid.to_vec());

                debug!("New connection: dcid={:?} scid={:?}", hdr.dcid, scid);

                #[allow(unused_mut)]
                let mut conn = quiche::accept(
                    &scid,
                    odcid.as_ref(),
                    local_addr,
                    from,
                    &mut config,
                )
                .unwrap();

                // FIXME: Allow logging keys if set
                // if let Some(keylog) = &mut keylog {
                //     if let Ok(keylog) = keylog.try_clone() {
                //         conn.set_keylog(Box::new(keylog));
                //     }
                // }

                // Only bother with qlog if the user specified it.
                #[cfg(feature = "qlog")]
                {
                    if let Some(dir) = std::env::var_os("QLOGDIR") {
                        let id = format!("{:?}", &scid);
                        let writer = make_qlog_writer(&dir, "server", &id);

                        conn.set_qlog(
                            std::boxed::Box::new(writer),
                            "quiche-server qlog".to_string(),
                            format!("{} id={}", "quiche-server qlog", id),
                        );
                    }
                }

                let client_id = next_client_id;

                let client = Client {
                    conn,
                    client_id,
                    app_proto_selected: false,
                    max_datagram_size: MAX_DATAGRAM_SIZE,
                    loss_rate: 0.0,
                    max_send_burst: MAX_BUF_SIZE,
                };

                clients.insert(client_id, client);
                clients_ids.insert(scid.clone(), client_id);

                next_client_id += 1;

                clients.get_mut(&client_id).unwrap()
            } else {
                let cid = match clients_ids.get(&hdr.dcid) {
                    Some(v) => v,

                    None => clients_ids.get(&conn_id).unwrap(),
                };

                clients.get_mut(cid).unwrap()
            };

            let recv_info = quiche::RecvInfo {
                to: local_addr,
                from,
            };

            // Process potentially coalesced packets
            // inside of QUICHE
            let read = match client.conn.recv(pkt_buf, recv_info) {
                Ok(v) => v,
                Err(e) => {
                    error!("{} recv failed: {:?}", client.conn.trace_id(), e);
                    continue 'read;
                },
            };

            trace!("{} processed {} bytes", client.conn.trace_id(), read);

            // Create a new application protocol session as soon as the QUIC
            // connection is established.
            if !client.app_proto_selected &&
                (client.conn.is_in_early_data() ||
                    client.conn.is_established())
            {
                // Normally we would perform some application proto
                // selection. Here we simply expect it to be raw data
                // and therefore chose our test protocol
                let app_proto = client.conn.application_proto();

                if STUN_TEST_ALPN.contains(&app_proto) {
                    info!("Connection established. Selecting QUICHESTUN protocol.");
                    // client.protocol = Some(Protocol::new_with_password(self.password.clone()));

                } else {
                    warn!("ALPN did not match {:?}: {:?}", STUN_TEST_ALPN, app_proto);
                    client.conn.close(false, 0x1, b"No ALPN match").ok();
                }

                client.app_proto_selected = true;
                client.max_datagram_size = client.conn.max_send_udp_payload_size();
            }

            handle_path_events(client);

            // See whether source Connection IDs have been retired.
            while let Some(retired_scid) = client.conn.retired_scid_next() {
                info!("Retiring source CID {:?}", retired_scid);
                clients_ids.remove(&retired_scid);
            }

            // Provides as many CIDs as possible.
            while client.conn.source_cids_left() > 0 {
                let (scid, reset_token) = generate_cid_and_reset_token(&rng);
                if client
                    .conn
                    .new_source_cid(&scid, reset_token, false)
                    .is_err()
                {
                    break;
                }

                clients_ids.insert(scid, client.client_id);
            }
        }

        // Generate outgoing QUIC packets for all active connections and send
        // them on the UDP socket, until quiche reports that there are no more
        // packets to be sent.
        continue_write = false;
        for client in clients.values_mut() {
            // Reduce max_send_burst by 25% if loss is increasing more than 0.1%.
            let loss_rate =
                client.conn.stats().lost as f64 / client.conn.stats().sent as f64;
            if loss_rate > client.loss_rate + 0.001 {
                client.max_send_burst = client.max_send_burst / 4 * 3;
                // Minimun bound of 10xMSS.
                client.max_send_burst =
                    client.max_send_burst.max(client.max_datagram_size * 10);
                client.loss_rate = loss_rate;
            }

            let max_send_burst =
                client.conn.send_quantum().min(client.max_send_burst) /
                    client.max_datagram_size *
                    client.max_datagram_size;
            let mut total_write = 0;
            let mut dst_info: Option<quiche::SendInfo> = None;

            while total_write < max_send_burst {
                let res = match dst_info {
                    Some(info) => client.conn.send_on_path(
                        &mut out[total_write..max_send_burst],
                        Some(info.from),
                        Some(info.to),
                    ),
                    None =>
                        client.conn.send(&mut out[total_write..max_send_burst]),
                };

                let (write, send_info) = match res {
                    Ok(v) => v,

                    Err(quiche::Error::Done) => {
                        continue_write = dst_info.is_some();
                        trace!("{} done writing", client.conn.trace_id());
                        break;
                    },

                    Err(e) => {
                        error!("{} send failed: {:?}", client.conn.trace_id(), e);

                        client.conn.close(false, 0x1, b"fail").ok();
                        break;
                    },
                };

                total_write += write;

                // Use the first packet time to send, not the last.
                let _ = dst_info.get_or_insert(send_info);

                if write < client.max_datagram_size {
                    continue_write = true;
                    break;
                }
            }

            if total_write == 0 || dst_info.is_none() {
                break;
            }

            if let Err(e) = send_to_mio(
                &socket,
                &out[..total_write],
                &dst_info.unwrap(),
                client.max_datagram_size,
            ) {
                if e.kind() == std::io::ErrorKind::WouldBlock {
                    trace!("send() would block");
                    break;
                }

                panic!("send_to() failed: {:?}", e);
            }

            trace!("{} written {} bytes", client.conn.trace_id(), total_write);

            if continue_write {
                trace!(
                    "{} pause writing and consider another path",
                    client.conn.trace_id()
                );
                break;
            }

            if total_write >= max_send_burst {
                trace!("{} pause writing", client.conn.trace_id(),);
                continue_write = true;
                break;
            }
        }

        // Garbage collect closed connections.
        clients.retain(|_, ref mut c| {
            trace!("Collecting garbage");

            if c.conn.is_closed() {
                info!(
                    "{} connection collected {:?} {:?}",
                    c.conn.trace_id(),
                    c.conn.stats(),
                    c.conn.path_stats().collect::<Vec<quiche::PathStats>>()
                );

                for id in c.conn.source_ids() {
                    let id_owned = id.clone().into_owned();
                    clients_ids.remove(&id_owned);
                }
            }

            !c.conn.is_closed()
        });
    }

    // return Ok(());
}