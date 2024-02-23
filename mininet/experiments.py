# This file contains the setup and execution of mininet tests
# Each test:
# 1. Creates the topology required
# 2. Performs the measurement setup necessary for the test
# 3. Runs the test
# 4. Stores the result
# 5. Cleans the mininet environment
# 


from mininet.node import Node, Switch, OVSController
from topologies import TwoConnections, TwoConnectionWithInternet, DirectAndInternet, InternetTopo
from measurement_util import capture_pcap, capture_ssl, terminate, stop_path, start_path
from mininet.net import Mininet
from mininet.cli import CLI
from pathlib import Path

import mininet.net as net
import time
import os
import subprocess

def start_quicheperf_server(net):
    """Starting the quicheperf server"""

    h2 = net.get("h2")
    Path("h2").mkdir(parents=True, exist_ok=True)
    os.environ["RUST_LOG"] = "debug"
    scheduler = "round-robin"
    server = h2.popen(f"../quicheperf/target/release/quicheperf server -l 10.0.1.10:443 -l 172.16.2.20:443 --mp true --scheduler {scheduler} --cert ../quicheperf/src/cert.crt --key ../quicheperf/src/cert.key", stdout=subprocess.PIPE)

    return server

def start_quicheperf_client(net):
    """Starting the quicheperf client"""

    h1 = net.get("h1")
    # Path is .../Code/..supplementary-material
    Path("h1").mkdir(parents=True, exist_ok=True)
    os.environ["RUST_LOG"] = "debug"
    duration = "10"
    bitrate = "1MB"
    scheduler = "round-robin"
    print(f"Duration: {duration}s , Bitrate {bitrate}")
    client = h1.popen(f"../quicheperf/target/release/quicheperf client -c 10.0.1.10:443 -c 172.168.2.20:443 -l 192.168.1.10:0 -l 172.16.1.10:0 --mp true --scheduler {scheduler} --duration {duration} --bitrate {bitrate}", stdout=subprocess.PIPE)
    
    return client

def quicheperf():
    """Executing the quicheperf test to check our functionality"""

    topo = TwoConnections()
    net = Mininet(topo=topo, controller = OVSController)
    net.start()
    TwoConnections.configure_routing(net)

    procs = list()
    capture_ssl(net, "h2")
    h2_pcap = capture_pcap(net, "h2")
    h1_pcap = capture_pcap(net, "h1")
    procs.append({"proc" : h2_pcap, "name" : None })
    procs.append({"proc" : h1_pcap, "name" : None })
    # This is required to be able to capture the handshake and the initial packets of the connection
    time.sleep(0.5)

    server = start_quicheperf_server(net)
    procs.append({"proc" : server, "name" : "h2"})
    client = start_quicheperf_client(net)
    procs.append({"proc" : client, "name" : "h1"})
    CLI(net)
    for proc in procs:
        if proc["name"] is not None:
            terminate(proc["proc"], proc["name"] + "/")
        else:
            terminate(proc["proc"])
    net.stop()
    # We don't want to start the CLI again
    exit(0)

def start_webrtc_server(net):
    """
    Starting the WebRTC answerer
    """

    h2 = net.get("h2") # Should be the one without firewall
    Path("h2").mkdir(parents=True, exist_ok=True)
    os.environ["RUST_LOG"] = "debug"
    # server = h2.popen(f"../webrtc/target/debug/examples/answer --offer-address 1.20.30.10:50000", stdout=subprocess.PIPE)
    server = h2.popen(f"../webrtc/target/debug/examples/answer --offer-address 192.168.1.2:50000", stdout=subprocess.PIPE)
    return server

def start_webrtc_client(net):
    """
    Starting the WebRTC questioner
    """

    h1 = net.get("h1") # Should be the one behind the firewall
    Path("h1").mkdir(parents=True, exist_ok=True)
    os.environ["RUST_LOG"] = "debug"
    # client = h1.popen(f"../webrtc/target/debug/examples/offer --debug --answer-address 2.40.60.20:60000", stdout=subprocess.PIPE)
    client = h1.popen(f"../webrtc/target/debug/examples/offer --debug --answer-address 192.168.1.3:60000", stdout=subprocess.PIPE)
    return client

