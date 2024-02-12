// Copyright (C) 2018-2019, Cloudflare, Inc.
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are
// met:
//
//     * Redistributions of source code must retain the above copyright notice,
//       this list of conditions and the following disclaimer.
//
//     * Redistributions in binary form must reproduce the above copyright
//       notice, this list of conditions and the following disclaimer in the
//       documentation and/or other materials provided with the distribution.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
// IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
// THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
// PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
// CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
// EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
// PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
// PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
// LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
// NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
// SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#[macro_use]
extern crate log;

#[macro_use]
extern crate lazy_static;

use std::f32::consts::E;
use std::net::{self, Ipv4Addr, SocketAddrV4};
use std::sync::Arc;
use std::collections::HashMap;

use anyhow::{Error, Result};
use quiche::Config;
use tokio::net::unix::SocketAddr;
use tokio::net::UdpSocket;
use webrtc::api::interceptor_registry::register_default_interceptors;
use webrtc::api::media_engine::MediaEngine;
use webrtc::api::APIBuilder;
use webrtc::ice_transport::ice_server::RTCIceServer;
use webrtc::interceptor::registry::Registry;
use webrtc::peer_connection::configuration::RTCConfiguration;
use webrtc::peer_connection::RTCPeerConnection;
use webrtc_ice::state::ConnectionState;
use webrtc_ice::candidate::Candidate;
use webrtc_ice::network_type::NetworkType;
use webrtc_ice::udp_network::{self, UDPNetwork};
use webrtc_ice::udp_mux::{UDPMuxParams, UDPMuxDefault};
use webrtc_ice::agent::{self, agent_config::AgentConfig, Agent};

use hyper::service::{make_service_fn, service_fn};
use hyper::{Body, Method, Request, Response, Server, StatusCode};

use ring::rand::*;

use crate::multiplexer::is_packet_quic;

mod ice;
mod multiplexer;

// use ice::handle_ice;

const MAX_DATAGRAM_SIZE: usize = 1350;

struct PartialResponse {
    body: Vec<u8>,

    written: usize,
}

struct Client {
    conn: quiche::Connection,

    partial_responses: HashMap<u64, PartialResponse>,
}

type ClientMap = HashMap<quiche::ConnectionId<'static>, Client>;

fn configure_quic(config: &mut Config) {
    config
        .load_cert_chain_from_pem_file("resources/cert.crt")
        .unwrap();
    config
        .load_priv_key_from_pem_file("resources/cert.key")
        .unwrap();

    config
        .set_application_protos(&[
            b"hq-interop",
            b"hq-29",
            b"hq-28",
            b"hq-27",
            b"http/0.9",
        ])
        .unwrap();

    config.set_max_idle_timeout(5000);
    config.set_max_recv_udp_payload_size(MAX_DATAGRAM_SIZE);
    config.set_max_send_udp_payload_size(MAX_DATAGRAM_SIZE);
    config.set_initial_max_data(10_000_000);
    config.set_initial_max_stream_data_bidi_local(1_000_000);
    config.set_initial_max_stream_data_bidi_remote(1_000_000);
    config.set_initial_max_stream_data_uni(1_000_000);
    config.set_initial_max_streams_bidi(100);
    config.set_initial_max_streams_uni(100);
    config.set_disable_active_migration(true);
    config.enable_early_data();
}


