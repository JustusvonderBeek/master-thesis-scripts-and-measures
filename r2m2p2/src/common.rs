
// Defining a trait and implementation for an abstract sending and receiving channel
// Allows to switch out the underlying socket infrastructure

use std::{cmp, collections::HashMap, io::Error, net::SocketAddr, os::fd::{FromRawFd, IntoRawFd}};

use anyhow::Result;
use mio::net::{UdpSocket};
use quiche::ConnectionId;
use ring::rand::SecureRandom;

const MAX_DATAGRAM_SIZE: usize = 1350;
pub const STUN_TEST_ALPN: [&[u8]; 2] = [b"quichestun", b"quichestun-00"];


pub type ClientId = u64;
pub type ClientIdMap = HashMap<ConnectionId<'static>, ClientId>;
pub type ClientMap = HashMap<ClientId, Client>;

pub struct Client {
    pub conn: quiche::Connection,

    pub client_id: ClientId,

    pub app_proto_selected: bool,

    pub max_datagram_size: usize,

    pub loss_rate: f64,

    pub max_send_burst: usize,
}

// Used to abstract the underlying socket and allow multiple
// sockets to be used in the application
pub trait UdpSocketConnection {
    fn send(&self, buf: &[u8]) -> Result<usize, std::io::Error>;
    fn send_to(&self, buf: &[u8], addr: SocketAddr) -> Result<usize, std::io::Error>;
    fn recv(&self, buf: &mut [u8]) -> Result<usize, std::io::Error>;
    fn recv_from(&self, buf: &mut [u8]) -> Result<(usize, SocketAddr), std::io::Error>;
    fn peek(&self, buf: &mut [u8]) -> Result<usize, std::io::Error>;
    fn local_addr(&self) -> Result<SocketAddr, std::io::Error>;
}

impl UdpSocketConnection for mio::net::UdpSocket {
    fn send(&self, buf: &[u8]) -> Result<usize, std::io::Error> {
        self.send(buf)
    }

    fn send_to(&self, buf: &[u8], addr: SocketAddr) -> Result<usize, std::io::Error> {
        self.send_to(buf, addr)
    }

    fn recv(&self, buf: &mut [u8]) -> Result<usize, std::io::Error> {
        self.recv(buf)
    }

    fn recv_from(&self, buf: &mut [u8]) -> Result<(usize, SocketAddr), std::io::Error> {
        self.recv_from(buf)
    }

    fn peek(&self, buf: &mut [u8]) -> Result<usize, std::io::Error> {
        self.peek(buf)
    }

    fn local_addr(&self) -> Result<SocketAddr, std::io::Error> {
        self.local_addr()
    }
}

// TODO: Add implementation for tokio socket
// TODO: Add implementation for std socket

pub fn bind_socket(address: Option<&str>) -> Result<Box<dyn UdpSocketConnection>> {

    let local_addr = match address {
        Some(s) => s,
        None => "0.0.0.0:0",
    };

    let socket = mio::net::UdpSocket::bind(local_addr.parse().unwrap()).unwrap();

    // Testing if converting to tokio would be possible
    // let raw_socket = socket.into_raw_fd();
    // let std_socket = unsafe {
    //     std::net::UdpSocket::from_raw_fd(raw_socket)
    // };
    // let tokio_socket = tokio::net::UdpSocket::from_std(std_socket);

    let boxed_s = Box::new(socket);

    return Ok(boxed_s);
}

pub fn create_quic_client_conf() -> Result<quiche::Config, Error> {
    let mut config = quiche::Config::new(quiche::PROTOCOL_VERSION).unwrap();
    create_quic_conf(&mut config);
    return Ok(config);
}

pub fn create_quic_conf(config: &mut quiche::Config) {
    // Values taken from quicheperf config
    config.set_max_idle_timeout(30_000);
    config.set_max_recv_udp_payload_size(MAX_DATAGRAM_SIZE);
    config.set_max_send_udp_payload_size(MAX_DATAGRAM_SIZE);
    config.set_initial_max_data(25165824);

    config.set_initial_max_stream_data_bidi_local(1000000);
    config.set_initial_max_stream_data_bidi_remote(1000000);
    config.set_initial_max_stream_data_uni(1000000);

    config.set_initial_max_streams_bidi(100);
    config.set_initial_max_streams_uni(100);
    config.set_disable_active_migration(false);
    config.set_active_connection_id_limit(30);
    config.set_multipath(true);

    config.set_max_connection_window(25_165_824);
    config.set_max_stream_window(16_777_216);

    config.enable_pacing(false);

    let mut keylog = None;

    if let Some(keylog_path) = std::env::var_os("SSLKEYLOGFILE") {
        let file = std::fs::OpenOptions::new()
            .create(true)
            .append(true)
            .open(keylog_path)
            .unwrap();

        keylog = Some(file);

        config.log_keys();
    }

    // TODO: This should later on be enabled again
    config.grease(false);

    config
        .set_cc_algorithm_name("cubic")
        .unwrap();

    return;
}

pub fn generate_cid_and_reset_token<T: SecureRandom>(rng: &T) -> (quiche::ConnectionId<'static>, u128) {
    let mut scid = [0; quiche::MAX_CONN_ID_LEN];
    rng.fill(&mut scid).unwrap();
    let scid = scid.to_vec().into();
    let mut reset_token = [0; 16];
    rng.fill(&mut reset_token).unwrap();
    let reset_token = u128::from_be_bytes(reset_token);
    (scid, reset_token)   
}

pub fn send_to(socket: &Box<dyn UdpSocketConnection>, buf: &[u8], send_info: &quiche::SendInfo, segment_size: usize) -> std::io::Result<usize> {
    let mut off = 0;
    let mut left = buf.len();
    let mut written = 0;

    while left > 0 {
        let pkt_len = cmp::min(left, segment_size);

        match socket.send_to(&buf[off..off + pkt_len], send_info.to) {
            Ok(v) => {
                written += v;
            },
            Err(e) => return Err(e),
        }

        off += pkt_len;
        left -= pkt_len;
    }

    Ok(written)
}