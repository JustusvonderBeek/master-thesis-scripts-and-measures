/* Implementing the behavior of the QUIC client. */

use std::{collections::HashMap, fmt::format, io::Error};

use clap::ErrorKind;
use quiche::Connection;
use quicheperf::{client::ClientError, make_quiche_config};
use ring::rand::{SecureRandom, SystemRandom};

use crate::common::{bind_mio_socket, bind_socket, create_quic_client_conf, generate_cid_and_reset_token, STUN_TEST_ALPN};

const MAX_DATAGRAM_SIZE: usize = 1350;


fn handle_path_events(conn: &mut Connection) {
    while let Some(qe) = conn.path_event_next() {
        match qe {
            quiche::PathEvent::New(..) => unreachable!(),
            quiche::PathEvent::Validated(local_addr, peer_addr) => {
                info!(
                    "Path ({}, {}) is now validated",
                    local_addr, peer_addr
                );
                // Because multipath is enabled (by me)
                conn.set_active(local_addr, peer_addr, true).ok();
                // if conn_args.multipath {
                //     conn.set_active(local_addr, peer_addr, true).ok();
                // } else if args.perform_migration {
                //     conn.migrate(local_addr, peer_addr).unwrap();
                //     migrated = true;
                // }
            },
            quiche::PathEvent::FailedValidation(local_addr, peer_addr) => {
                info!(
                    "Path ({}, {}) failed validation",
                    local_addr, peer_addr
                );
            },
            quiche::PathEvent::Closed(local_addr, peer_addr, e, reason) => {
                info!(
                    "Path ({}, {}) is now closed and unusable; err = {}, reason = {:?}",
                    local_addr, peer_addr, e, reason
                );
            },
            quiche::PathEvent::ReusedSourceConnectionId(
                cid_seq,
                old,
                new,
            ) => {
                info!(
                    "Peer reused cid seq {} (initially {:?}) on {:?}",
                    cid_seq, old, new
                );
            },
            quiche::PathEvent::PeerMigrated(..) => unreachable!(),
            quiche::PathEvent::PeerPathStatus(..) => {},
        }
    }
}

/// Generate a ordered list of 4-tuples on which the host should send packets,
/// following a lowest-latency scheduling.
fn lowest_latency_scheduler(
    conn: &quiche::Connection,
) -> impl Iterator<Item = (std::net::SocketAddr, std::net::SocketAddr)> {
    use itertools::Itertools;
    conn.path_stats()
        .sorted_by_key(|p| p.rtt)
        .map(|p| (p.local_addr, p.peer_addr))
}