async fn start_ice_agent(udp_socket: tokio::net::UdpSocket) -> Result<()> {
    // Setup the QUIC & ICE parts
    // FIXME: Fix the trait not implemented
    
    // Multiplex the connection onto an existing udp connection
    let udp_mux = UDPMuxDefault::new(UDPMuxParams::new(udp_socket));
    let udp_network = UDPNetwork::Muxed(udp_mux);

    let ice_agent = Arc::new(
        Agent::new(AgentConfig {
            network_types: vec![NetworkType::Udp4],
            udp_network,
            ..Default::default()
        })
        .await?,
    );

    let remote_ip = "127.0.0.1";
    let remote_http_port = 9000;

    // TODO: Setup handling of stuff
    let client = Arc::new(hyper::Client::new());
    let client2 = Arc::clone(&client);
    ice_agent.on_candidate(Box::new(
        move |c: Option<Arc<dyn Candidate + Send + Sync>>| {
            let internal_client = Arc::clone(&client2);
            Box::pin(async move {
                if let Some(c) = c {
                    println!("posting remoteCandidate with {}", c.marshal());

                    let req = match Request::builder()
                        .method(Method::POST)
                        .uri(format!(
                            "http://{remote_ip}:{remote_http_port}/remoteCandidate"
                        )).body(Body::from(c.marshal()))
                    {
                        Ok(req) => req,
                        Err(err) => {
                            println!("{err}");
                            return;
                        }
                    };
                    let resp = match internal_client.request(req).await {
                        Ok(resp) => resp,
                        Err(err) => {
                            println!("{err}");
                            return;
                        }
                    };
                    println!("Response from remoteCandidate: {}", resp.status());
                }
            })
    },));

    ice_agent.on_connection_state_change(Box::new(move |c: ConnectionState| {
        println!("ICE Connection State has changed: {c}");
        if c == ConnectionState::Failed {
            // let _ = ice_done_tx.try_send(());
            println!("Should try to send here");
        }
        Box::pin(async move {})
    }));

    let (local_ufrag, local_pwd) = ice_agent.get_local_user_credentials().await;
    println!("posting remoteAuth with {local_ufrag}:{local_pwd}");
    
    let req = match Request::builder()
            .method(Method::POST)
            .uri(format!("http://{remote_ip}:{remote_http_port}/remoteAuth"))
            .body(Body::from(format!("{local_ufrag}:{local_pwd}")))
        {
            Ok(req) => req,
            Err(err) => return Err(Error::new(err)),
        };
        let resp = match client.request(req).await {
            Ok(resp) => resp,
            Err(err) => return Err(Error::new(err)),
        };
        println!("Response from remoteAuth: {}", resp.status());


        
    // Start the gathering process
    ice_agent.gather_candidates()?;

    Ok(())
}


// HTTP Listener to get ICE Credentials/Candidate from remote Peer
// async fn remote_handler(req: Request<Body>) -> Result<Response<Body>, hyper::Error> {
    //println!("received {:?}", req);
    // match (req.method(), req.uri().path()) {
    //     (&Method::POST, "/remoteAuth") => {
    //         let full_body =
    //             match std::str::from_utf8(&hyper::body::to_bytes(req.into_body()).await?) {
    //                 Ok(s) => s.to_owned(),
    //                 Err(err) => panic!("{}", err),
    //             };
    //         let tx = REMOTE_AUTH_CHANNEL.0.lock().await;
    //         //println!("body: {:?}", full_body);
    //         let _ = tx.send(full_body).await;

    //         let mut response = Response::new(Body::empty());
    //         *response.status_mut() = StatusCode::OK;
    //         Ok(response)
    //     }

    //     (&Method::POST, "/remoteCandidate") => {
    //         let full_body =
    //             match std::str::from_utf8(&hyper::body::to_bytes(req.into_body()).await?) {
    //                 Ok(s) => s.to_owned(),
    //                 Err(err) => panic!("{}", err),
    //             };
    //         let tx = REMOTE_CAND_CHANNEL.0.lock().await;
    //         //println!("body: {:?}", full_body);
    //         let _ = tx.send(full_body).await;

    //         let mut response = Response::new(Body::empty());
    //         *response.status_mut() = StatusCode::OK;
    //         Ok(response)
    //     }

    //     // Return the 404 Not Found for other routes.
    //     _ => {
    //         let mut not_found = Response::default();
    //         *not_found.status_mut() = StatusCode::NOT_FOUND;
    //         Ok(not_found)
    //     }
    // }
// }

fn start_sdp_server(addr: String, port: String) {
    println!("Listening on http://{addr}:{port}");
    // FIXME: Fix the handling of values and other stuff
    // tokio::spawn(async move {
    //     let addr = (addr, port).into();
    //     let service = make_service_fn(|_| async { 
    //         Ok::<_, hyper::Error>(service_fn(remote_handler)) 
    //     });
    //     let server = Server::bind(&addr).serve(service);
    //     tokio::select! {
    //         _ = done_http_server.changed() => {
    //             println!("receive cancel http server!");
    //         }
    //         result = server => {
    //             // Run this server for... forever!
    //             if let Err(e) = result {
    //                 eprintln!("server error: {e}");
    //             }
    //             println!("exit http server!");
    //         }
    //     };
    // });
}

