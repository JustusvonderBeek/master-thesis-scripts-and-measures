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

use std::net::{IpAddr, Ipv4Addr, SocketAddr, SocketAddrV4};
use std::os::fd::{AsRawFd, FromRawFd};
use std::sync::Arc;
use std::thread;
use std::sync::atomic::AtomicBool;
use std::io;
use std::process::ExitCode;
use std::time::{Duration, Instant};
use rand::{thread_rng, Rng};
use async_trait::async_trait;

use anyhow::Result;
use quiche::{scheduler, PathStatus};
use tokio::net::UdpSocket;
use tokio::sync::{mpsc, Mutex};
use webrtc_ice::state::ConnectionState;
use webrtc_ice::candidate::Candidate;
use webrtc_ice::network_type::NetworkType;
use webrtc_ice::udp_network::UDPNetwork;
use webrtc_ice::udp_mux::{UDPMuxParams, UDPMuxDefault};
use webrtc_ice::agent::{agent_config::AgentConfig, Agent};
use webrtc_ice::candidate::candidate_base::unmarshal_candidate;
use webrtc::util::Conn;

use hyper::service::{make_service_fn, service_fn};
use hyper::{Body, Method, Request, Client, Response, Server, StatusCode};

use ring::rand::*;

mod ice;
mod multiplexer;

// Parsing the command line
use clap::{App, Arg};

// Quicheperf stuff
use quicheperf::quicheperf_server;
use quicheperf::server::Server as QuicheperfServer;
use quicheperf::client::Client as QuicheperfClient;
use quicheperf::common;
use quicheperf::protocol::TestConfig;
use quicheperf::quicheperf_client;

const QUICHEPERF_ALPN: [&[u8]; 2] = [b"quicheperf", b"quicheperf-00"];
const MAX_DATAGRAM_SIZE: usize = 1350;


#[derive(Clone)]
pub struct ArcConnStruct {
    socket: Arc<UdpSocket>,
}

#[async_trait]
impl Conn for ArcConnStruct {
    async fn connect(&self, addr: SocketAddr) -> webrtc::util::Result<()> {
        // Delegate the method call to the wrapped socket
        self.socket.connect(addr).await.map_err(|err| err.into())
    }

    async fn recv(&self, buf: &mut [u8]) -> webrtc::util::Result<usize> {
        // Delegate the method call to the wrapped socket
        self.socket.recv(buf).await.map_err(|err| err.into())
    }

    async fn recv_from(&self, buf: &mut [u8]) -> webrtc::util::Result<(usize, SocketAddr)> {
        // Delegate the method call to the wrapped socket
        self.socket.recv_from(buf).await.map_err(|err| err.into())
    }

    async fn send(&self, buf: &[u8]) -> webrtc::util::Result<usize> {
        // Delegate the method call to the wrapped socket
        self.socket.send(buf).await.map_err(|err| err.into())
    }

    async fn send_to(&self, buf: &[u8], target: SocketAddr) -> webrtc::util::Result<usize> {
        // Delegate the method call to the wrapped socket
        self.socket.send_to(buf, target).await.map_err(|err| err.into())
    }

    fn local_addr(&self) -> webrtc::util::Result<SocketAddr> {
        // Delegate the method call to the wrapped socket
        self.socket.local_addr().map_err(|err| err.into())
    }

    fn remote_addr(&self) -> Option<SocketAddr> {
        // Delegate the method call to the wrapped socket
        self.socket.remote_addr()
    }

    async fn close(&self) -> webrtc::util::Result<()> {
        // Delegate the method call to the wrapped socket
        self.socket.close().await
    }
}

type SenderType = Arc<Mutex<mpsc::Sender<String>>>;
type ReceiverType = Arc<Mutex<mpsc::Receiver<String>>>;


lazy_static! {
    // ErrUnknownType indicates an error with Unknown info.
    static ref REMOTE_AUTH_CHANNEL: (SenderType, ReceiverType ) = {
        let (tx, rx) = mpsc::channel::<String>(3);
        (Arc::new(Mutex::new(tx)), Arc::new(Mutex::new(rx)))
    };

    static ref REMOTE_CAND_CHANNEL: (SenderType, ReceiverType) = {
        let (tx, rx) = mpsc::channel::<String>(10);
        (Arc::new(Mutex::new(tx)), Arc::new(Mutex::new(rx)))
    };
}