def start_turn_server(net):
    """
    Starting a TURN/STUN server at the host in the 'internet' localtion
    """

    Path("turn").mkdir(parents=True, exist_ok=True)
    turn = net.get("turn")
    Path("turn").mkdir(parents=True, exist_ok=True)
    
    turnserver = turn.popen(f"../coturn/bin/turnserver", stdout=subprocess.PIPE)
    return turnserver


def p2p_webrtc():
    """
    Launching a direct peer-to-peer connection between two WebRTC clients
    Includes breaking the connection and letting WebRTC figure out the reconnect
    """

    test_duration=10
    # topo = TwoConnectionWithInternet()
    topo = DirectAndInternet()
    net = Mininet(topo=topo, controller = OVSController)
    # Include internet connection
    DirectAndInternet.add_internet(net)
    # TwoConnectionWithInternet.configure_routing(net)
    # TwoConnectionWithInternet.add_internet(net)
    # TwoConnectionWithInternet.configure_firewall(net)
    net.start()

    procs = list()
    h2_pcap = capture_pcap(net, "h2")
    h1_pcap = capture_pcap(net, "h1")
    procs.append({"proc" : h2_pcap, "name" : None })
    procs.append({"proc" : h1_pcap, "name" : None })
    # This is required to be able to capture the handshake and the initial packets of the connection
    time.sleep(0.5)

    # Start the webrtc client and server
    server = start_webrtc_server(net)
    procs.append({"proc":server, "name": "h2"})
    time.sleep(0.1) # So the server has time to start
    client = start_webrtc_client(net)
    procs.append({"proc":client, "name": "h1"})

    print(f"Testing for {test_duration}s ...")
    time.sleep(test_duration)
    stop_path(net, "h1", "h2")
    print("Waiting 10s...")
    time.sleep(10)
    start_path(net, "h1", "h2")
    print("Waiting 10s...")
    time.sleep(10)

    CLI(net) # When the user kills the CLI, we stop recording
    for proc in procs:
        if proc["name"] is not None:
            terminate(proc["proc"], proc["name"] + "/")
        else:
            terminate(proc["proc"])
    net.stop()
    # We don't want to start the CLI again
    exit(0)

def quic_multiplex():
    test_duration=10
    topo = DirectAndInternet()
    net = Mininet(topo=topo, controller = OVSController)
    DirectAndInternet.add_internet(net)
    net.start()

    h1_pcap = capture_pcap(net, "h1")
    h2_pcap = capture_pcap(net, "h2")

    h1 = net.get("h1")
    h2 = net.get("h2")
    
    # turn = start_turn_server(net)
    # Cert dir depending on call dir, expecting: master-dir
    os.environ["RUST_LOG"] = "trace"
    server = h2.popen(f"./r2m2p2/target/debug/quic-multiplex -k r2m2p2/resources -l 192.168.1.3 -r 192.168.1.2 -c -m", stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    client = h1.popen(f"./r2m2p2/target/debug/quic-multiplex -l 192.168.1.2 -r 192.168.1.3 -m", stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    # Processes require the enter key to start
    # time.sleep(1)
    # print("Starting controlling")
    # server.communicate(input=b"\n\r") # Doesn't work for controlling?
    # time.sleep(1)
    # print("Starting controlled")
    # client.communicate(input=b"\n\r")

    print("Waiting 20s...")
    time.sleep(20)

    CLI(net)

    terminate(h1_pcap)
    terminate(h2_pcap)
    # terminate(turn, "turn/")
    terminate(server, "h2/")
    terminate(client, "h1/")

    net.stop()
    
    exit(0)

# TODO: Repeat the experiment with our own implementation

topologies = { 'quicheperf': (lambda: quicheperf()), "p2p": (lambda: p2p_webrtc()), 'inet-wifi': (lambda: quic_multiplex()) }

if __name__ == "__main__":
    # quicheperf()
    # p2p_webrtc()
    quic_multiplex()