#[tokio::main]
async fn main() {
    let mut buf = [0; 65535];
    let mut out = [0; MAX_DATAGRAM_SIZE];

    let mut args = std::env::args();

    let cmd = &args.next().unwrap();

    if args.len() != 0 {
        println!("Usage: {cmd}");
        println!("\nSee tools/apps/ for more complete implementations.");
        return;
    }
    // Create the UDP listening socket, and register it with the event loop.
    // TODO: Add argument to specify where to bind the socket to
    let mut socket =
        tokio::net::UdpSocket::bind(SocketAddrV4::new(Ipv4Addr::new(127,0,0,1), 4433)).await.unwrap();

    // Create the configuration for the QUIC connections.
    let mut config = quiche::Config::new(quiche::PROTOCOL_VERSION).unwrap();
    configure_quic(&mut config);

    let expected_server_str = "stun:stun.l.google.com:19302";
    let peer_config = RTCConfiguration {
        ice_servers: vec![RTCIceServer {
            urls: vec![expected_server_str.to_owned()],
            ..Default::default()
        }],
        ..Default::default()
    };
    
    // Create a MediaEngine object to configure the supported codec
    let mut m = MediaEngine::default();
    m.register_default_codecs().unwrap();

    let mut registry = Registry::new();

    // Use the default set of Interceptors
    registry = register_default_interceptors(registry, &mut m).unwrap();

    // Create the API object with the MediaEngine
    let api = APIBuilder::new()
        .with_media_engine(m)
        .with_interceptor_registry(registry)
        .build();

    // Create a new RTCPeerConnection
    let peer_connection = Arc::new(api.new_peer_connection(peer_config).await.unwrap());

    // QUIC stuff
    let rng = SystemRandom::new();
    let conn_id_seed = ring::hmac::Key::generate(ring::hmac::HMAC_SHA256, &rng).unwrap();

    let mut clients = ClientMap::new();
    let local_addr = socket.local_addr().unwrap();

    loop {
        // Find the shorter timeout from all the active connections.
        //
        // TODO: use event loop that properly supports timers
        // let timeout = clients.values().filter_map(|c| c.conn.timeout()).min();

        // poll.poll(&mut events, timeout).unwrap();

        // TODO: Multiplex the peer connection and quic on one socket
        // TODO: Handling of the external signalling of data via http in ice
        

        // Read incoming UDP packets from the socket and feed them to quiche,
        // until there are no more packets to read.
        'read: loop {
            // If the event loop reported no events, it means that the timeout
            // has expired, so handle it without attempting to read packets. We
            // will then proceed with the send loop.
            // if events.is_empty() {
            //     debug!("timed out");

            //     clients.values_mut().for_each(|c| c.conn.on_timeout());

            //     break 'read;
            // }

            let (len, from) = match socket.recv_from(&mut buf).await {
                Ok(v) => v,

                Err(e) => {
                    // There are no more UDP packets to read, so end the read
                    // loop.
                    if e.kind() == std::io::ErrorKind::WouldBlock {
                        debug!("recv() would block");
                        break 'read;
                    }

                    panic!("recv() failed: {:?}", e);
                },
            };

            debug!("got {} bytes", len);

            let pkt_buf = &mut buf[..len];

            if !is_packet_quic(&mut octets::Octets::with_slice(pkt_buf)) {
                info!("Handling ICE packet");
                // handle_ice(&mut octets::Octets::with_slice(pkt_buf)).await;

                break 'read;
            }

            // Parse the QUIC packet's header.
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

            trace!("got packet {:?}", hdr);

            let conn_id = ring::hmac::sign(&conn_id_seed, &hdr.dcid);
            let conn_id = &conn_id.as_ref()[..quiche::MAX_CONN_ID_LEN];
            let conn_id = conn_id.to_vec().into();

            // Lookup a connection based on the packet's connection ID. If there
            // is no connection matching, create a new one.
            let client = if !clients.contains_key(&hdr.dcid) &&
                !clients.contains_key(&conn_id)
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

                    if let Err(e) = socket.send_to(out, from).await {
                        if e.kind() == std::io::ErrorKind::WouldBlock {
                            debug!("send() would block");
                            break;
                        }

                        panic!("send() failed: {:?}", e);
                    }
                    continue 'read;
                }

                let mut scid = [0; quiche::MAX_CONN_ID_LEN];
                scid.copy_from_slice(&conn_id);

                let scid = quiche::ConnectionId::from_ref(&scid);

                // Token is always present in Initial packets.
                let token = hdr.token.as_ref().unwrap();

                // Do stateless retry if the client didn't send a token.
                if token.is_empty() {
                    warn!("Doing stateless retry");

                    let new_token = mint_token(&hdr, &from);

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

                    if let Err(e) = socket.send_to(out, from).await {
                        if e.kind() == std::io::ErrorKind::WouldBlock {
                            debug!("send() would block");
                            break;
                        }

                        panic!("send() failed: {:?}", e);
                    }
                    continue 'read;
                }

                let odcid = validate_token(&from, token);

                // The token was not valid, meaning the retry failed, so
                // drop the packet.
                if odcid.is_none() {
                    error!("Invalid address validation token");
                    continue 'read;
                }

                if scid.len() != hdr.dcid.len() {
                    error!("Invalid destination connection ID");
                    continue 'read;
                }

                // Reuse the source connection ID we sent in the Retry packet,
                // instead of changing it again.
                let scid = hdr.dcid.clone();

                debug!("New connection: dcid={:?} scid={:?}", hdr.dcid, scid);

                let conn = quiche::accept(
                    &scid,
                    odcid.as_ref(),
                    local_addr,
                    from,
                    &mut config,
                )
                .unwrap();

                let client = Client {
                    conn,
                    partial_responses: HashMap::new(),
                };

                clients.insert(scid.clone(), client);

                clients.get_mut(&scid).unwrap()
            } else {
                match clients.get_mut(&hdr.dcid) {
                    Some(v) => v,

                    None => clients.get_mut(&conn_id).unwrap(),
                }
            };

            let recv_info = quiche::RecvInfo {
                to: socket.local_addr().unwrap(),
                from,
            };

            // Process potentially coalesced packets.
            let read = match client.conn.recv(pkt_buf, recv_info) {
                Ok(v) => v,

                Err(e) => {
                    error!("{} recv failed: {:?}", client.conn.trace_id(), e);
                    continue 'read;
                },
            };

            debug!("{} processed {} bytes", client.conn.trace_id(), read);

            if client.conn.is_in_early_data() || client.conn.is_established() {
                // Handle writable streams.
                for stream_id in client.conn.writable() {
                    handle_writable(client, stream_id);
                }

                // Process all readable streams.
                for s in client.conn.readable() {
                    while let Ok((read, fin)) =
                        client.conn.stream_recv(s, &mut buf)
                    {
                        debug!(
                            "{} received {} bytes",
                            client.conn.trace_id(),
                            read
                        );

                        let stream_buf = &buf[..read];

                        debug!(
                            "{} stream {} has {} bytes (fin? {})",
                            client.conn.trace_id(),
                            s,
                            stream_buf.len(),
                            fin
                        );

                        handle_stream(client, s, stream_buf, "examples/root");
                    }
                }
            }
        }

        // Generate outgoing QUIC packets for all active connections and send
        // them on the UDP socket, until quiche reports that there are no more
        // packets to be sent.
        for client in clients.values_mut() {
            loop {
                let (write, send_info) = match client.conn.send(&mut out) {
                    Ok(v) => v,

                    Err(quiche::Error::Done) => {
                        debug!("{} done writing", client.conn.trace_id());
                        break;
                    },

                    Err(e) => {
                        error!("{} send failed: {:?}", client.conn.trace_id(), e);

                        client.conn.close(false, 0x1, b"fail").ok();
                        break;
                    },
                };

                if let Err(e) = socket.send_to(&out[..write], send_info.to).await {
                    if e.kind() == std::io::ErrorKind::WouldBlock {
                        debug!("send() would block");
                        break;
                    }

                    panic!("send() failed: {:?}", e);
                }

                debug!("{} written {} bytes", client.conn.trace_id(), write);
            }
        }

        // Garbage collect closed connections.
        clients.retain(|_, ref mut c| {
            debug!("Collecting garbage");

            if c.conn.is_closed() {
                info!(
                    "{} connection collected {:?}",
                    c.conn.trace_id(),
                    c.conn.stats()
                );
            }

            !c.conn.is_closed()
        });
    }
}