// HTTP Listener to get ICE Credentials/Candidate from remote Peer
async fn remote_handler(req: Request<Body>) -> Result<Response<Body>, hyper::Error> {
    //println!("received {:?}", req);
    match (req.method(), req.uri().path()) {
        (&Method::POST, "/remoteAuth") => {
            let full_body =
                match std::str::from_utf8(&hyper::body::to_bytes(req.into_body()).await?) {
                    Ok(s) => s.to_owned(),
                    Err(err) => panic!("{}", err),
                };
            let tx = REMOTE_AUTH_CHANNEL.0.lock().await;
            //println!("body: {:?}", full_body);
            let _ = tx.send(full_body).await;

            let mut response = Response::new(Body::empty());
            *response.status_mut() = StatusCode::OK;
            Ok(response)
        }

        (&Method::POST, "/remoteCandidate") => {
            let full_body =
                match std::str::from_utf8(&hyper::body::to_bytes(req.into_body()).await?) {
                    Ok(s) => s.to_owned(),
                    Err(err) => panic!("{}", err),
                };
            let tx = REMOTE_CAND_CHANNEL.0.lock().await;
            //println!("body: {:?}", full_body);
            let _ = tx.send(full_body).await;

            let mut response = Response::new(Body::empty());
            *response.status_mut() = StatusCode::OK;
            Ok(response)
        }

        // Return the 404 Not Found for other routes.
        _ => {
            let mut not_found = Response::default();
            *not_found.status_mut() = StatusCode::NOT_FOUND;
            Ok(not_found)
        }
    }
}

fn make_quiche_config() -> Result<quiche::Config, ExitCode> {
    let mut config = match quiche::Config::new(quiche::PROTOCOL_VERSION) {
        Ok(v) => v,
        Err(e) => {
            eprintln!("Could not create quiche config: {}", e);
            return Err(ExitCode::FAILURE);
        }
    };

    config
        .set_application_protos(&QUICHEPERF_ALPN)
        .unwrap();

    config.set_max_idle_timeout(30_000); // in ms
    config.set_max_recv_udp_payload_size(MAX_DATAGRAM_SIZE);
    config.set_max_send_udp_payload_size(MAX_DATAGRAM_SIZE);
    config.set_initial_max_data(25165824);

    config.set_initial_max_stream_data_bidi_local(1000000);
    config.set_initial_max_stream_data_bidi_remote(1000000);
    config.set_initial_max_stream_data_uni(1000000);

    config.set_initial_max_streams_bidi(100);
    config.set_initial_max_streams_uni(100);
    config.set_ack_delay_exponent(3); // quiche default
    config.set_max_ack_delay(25); // quiche default
    config.set_active_connection_id_limit(5);
    config.set_disable_active_migration(false);

    // get_bool(--mp) -> is the flag present?
    let implicitely_mp = !false && 2 > 1;
    let explicitly_mp = true;
    if implicitely_mp || explicitly_mp {
        config.set_multipath(true);
        info!("Enabled multipath");
    } else {
        config.set_multipath(false);
    }

    if let Ok(cwnd) = Err(()) {
        config.set_cc_algorithm_name("constant").unwrap();
        config.set_constant_cwnd(cwnd);
        info!("Set constant cwnd={}B", cwnd);
    } else if let Err(e) = config.set_cc_algorithm_name("cubic") {
        eprintln!("Could not set CCA {}: {}", "cubic", e);
        return Err(ExitCode::FAILURE);
    };

    config.enable_hystart(true);
    config.enable_pacing(true);

    config.enable_dgram(false, 1000, 1000);

    config.set_max_connection_window(25_165_824);
    config.set_max_stream_window(16_777_216);

    // config.set_stateless_reset_token
    // config.set_disable_dcid_reuse

    config.flow_control_config.initial_connection_window = 49152;
    config.flow_control_config.initial_stream_window = 32768;
    config.flow_control_config.window_update_threshold = 50;
    config.flow_control_config.autotune_increase_factor = 2;
    config.flow_control_config.reactive_rtt_trigger_factor = 2;

    if let Err(e) = config.set_fc_autotune_strategy("reactive") {
        eprintln!(
            "Error setting flow control autotune strategy {}: {}",
            "reactive", e
        );
        return Err(ExitCode::FAILURE);
    }

    Ok(config)
}


