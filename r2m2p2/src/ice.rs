// // Combines and extends the utilities from the webrtc-ice crate into single functions
// // which can be used on the same socket as the QUIC transfer

// // use std::io::Write;
// use std::net::SocketAddr;
// use std::str::FromStr;
// use std::sync::Arc;

// use anyhow::{Ok, Result};
// use tokio::time::Duration;
// use tokio::sync::Mutex;
// use octets::Octets;

// use webrtc::peer_connection::configuration::RTCConfiguration;
// use webrtc::peer_connection::peer_connection_state::RTCPeerConnectionState;
// use webrtc::ice_transport::ice_server::RTCIceServer;
// use webrtc::api::media_engine::MediaEngine;
// use webrtc::interceptor::registry::Registry;
// use webrtc::api::APIBuilder;
// use webrtc_ice::agent::agent_config::AgentConfig;
// use webrtc_ice::agent::{self, agent_config, Agent};
// use webrtc::ice_transport::ice_candidate::{RTCIceCandidate, RTCIceCandidateInit};
// use webrtc::peer_connection::sdp::session_description::RTCSessionDescription;
// use webrtc::peer_connection::{math_rand_alpha, RTCPeerConnection};
// use webrtc::api::interceptor_registry::register_default_interceptors;

// use hyper::service::{make_service_fn, service_fn};
// use hyper::{Body, Client, Method, Request, Response, Server, StatusCode};

// lazy_static! {
//     static ref PEER_CONNECTION_MUTEX: Arc<Mutex<Option<Arc<RTCPeerConnection>>>> =
//         Arc::new(Mutex::new(None));
//     static ref PENDING_CANDIDATES: Arc<Mutex<Vec<RTCIceCandidate>>> = Arc::new(Mutex::new(vec![]));
//     static ref ADDRESS: Arc<Mutex<String>> = Arc::new(Mutex::new(String::new()));
// }

// async fn signal_candidate(addr: &str, c: &RTCIceCandidate) -> Result<()> {
//     /*println!(
//         "signal_candidate Post candidate to {}",
//         format!("http://{}/candidate", addr)
//     );*/
//     let payload = c.to_json()?.candidate;
//     let req = match Request::builder()
//         .method(Method::POST)
//         .uri(format!("http://{addr}/candidate"))
//         .header("content-type", "application/json; charset=utf-8")
//         .body(Body::from(payload))
//     {
//         Ok(req) => req,
//         Err(err) => {
//             println!("{err}");
//             return Err(err.into());
//         }
//     };

//     let _resp = match Client::new().request(req).await {
//         Ok(resp) => resp,
//         Err(err) => {
//             println!("{err}");
//             return Err(err.into());
//         }
//     };
//     //println!("signal_candidate Response: {}", resp.status());

//     Ok(())
// }

// async fn remote_handler(req: Request<Body>) -> Result<Response<Body>, hyper::Error> {
//     let pc = {
//         let pcm = PEER_CONNECTION_MUTEX.lock().await;
//         pcm.clone().unwrap()
//     };
//     let addr = {
//         let addr = ADDRESS.lock().await;
//         addr.clone()
//     };

//     match (req.method(), req.uri().path()) {
//         // A HTTP handler that allows the other WebRTC-rs or Pion instance to send us ICE candidates
//         // This allows us to add ICE candidates faster, we don't have to wait for STUN or TURN
//         // candidates which may be slower
//         (&Method::POST, "/candidate") => {
//             //println!("remote_handler receive from /candidate");
//             let candidate =
//                 match std::str::from_utf8(&hyper::body::to_bytes(req.into_body()).await?) {
//                     Ok(s) => s.to_owned(),
//                     Err(err) => panic!("{}", err),
//                 };

//             if let Err(err) = pc
//                 .add_ice_candidate(RTCIceCandidateInit {
//                     candidate,
//                     ..Default::default()
//                 })
//                 .await
//             {
//                 panic!("{}", err);
//             }

//             let mut response = Response::new(Body::empty());
//             *response.status_mut() = StatusCode::OK;
//             Ok(response)
//         }

//         // A HTTP handler that processes a SessionDescription given to us from the other WebRTC-rs or Pion process
//         (&Method::POST, "/sdp") => {
//             //println!("remote_handler receive from /sdp");
//             let sdp_str = match std::str::from_utf8(&hyper::body::to_bytes(req.into_body()).await?)
//             {
//                 Ok(s) => s.to_owned(),
//                 Err(err) => panic!("{}", err),
//             };
//             let sdp = match serde_json::from_str::<RTCSessionDescription>(&sdp_str) {
//                 Ok(s) => s,
//                 Err(err) => panic!("{}", err),
//             };

//             if let Err(err) = pc.set_remote_description(sdp).await {
//                 panic!("{}", err);
//             }

//             {
//                 let cs = PENDING_CANDIDATES.lock().await;
//                 for c in &*cs {
//                     if let Err(err) = signal_candidate(&addr, c).await {
//                         panic!("{}", err);
//                     }
//                 }
//             }

//             let mut response = Response::new(Body::empty());
//             *response.status_mut() = StatusCode::OK;
//             Ok(response)
//         }
//         // Return the 404 Not Found for other routes.
//         _ => {
//             let mut not_found = Response::default();
//             *not_found.status_mut() = StatusCode::NOT_FOUND;
//             Ok(not_found)
//         }
//     }
// }

