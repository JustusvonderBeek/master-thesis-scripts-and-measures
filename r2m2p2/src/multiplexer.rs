// This file contains the handling of a socket and 
// de-multiplexing different packets into the differnet
// ICE and QUIC stacks

use octets::{Octets};

// Expecting the QUIC or other header as input
// Deciding if the given input is QUIC or not
// Returns true if the packet is QUIC
pub fn is_packet_quic(b: &mut Octets) -> bool {
    let first = b.get_u8().unwrap();

    // For now we aim for the 2nd highest bit = 1
    if first & 0x40 == 0 {
        return false;
    }

    info!("Found quic packet");
    true
}