#[tokio::main]
async fn main() {

    // Parsing the command line
    let app = App::new("ICE & QUIC Multiplex")
        .version("0.1")
        .about("An example implementation to multiplex ICE and QUIC on a single socket in rust")
        .arg(
            Arg::with_name("remote")
                .takes_value(true)
                .long("remote")
                .short('r')
                .default_value("127.0.0.1")
                .help("Remote endpoint ip to send the ICE candidates to")
        )
        .arg(
            Arg::with_name("controlling")
                .takes_value(false)
                .long("controlling")
                .short('c')
                .help("If the program is controlled or controlling")
        )
        .arg(
            Arg::with_name("local-quic-address")
                .takes_value(true)
                .long("local")
                .short('l')
                .default_value("127.0.0.1")
                .help("The address the local quic socket should bind to")
        )
        ;

    // Extracting the given arguments
    let matches = app.clone().get_matches();

    // Create the UDP listening socket, and register it with the event loop.
    // FIXME: Add argument to specify where to bind the socket to

    let remote_endpoint = Arc::new(matches.value_of("remote").expect("Remote endpoint not given but required!"));
    let local_endpoint = matches.value_of("local-quic-address").expect("Expected local address but non was given!");
    // Controlling in this case also means server (quic related)
    let is_controlling = matches.is_present("controlling");
    let (local_http_port, remote_http_port) = if is_controlling {
        (9000, 9001)
    } else {
        (9001, 9000)
    };
    let port = if is_controlling { 4000 } else { 4001 };
    let remote_quic_port = if is_controlling { 4001 } else { 4000 };
    // Let the computer decide which socket and IP to use
    // TODO: Instead of letting each application poll, we need to poll in one place and the multiplex
    // depending on the packet. Now, the ice thingy doesn't get the ice packets anymore
    let udp_socket = UdpSocket::bind((local_endpoint, port)).await.unwrap();
    let udp_socket2 = Arc::new(udp_socket);
    let udp_socket3 = Arc::clone(&udp_socket2);
    let udp_socket_struct = ArcConnStruct {
        socket: udp_socket2,
    };

    let udp_mux = UDPMuxDefault::new(UDPMuxParams::new(udp_socket_struct));
    let udp_network = UDPNetwork::Muxed(udp_mux);

    // Manually handling the ice agent
    let ice_agent = Arc::new(Agent::new(AgentConfig {
        network_types: vec![NetworkType::Udp4],
        udp_network,
        ..Default::default()
    }).await.unwrap());

    // ------------------------------------
    // Configure the out-of-band signalling of ice
    // ------------------------------------

    // Step 1: Start a local http server that can receive ice candidates out-of-band
    // FIXME: This should later probably be replaced with a TURN server in case we cannot create a direct connection
    println!("Listening on http://{local_endpoint}:{local_http_port}");
    // let mut done_http_server = done_rx.clone();
    tokio::spawn(async move {
        let addr = ([0, 0, 0, 0], local_http_port).into();
        let service = make_service_fn(|_| async { Ok::<_, hyper::Error>(service_fn(remote_handler)) });
        let server = Server::bind(&addr).serve(service);
        tokio::select! {
            // _ = done_http_server.changed() => {
            //     println!("receive cancel http server!");
            // }
            result = server => {
                // Run this server for... forever!
                if let Err(e) = result {
                    eprintln!("server error: {e}");
                }
                println!("exit http server!");
            }
        };
    });

    if is_controlling {
        println!("Local Agent is controlling");
    } else {
        println!("Local Agent is controlled");
    };
    println!("Press 'Enter' when both processes have started");
    let mut input = String::new();
    let _ = io::stdin().read_line(&mut input).unwrap();

    // Step 2: For each candidate our ice agent finds, send out-of-band to the other end
    let client = Arc::new(Client::new());

    // When we have gathered a new ICE Candidate send it to the remote peer
    // IMPORTANT: This connection is the out of band, it is NOT the multiplexed connection
    let remote_endpoint2 = remote_endpoint.to_string(); // Copy the string to fix the ownership issues
    let remote_endpoint4 = Arc::clone(&remote_endpoint);
    let client2 = Arc::clone(&client);
    ice_agent.on_candidate(Box::new(
        move |c: Option<Arc<dyn Candidate + Send + Sync>>| {
            let client3 = Arc::clone(&client2);
            let remote_endpoint3 = remote_endpoint2.clone();
            Box::pin(async move {
                if let Some(c) = c {
                    println!("posting remoteCandidate with {}", c.marshal());

                    let req = match Request::builder()
                        .method(Method::POST)
                        .uri(format!(
                            "http://{remote_endpoint3}:{remote_http_port}/remoteCandidate"
                        ))
                        .body(Body::from(c.marshal()))
                    {
                        Ok(req) => req,
                        Err(err) => {
                            println!("{err}");
                            return;
                        }
                    };
                    let resp = match client3.request(req).await {
                        Ok(resp) => resp,
                        Err(err) => {
                            println!("{err}");
                            return;
                        }
                    };
                    println!("Response from remoteCandidate: {}", resp.status());
                }
            })
        },
    ));

    ice_agent.on_connection_state_change(Box::new(move |c: ConnectionState| {
        println!("ICE Connection State has changed: {c}");
        if c == ConnectionState::Failed {
            // let _ = ice_done_tx.try_send(());
            println!("Connection state failed. You can end the program...");
        }
        Box::pin(async move {})
    }));

    // Get the local auth details and send to remote peer
    let (local_ufrag, local_pwd) = ice_agent.get_local_user_credentials().await;
    println!("posting remoteAuth with {local_ufrag}:{local_pwd}");
    let req = match Request::builder()
        .method(Method::POST)
        .uri(format!("http://{remote_endpoint4}:{remote_http_port}/remoteAuth"))
        .body(Body::from(format!("{local_ufrag}:{local_pwd}")))
    {
        Ok(req) => req,
        Err(err) => return error!("Failed to create request"),
    };
    let resp = match client.request(req).await {
        Ok(resp) => resp,
        Err(err) => return error!("Failed to perform request"),
    };
    println!("Response from remoteAuth: {}", resp.status());

    let (remote_ufrag, remote_pwd) = {
        let mut rx = REMOTE_AUTH_CHANNEL.1.lock().await;
        if let Some(s) = rx.recv().await {
            println!("received: {s}");
            let fields: Vec<String> = s.split(':').map(|s| s.to_string()).collect();
            (fields[0].clone(), fields[1].clone())
        } else {
            panic!("rx.recv() empty");
        }
    };
    println!("remote_ufrag: {remote_ufrag}, remote_pwd: {remote_pwd}");

    let ice_agent2 = Arc::clone(&ice_agent);
    // let mut done_cand = done_rx.clone();
    tokio::spawn(async move {
        let mut rx = REMOTE_CAND_CHANNEL.1.lock().await;
        loop {
            tokio::select! {
                    // _ = done_cand.changed() => {
                    // println!("receive cancel remote cand!");
                    // break;
                // }
                result = rx.recv() => {
                    if let Some(s) = result {
                        if let Ok(c) = unmarshal_candidate(&s) {
                            println!("add_remote_candidate: {c}");
                            let c: Arc<dyn Candidate + Send + Sync> = Arc::new(c);
                            let _ = ice_agent2.add_remote_candidate(&c);
                        }else{
                            println!("unmarshal_candidate error!");
                            break;
                        }
                    }else{
                        println!("REMOTE_CAND_CHANNEL done!");
                        break;
                    }
                }
            };
        }
    });

    ice_agent.gather_candidates().unwrap();
    println!("Connecting...");
    
    let (_cancel_tx, cancel_rx) = mpsc::channel(1);
    let conn: Arc<dyn Conn + Send + Sync> = if is_controlling {
        ice_agent.dial(cancel_rx, remote_ufrag, remote_pwd).await.unwrap()
    } else {
        ice_agent
            .accept(cancel_rx, remote_ufrag, remote_pwd)
            .await.unwrap()
    };

    // Send messages in a loop to the remote peer
    let conn_tx = Arc::clone(&conn);
    // let mut done_send = done_rx.clone();
    tokio::spawn(async move {
        const RANDOM_STRING: &[u8] = b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
        loop {
            tokio::time::sleep(Duration::from_secs(3)).await;

            let val: String = (0..15)
                .map(|_| {
                    let idx = thread_rng().gen_range(0..RANDOM_STRING.len());
                    RANDOM_STRING[idx] as char
                })
                .collect();

            tokio::select! {
                //  _ = done_send.changed() => {
                //     println!("receive cancel ice send!");
                //     break;
                // }
                result = conn_tx.send(val.as_bytes()) => {
                    if let Err(err) = result {
                        eprintln!("conn_tx send error: {err}");
                        break;
                    }else{
                        println!("Sent: '{val}'");
                    }
                }
            };
        }
    });

    // ------------------------------------
    // at this point ice is sending happily data from the server to the client.
    // Now: Starting the quiche loop and using the ice data to build a connection
    // on top of the existing udp_socket
    // ------------------------------------

    // this is the way we can use the socket to send more stuff
    // udp_socket3.as_ref().send(&buf).await.unwrap();

    // Using the quicheperf library to send and receive code
    let mut buf = [0; 65535];
    let mut out = [0; MAX_DATAGRAM_SIZE];

    // Create the configuration for the QUIC connections.
    let mut config = match make_quiche_config() {
        Ok(v) => v,
        Err(_) => {
            panic!("Failed to create QUICHEPERF config!");
        }
    };

    // QUIC stuff
    let rng = SystemRandom::new();
    let conn_id_seed = ring::hmac::Key::generate(ring::hmac::HMAC_SHA256, &rng).unwrap();

    // Let ICE do it's job and then proceed to perform some quic
    thread::sleep(Duration::from_secs(5));

    // let mut clients = ClientMap::new();
    // For now hardcode the local address
    let local_addr = udp_socket3.local_addr().unwrap();
    let mut local_addrs = Vec::new();
    local_addrs.push(local_addr);

    let scheduler: Box<dyn scheduler::MultipathScheduler> = Box::new(scheduler::MinRTT::new());

    let terminate = Arc::new(AtomicBool::new(false));
    let t = terminate.clone();
    
    // Convert the tokio::net::UdpSocket into a mio::net::UdpSocket because thats the type quichperf is working with
    let raw_udp_fd = udp_socket3.as_raw_fd();
    let mio_udp_socket : mio::net::UdpSocket;
    unsafe {
        mio_udp_socket = mio::net::UdpSocket::from_raw_fd(raw_udp_fd);
    };
    // let mio_udp_socket_a = Arc::new(mio_udp_socket);
    // FIXME: This is not in the sense of the creator, I guess; implement some correct borrowing and transfer
    // of ownership into the quicheperf crate. Requires probably changes in the quicheperf crate
    let mut udp_socket_vec = Vec::new();
    udp_socket_vec.push(mio_udp_socket);

    match is_controlling {
        true => {
            // Server
            println!("Starting server...");
            if let Err(e) = config.load_cert_chain_from_pem_file("resources/cert.crt") {
                eprintln!("Error loading certificate from {:?}: {}", "resources/cert.crt", e);
                panic!("No cert found");
            };

            if let Err(e) = config.load_priv_key_from_pem_file("resources/cert.key") {
                eprintln!("Error loading private key from {:?}: {}", "resources/cert.key", e);
                panic!("No key found");
            };


            let (read, remote_addr) = match udp_socket3.recv_from(&mut buf).await {
                Ok(u) => u,
                Err(_) => panic!("Failed to read remote")
            };
            
            println!("Received from {remote_addr}");
            let server = match QuicheperfServer::new(local_addrs, None, config, scheduler, Some(udp_socket_vec)) {
                Ok(v) => v,
                Err(e) => {
                    eprintln!("Failed to set up server: {:?}", e);
                    panic!("Server creation failed!");
                }
            };

            let _ = match quicheperf_server(server, t) {
                Ok(_) => ExitCode::SUCCESS,
                Err(quicheperf::server::ServerError::FatalSocket(e)) => {
                    eprintln!("Fatal: {}", e);
                    ExitCode::FAILURE
                }
                Err(quicheperf::server::ServerError::Unexpected(e)) => {
                    eprintln!("Unexpected: {}", e);
                    ExitCode::FAILURE
                }
            };
        },
        false => {
            // Client
            println!("Starting client...");
            // FIXME: Fix the hardcoded parameters to allow for the same options as the quicheperf command line
            let mut peer_addrs = Vec::new();
            // TODO: Fix this hardcoded value later on
            // Use the remote address for now to connect to the correct remote endpoint
            let remote_ipv4 : Ipv4Addr = remote_endpoint.parse().unwrap();
            peer_addrs.push(SocketAddr::new(IpAddr::V4(remote_ipv4), remote_quic_port));

            // FIXME: Should be fine if empty, handling of paths etc. should be done by the ICE crate anyways
            let path_statuses = Vec::<(Duration, usize, PathStatus)>::new();

            let psu = match common::PathStatusUpdater::new(
                Instant::now(),
                local_addrs.clone(),
                peer_addrs.clone(),
                path_statuses,
            ) {
                Ok(v) => v,
                Err(e) => {
                    eprintln!("Path status updater: {}", e);
                    panic!("Failed to create PSU for client");
                }
            };

            let tc = TestConfig {
                local_addrs: local_addrs.iter().map(|s| s.to_string()).collect(),
                peer_addrs: peer_addrs.iter().map(|s| s.to_string()).collect(),
                password: None,
                client_sending: true,
                duration: Duration::from_secs(10),
                bitrate_target: None,
            };

            let client = QuicheperfClient::new(local_addrs, peer_addrs, config, Some(udp_socket_vec)).unwrap();

            let _ = match quicheperf_client(client, scheduler, tc, psu, terminate) {
                Err(quicheperf::client::ClientError::HandshakeFail) => ExitCode::FAILURE,

                Err(quicheperf::client::ClientError::IOFail(e)) | Err(quicheperf::client::ClientError::Other(e)) => {
                    eprintln!("{}", e);
                    ExitCode::FAILURE
                }

                Ok(_) => ExitCode::SUCCESS,
            };
        }
    }

}