/// Generate a stateless retry token.
///
/// The token includes the static string `"quiche"` followed by the IP address
/// of the client and by the original destination connection ID generated by the
/// client.
///
/// Note that this function is only an example and doesn't do any cryptographic
/// authenticate of the token. *It should not be used in production system*.
fn mint_token(hdr: &quiche::Header, src: &net::SocketAddr) -> Vec<u8> {
    let mut token = Vec::new();

    token.extend_from_slice(b"quiche");

    let addr = match src.ip() {
        std::net::IpAddr::V4(a) => a.octets().to_vec(),
        std::net::IpAddr::V6(a) => a.octets().to_vec(),
    };

    token.extend_from_slice(&addr);
    token.extend_from_slice(&hdr.dcid);

    token
}

/// Validates a stateless retry token.
///
/// This checks that the ticket includes the `"quiche"` static string, and that
/// the client IP address matches the address stored in the ticket.
///
/// Note that this function is only an example and doesn't do any cryptographic
/// authenticate of the token. *It should not be used in production system*.
fn validate_token<'a>(
    src: &net::SocketAddr, token: &'a [u8],
) -> Option<quiche::ConnectionId<'a>> {
    if token.len() < 6 {
        return None;
    }

    if &token[..6] != b"quiche" {
        return None;
    }

    let token = &token[6..];

    let addr = match src.ip() {
        std::net::IpAddr::V4(a) => a.octets().to_vec(),
        std::net::IpAddr::V6(a) => a.octets().to_vec(),
    };

    if token.len() < addr.len() || &token[..addr.len()] != addr.as_slice() {
        return None;
    }

    Some(quiche::ConnectionId::from_ref(&token[addr.len()..]))
}