// pub async fn create_ice_setup() -> Result<()> {
//     // Prepare the configuration
//     let config = RTCConfiguration {
//         ice_servers: vec![RTCIceServer {
//             urls: vec!["stun:stun.l.google.com:19302".to_owned()],
//             ..Default::default()
//         }],
//         ..Default::default()
//     };

//     // Create a MediaEngine object to configure the supported codec
//     let mut m = MediaEngine::default();
//     m.register_default_codecs()?;

//     let mut registry = Registry::new();

//     // Use the default set of Interceptors
//     registry = register_default_interceptors(registry, &mut m)?;

//     // Create the API object with the MediaEngine
//     let api = APIBuilder::new()
//         .with_media_engine(m)
//         .with_interceptor_registry(registry)
//         .build();

//     // Create a new RTCPeerConnection
//     let peer_connection = Arc::new(api.new_peer_connection(config).await?);

//     let answer_addr = "127.0.0.1:60000";
//     let offer_addr = "127.0.0.1:50000";

//     // When an ICE candidate is available send to the other Pion instance
//     // the other Pion instance will add this candidate by calling AddICECandidate
//     let pc = Arc::downgrade(&peer_connection);
//     let pending_candidates2 = Arc::clone(&PENDING_CANDIDATES);
//     let addr2 = answer_addr.clone();
//     peer_connection.on_ice_candidate(Box::new(move |c: Option<RTCIceCandidate>| {
//         //println!("on_ice_candidate {:?}", c);

//         let pc2 = pc.clone();
//         let pending_candidates3 = Arc::clone(&pending_candidates2);
//         let addr3 = addr2.clone();
//         Box::pin(async move {
//             if let Some(c) = c {
//                 if let Some(pc) = pc2.upgrade() {
//                     let desc = pc.remote_description().await;
//                     if desc.is_none() {
//                         let mut cs = pending_candidates3.lock().await;
//                         cs.push(c);
//                     } else if let Err(err) = signal_candidate(&addr3, &c).await {
//                         panic!("{}", err);
//                     }
//                 }
//             }
//         })
//     }));

//     println!("Listening on http://{offer_addr}");
//     {
//         let mut pcm = PEER_CONNECTION_MUTEX.lock().await;
//         *pcm = Some(Arc::clone(&peer_connection));
//     }

//     tokio::spawn(async move {
//         let addr = SocketAddr::from_str(&offer_addr).unwrap();
//         let service =
//             make_service_fn(|_| async { Ok::<_, hyper::Error>(service_fn(remote_handler)) });
//         let server = Server::bind(&addr).serve(service);
//         // Run this server for... forever!
//         if let Err(e) = server.await {
//             eprintln!("server error: {e}");
//         }
//     });

//     // Create a datachannel with label 'data'
//     let data_channel = peer_connection.create_data_channel("data", None).await?;

//     let (done_tx, mut done_rx) = tokio::sync::mpsc::channel::<()>(1);

//     // Set the handler for Peer connection state
//     // This will notify you when the peer has connected/disconnected
//     peer_connection.on_peer_connection_state_change(Box::new(move |s: RTCPeerConnectionState| {
//         println!("Peer Connection State has changed: {s}");

//         if s == RTCPeerConnectionState::Failed {
//             // Wait until PeerConnection has had no network activity for 30 seconds or another failure. It may be reconnected using an ICE Restart.
//             // Use webrtc.PeerConnectionStateDisconnected if you are interested in detecting faster timeout.
//             // Note that the PeerConnection may come back from PeerConnectionStateDisconnected.
//             println!("Peer Connection has gone to failed exiting");
//             let _ = done_tx.try_send(());
//         }

//         Box::pin(async {})
//     }));

//     // Register channel opening handling
//     let d1 = Arc::clone(&data_channel);
//     data_channel.on_open(Box::new(move || {
//         println!("Data channel '{}'-'{}' open. Random messages will now be sent to any connected DataChannels every 5 seconds", d1.label(), d1.id());

//         let d2 = Arc::clone(&d1);
//         Box::pin(async move {
//             let mut result = Result::<usize>::Ok(0);
//             while result.is_ok() {
//                 let timeout = tokio::time::sleep(Duration::from_secs(5));
//                 tokio::pin!(timeout);

//                 tokio::select! {
//                     _ = timeout.as_mut() =>{
//                         let message = math_rand_alpha(15);
//                         println!("Sending '{message}'");
//                         result = d2.send_text(message).await.map_err(Into::into);
//                     }
//                 };
//             }
//         })
//     }));

//     Ok(())
// }

// async fn auth_handler() -> Result<()> {
//     Ok(())
// }

// async fn candidate_handler() -> Result<()> {
//     Ok(())
// }

// pub async fn new_ice_agent() -> Result<Agent, anyhow::Error> {
//     let agent_config = AgentConfig::default();
//     // In case of configuration changes they can be introduced here
//     let agent = Agent::new(agent_config).await?;
    
//     // TODO: Add handling of auth and candidates (see pion)

//     Ok(agent)
// }


// pub async fn handle_ice(pkt_buf: &mut Octets<'_>) -> Result<(), anyhow::Error> {
//     // TODO: Implement handling


//     Ok(())
// }