pub fn connect(remote : &str) -> Result<(), std::io::Error> {
    // Bind to local socket
    // Connect to remote endpoint
    // Exchange data
    let mut buf = [0; 65535];
    let mut out = [0; MAX_DATAGRAM_SIZE];

    let mut socket = bind_mio_socket(None).unwrap();

    let mut config = create_quic_client_conf().unwrap();

    let mut app_proto_selected = false;
    // Generate a random source connection ID for the connection.
    let mut scid = [0; quiche::MAX_CONN_ID_LEN];
    let rng = SystemRandom::new();
    rng.fill(&mut scid[..]).unwrap();
    
    let scid = quiche::ConnectionId::from_ref(&scid);

    let local_addr = socket.local_addr().unwrap();
    let peer_addr = remote.parse().unwrap();
    // Create a QUIC connection and initiate handshake.
    let mut conn = quiche::connect(
        None,
        &scid,
        local_addr,
        peer_addr,
        &mut config,
    )
    .unwrap();

    // TODO: Allow storing keylogs etc.

    info!(
        "connecting to {:} from {:} with scid {:?}",
        peer_addr, local_addr, scid,
    );

    let (write, send_info) = conn.send(&mut out).expect("initial send failed");
    
    while let Err(e) = socket.send_to(&out[..write], send_info.to) {
        if e.kind() == std::io::ErrorKind::WouldBlock {
            trace!("send() would block");
            continue;
        }
        return Err(e);
    }

    trace!("Written {}", write);

    let app_data_start = std::time::Instant::now();

    let mut probed_paths = 0;
    let mut pkt_count = 0;

    let mut scid_sent = false;
    let mut new_path_probed = false;
    let mut migrated = false;

    // Setup the event loop.
    let mut poll = mio::Poll::new().unwrap();
    let mut events = mio::Events::with_capacity(1024);

    // Register the socket to spit out events
    poll.registry().register(&mut socket, mio::Token(0), mio::Interest::READABLE).unwrap();

    loop {

        if !conn.is_in_early_data() || app_proto_selected {
            poll.poll(&mut events, conn.timeout()).unwrap();
        }

        if events.is_empty() {
            debug!("timed out");
            conn.on_timeout();
        }

        for _ in &events {
            let local_addr = socket.local_addr().unwrap();

            'read: loop {
                let (len, from) = match socket.recv_from(&mut buf) {
                    Ok(v) => v,
                    Err(e) => {
                        if e.kind() == std::io::ErrorKind::WouldBlock {
                            trace!("recv() would block");
                            break 'read;
                        }
                        return Err(e);
                    },
                };
    
                debug!("{}: got {} bytes", local_addr, len);
                pkt_count += 1;
    
                let recv_info = quiche::RecvInfo {
                    to: local_addr,
                    from,
                };
    
                // Process potentially coalesced packets.
                let read = match conn.recv(&mut buf[..len], recv_info) {
                    Ok(v) => v,
    
                    Err(e) => {
                        error!("{}: recv failed: {:?}", local_addr, e);
                        continue 'read;
                    },
                };
    
                trace!("{}: processed {} bytes", local_addr, read);
            }
        }

        trace!("done reading");

        if conn.is_closed() {

            if !conn.is_established() {
                error!("connection timed out after {:?}", app_data_start.elapsed());

                return Err(Error::new(std::io::ErrorKind::Other, "handshake failed"));
            }

            break;   
        }

        // Create a new application protocol session once the QUIC connection is
        // established.
        // FIXME: false was !args.perform_migration
        if (conn.is_established() || conn.is_in_early_data()) &&
            (false || migrated) &&
            !app_proto_selected
        {
            // At this stage the ALPN negotiation succeeded and selected a
            // single application protocol name. We'll use this to construct
            // the correct type of HttpConn but `application_proto()`
            // returns a slice, so we have to convert it to a str in order
            // to compare to our lists of protocols. We `unwrap()` because
            // we need the value and if something fails at this stage, there
            // is not much anyone can do to recover.

            let app_proto = conn.application_proto();

            if STUN_TEST_ALPN.contains(&app_proto) {
                info!("Connection established. Selecting QUICHESTUN protocol.");
                app_proto_selected = true;
            } else {
                warn!("ALPN did not match {:?}: {:?}", STUN_TEST_ALPN, app_proto);
                conn.close(false, 0x1, b"No ALPN match").ok();
            }
        }

        handle_path_events(&mut conn);

        // See whether source Connection IDs have been retired.
        while let Some(retired_scid) = conn.retired_scid_next() {
            info!("Retiring source CID {:?}", retired_scid);
        }

        // Provides as many CIDs as possible.
        while conn.source_cids_left() > 0 {
            let (scid, reset_token) = generate_cid_and_reset_token(&rng);

            if conn.new_source_cid(&scid, reset_token, false).is_err() {
                break;
            }

            scid_sent = true;
        }

        if true &&
            probed_paths < 1 &&
            conn.available_dcids() > 0 &&
            conn.probe_path(local_addr, peer_addr).is_ok()
        {
            probed_paths += 1;
        }

        // Determine in which order we are going to iterate over paths.
        let scheduled_tuples = lowest_latency_scheduler(&conn);

        // Generate outgoing QUIC packets and send them on the UDP socket, until
        // quiche reports that there are no more packets to be sent.
        for (local_addr, peer_addr) in scheduled_tuples {
            loop {
                let (write, send_info) = match conn.send_on_path(
                    &mut out,
                    Some(local_addr),
                    Some(peer_addr),
                ) {
                    Ok(v) => v,

                    Err(quiche::Error::Done) => {
                        trace!("{} -> {}: done writing", local_addr, peer_addr);
                        break;
                    },

                    Err(e) => {
                        error!(
                            "{} -> {}: send failed: {:?}",
                            local_addr, peer_addr, e
                        );

                        conn.close(false, 0x1, b"fail").ok();
                        break;
                    },
                };

                if let Err(e) = socket.send_to(&out[..write], send_info.to) {
                    if e.kind() == std::io::ErrorKind::WouldBlock {
                        trace!(
                            "{} -> {}: send() would block",
                            local_addr,
                            send_info.to
                        );
                        break;
                    }

                    return Err(e);
                }

                trace!("{} -> {}: written {}", local_addr, send_info.to, write);
            }
        }

        if conn.is_closed() {
            info!("connection closed");

            break;
        }

    }
    
    return Ok(())
}