/// Handles incoming HTTP/0.9 requests.
fn handle_stream(client: &mut Client, stream_id: u64, buf: &[u8], root: &str) {
    let conn = &mut client.conn;

    if buf.len() > 4 && &buf[..4] == b"GET " {
        let uri = &buf[4..buf.len()];
        let uri = String::from_utf8(uri.to_vec()).unwrap();
        let uri = String::from(uri.lines().next().unwrap());
        let uri = std::path::Path::new(&uri);
        let mut path = std::path::PathBuf::from(root);

        for c in uri.components() {
            if let std::path::Component::Normal(v) = c {
                path.push(v)
            }
        }

        info!(
            "{} got GET request for {:?} on stream {}",
            conn.trace_id(),
            path,
            stream_id
        );

        let body = std::fs::read(path.as_path())
            .unwrap_or_else(|_| b"Not Found!\r\n".to_vec());

        info!(
            "{} sending response of size {} on stream {}",
            conn.trace_id(),
            body.len(),
            stream_id
        );

        let written = match conn.stream_send(stream_id, &body, true) {
            Ok(v) => v,

            Err(quiche::Error::Done) => 0,

            Err(e) => {
                error!("{} stream send failed {:?}", conn.trace_id(), e);
                return;
            },
        };

        if written < body.len() {
            let response = PartialResponse { body, written };
            client.partial_responses.insert(stream_id, response);
        }
    }
}

/// Handles newly writable streams.
fn handle_writable(client: &mut Client, stream_id: u64) {
    let conn = &mut client.conn;

    debug!("{} stream {} is writable", conn.trace_id(), stream_id);

    if !client.partial_responses.contains_key(&stream_id) {
        return;
    }

    let resp = client.partial_responses.get_mut(&stream_id).unwrap();
    let body = &resp.body[resp.written..];

    let written = match conn.stream_send(stream_id, body, true) {
        Ok(v) => v,

        Err(quiche::Error::Done) => 0,

        Err(e) => {
            client.partial_responses.remove(&stream_id);

            error!("{} stream send failed {:?}", conn.trace_id(), e);
            return;
        },
    };

    resp.written += written;

    if resp.written == resp.body.len() {
        client.partial_responses.remove(&stream_id);
    }
}
