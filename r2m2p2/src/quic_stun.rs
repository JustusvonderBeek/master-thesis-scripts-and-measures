/* This file contains the prototype for moving the
    Address Gathering into QUIC.
*/

use anyhow::{Error};
use clap::{App, Arg};
use quic_client::connect;
use quic_server::start_server;

mod quic_client;
mod quic_server;
mod common;

#[macro_use]
extern crate log;

fn main() -> Result<(), Error> {
    env_logger::builder()
        .default_format()
        .init();

    // Parsing the command line
    let app = App::new("QUIC internal STUN")
        .version("0.1")
        .about("A prototype implementation of STUN information transferred via QUIC")
        .arg(
            Arg::with_name("remote")
                .takes_value(true)
                .long("remote")
                .short('r')
                .default_value("127.0.0.1:12345")
                .help("Remote endpoint ip to initially connect to")
        )
        .arg(
            Arg::with_name("client")
                .takes_value(false)
                .long("client")
                .short('c')
                .help("If the program is accepting connections or connecting to an endpoint")
        )
        .arg(
            Arg::with_name("cert-dir")
                .takes_value(true)
                .long("cert_dir")
                .short('k')
                .default_value("resources")
                .help("The directory containing the certificate and private key. Only relevant for the server")
        );

    // Extracting the given arguments
    let matches = app.clone().get_matches();

    let client = matches.is_present("client");
    let remote = matches.value_of("remote").expect("Endpoint expected but non given!");


    // Step 1: Starting a default QUIC connection between two clients
    // In this case we pretend to be in the same WiFi Direct
    // The process of finding this connection is not as relevant for this test

    if client {
        // TODO: This starts the client but does not allow for anything 
        // else to happen afterwards
        match connect(remote) {
            Err(e) => error!("Client failed: {}", e),
            Ok(_) => info!("Client gracefully closed"),
        }
        return Ok(());
    } else {
        // Server
        // let cert_dir = matches.value_of("cert-dir").expect("Expected certificate dir for server but non given!");
        
        // TODO: Fix not doing anything after starting the server
        match start_server() {
            Ok(_) => info!("Server closed gracefully"),
            Err(e) => error!("Server failed: {}", e),
        }
    }

    // Step 2: Starting the ICE gathering process
    // The ICE agent should ask QUIC what (I think) server-rflx addresses are found
    
    // Step 3: Starting the connectivity checks
    // ICE should ask QUIC to build a new connection based on the given candidates
    // Handling of when and where to is ICE's domain, performing the action is QUIC


    return Ok(())
}