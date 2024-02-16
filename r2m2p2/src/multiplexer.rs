// This file contains the handling of a socket and 
// de-multiplexing different packets into the different
// ICE and QUIC stacks

use std::{net::SocketAddr, sync::Arc};
use async_trait::async_trait;
use anyhow::Result;
use octets::Octets;

// Define an universal trait that we require the socket to have
// This allows using multiple UdpSocket implementations
#[async_trait]
pub trait MultiplexUdpSocket {
    async fn recv(&self, buf: &mut [u8]) -> Result<usize>;
    async fn recv_from(&self, buf: &mut [u8]) -> Result<(usize, SocketAddr)>;
    async fn peek(&self, buf: &mut  [u8]) -> Result<usize>;
}

// Adding the individual implementation for the different UdpSocket types below
#[async_trait]
impl MultiplexUdpSocket for tokio::net::UdpSocket {
    async fn recv(&self, buf: &mut [u8]) -> Result<usize> {
        self.recv(buf).await.map_err(|e| e.into())
    }

    async fn recv_from(&self, buf: &mut [u8]) -> Result<(usize, SocketAddr)> {
        self.recv_from(buf).await.map_err(|e| e.into())
    }

    async fn peek(&self, buf: &mut [u8]) -> Result<usize> {
        self.peek(buf).await.map_err(|e| e.into())
    }
}

#[async_trait]
impl MultiplexUdpSocket for mio::net::UdpSocket {
    async fn recv(&self, buf: &mut [u8]) -> Result<usize> {
        self.recv(buf).map_err(|e| e.into())
    }

    async fn recv_from(&self, buf: &mut [u8]) -> Result<(usize, SocketAddr)> {
        self.recv_from(buf).map_err(|e| e.into())
    }

    async fn peek(&self, buf: &mut [u8]) -> Result<usize> {
        self.peek(buf).map_err(|e| e.into())
    }
}

async fn poll_udp_socket(udp_socket : Arc<dyn MultiplexUdpSocket>, buf: &mut [u8]) -> Result<(usize, SocketAddr)> {
    udp_socket.recv_from(buf).await
}

// Expecting the QUIC or other header as input
// Deciding if the given input is QUIC or not
// Returns true if the packet is QUIC
pub fn is_packet_quic(b: &[u8]) -> bool {
    // For now we aim for the 2nd highest bit = 1
    return b[0] & 0x40 != 0;
}

pub struct Multiplexer {
    // Allows ICE and QUICHE to register their callbacks here
    ice_callback: Option<fn(&mut [u8]) -> Result<()>>,
    quic_callback: Option<fn(&mut [u8]) -> Result<()>>,
}

impl Multiplexer {

    pub fn new() -> Multiplexer {
        let m = Multiplexer { 
            ice_callback: None, 
            quic_callback: None 
        };
        m
    }

    pub fn register_ice_callback(&mut self, ice_callback: fn(&mut [u8]) -> Result<()>) {
        self.ice_callback = Some(ice_callback);
    }

    pub fn register_quic_callback(&mut self, quic_callback: fn(&mut [u8]) -> Result<()>) {
        self.quic_callback = Some(quic_callback);
    }

    pub async fn start_multiplex(&mut self, udp_socket : Arc<dyn MultiplexUdpSocket>) {
        let mut buf = [0; 65535];
        
        loop {
            let udp_socket2 = Arc::clone(&udp_socket);
            let (read, addr) = match poll_udp_socket(udp_socket2, &mut buf).await {
                Ok(r) => r,
                Err(e) => {
                    println!("Failed to poll from remote: {}", e);
                    break;
                }
            };
            if is_packet_quic(&buf[..1]) {
                debug!("Quic packet");
                if let Some(callback) = self.quic_callback {
                    callback(&mut buf).unwrap();
                }
            } else {
                debug!("Other packet");
                if let Some(callback) = self.ice_callback {
                    callback(&mut buf).unwrap();
                }
            }
        }

        println!("Multiplexing loop exited");
    }
}
