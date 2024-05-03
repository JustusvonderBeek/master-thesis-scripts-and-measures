# This file contains the setup and execution of mininet tests
# Each test:
# 1. Creates the topology required
# 2. Performs the measurement setup necessary for the test
# 3. Runs the test
# 4. Stores the result
# 5. Cleans the mininet environment
#

from dataclasses import dataclass
from mininet.node import Node, Switch, OVSController
from topologies import TwoConnections, TwoConnectionWithInternet, DirectAndInternet, InternetTopo, DirectAndInternetAndTURN
from measurement_util import capture_pcap, capture_ssl, terminate, stop_path, start_path, path_loss, set_default_route, if_down, if_up, wait, print_nat_table, create_new_test_folder, change_rights_test_folder
from logfile import filter_logfile_positiv
from mininet.net import Mininet
from mininet.cli import CLI
from pathlib import Path
from datetime import datetime

import mininet.net as net
import time
import os
import subprocess
import threading

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

def quic_stun():
    test_duration=10
    topo = DirectAndInternet()
    net = Mininet(topo=topo, controller = OVSController)
    DirectAndInternet.add_internet(net)
    net.start()

    h1_pcap = capture_pcap(net, "h1", ["h1-wifi", "h1-cellular"])
    h2_pcap = capture_pcap(net, "h2", ["h2-wifi", "h2-cellular"])

    time.sleep(0.5)

    h1 = net.get("h1")
    h2 = net.get("h2")

    os.environ["RUST_LOG"] = "info"
    server = h2.popen(f"/home/justus/Documents/Code/quicheperf-stun/target/debug/quicheperf server --cert /home/justus/Documents/Code/quicheperf-stun/src/cert.crt --key /home/justus/Documents/Code/quicheperf-stun/src/cert.key -l 192.168.1.3:10000 -l 2.40.60.3:10000", stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    client = h1.popen(f"/home/justus/Documents/Code/quicheperf-stun/target/debug/quicheperf client -l 192.168.1.2:20000 -l 1.20.30.2:20000 -c 192.168.1.3:10000 -c 2.40.60.3:10000 -b 10MB -d 2", stdout=subprocess.PIPE, stdin=subprocess.PIPE)

    print("Waiting 2s...")
    time.sleep(2)

    CLI(net)

    terminate(h1_pcap, terminate=True)
    terminate(h2_pcap, terminate=True)
    # terminate(turn, "turn/")
    terminate(server, "h2/", terminate=True)
    terminate(client, "h1/", terminate=True)

    net.stop()

    exit(0)

def start_turn_server(net, host):
    """Starting the 'coturn' turn server on the given host in the network.
    Returns the opened server process
    """

    h = net.get(host)
    # The server is correctly configured, nothing needed to answer simple STUN requests
    # And no login required; prevent creation of logfile under /var/log/turn_*
    cmd = f"/home/justus/Documents/Code/coturn/bin/turnserver -z --log-file stdout"
    process = h.popen(cmd)
    return process

@dataclass
class Configuration:
    """
    The default configuration for the mininet testing scenario.
    Should allow for long enough testing and all different kinds
    of scenarios for testing the ICE capabilities.
    """

    network_name: str = "Turn"
    log_level: str = "info"
    test_duration: int = 10
    debug: bool = False
    enable_pcap: bool = True
    enable_turn: bool = True
    enable_first_path: bool = True
    enable_second_path: bool = True
    enable_third_path: bool = True
    block_stun_on_first_path: bool = False

def create_network(conf):
    """
    Creating the network with the given name and configuration
    """

    network_name = conf.test_duration
    topo = DirectAndInternetAndTURN(
        second_path=conf.enable_second_path,
        third_path=conf.enable_third_path,
        block_stun=conf.block_stun_on_first_path,
    )
    network = Mininet(topo=topo, controller=OVSController)

    return network

def quic_ice():

    configuration = Configuration(
        debug=False,
        enable_second_path=False,
        enable_third_path=True,
    )

    # Creating the network
    # net = create_network(configuration)

    enable_turn=True
    enable_second_path=True
    enable_third_path=True
    save_delay=True
    debug_network=False
    enable_pcap=True
    block_stun=False
    topo = DirectAndInternetAndTURN(second_path=enable_second_path, third_path=enable_third_path, save_delay=save_delay, block_stun=block_stun)
    net = Mininet(topo=topo, controller = OVSController)
    # net = create_network(configuration)
    DirectAndInternetAndTURN.add_internet(net)
    DirectAndInternetAndTURN.enable_nat(net, block_stun=block_stun)
    net.start()

    directory = create_new_test_folder()

    # if not debug_network and not enable_pcap:
    h1_interfaces = ["h1-wifi", "h1-cellular"]
    h2_interfaces = ["h2-wifi", "h2-cellular"]
    if enable_third_path:
        h1_interfaces.append("h1-eth")
        h2_interfaces.append("h2-eth")

    h1_pcap, h1_pcap_file = capture_pcap(net, "h1", h1_interfaces, directory)
    h2_pcap, h2_pcap_file = capture_pcap(net, "h2", h2_interfaces, directory)
    s3_pcap, s3_pcap_file = capture_pcap(net, "s3", ["s3-eth1", "s3-eth2"], directory)
    nat1_pcap, nat1_pcap_file = capture_pcap(net, "nat1", ["nat1-local", "nat1-ext"], directory)
    nat2_pcap, nat2_pcap_file = capture_pcap(net, "nat2", ["nat2-local", "nat2-ext"], directory)
    if enable_third_path:
        nat3_pcap, nat3_pcap_file = capture_pcap(net, "nat3", ["nat3-local", "nat3-ext"], directory)
    # Kill the second interface on the client
    # TODO: Fix the routes on these interfaces when setting down again
    # if_down(net, "h1", "h1-cellular")

    if enable_turn:
        turn = start_turn_server(net, "turn")
        turn_pcap, turn_pcap_file = capture_pcap(net, "turn", ["turn-eth0"], directory)

    time.sleep(0.5)

    h1 = net.get("h1")
    h2 = net.get("h2")

    log_level = "info"
    quic_duration = 100 # Otherwise the test stops after 10s

    os.environ["RUST_LOG"] = log_level
    # os.environ["RUST_BACKTRACE"] = "1"

    # ip_storage = if_down(net, "h1", "h1-cellular")

    if configuration.debug:
        CLI(net)
        terminate(h1_pcap, file_perm=h1_pcap_file)
        terminate(h2_pcap, file_perm=h2_pcap_file)
        net.stop()
        exit(0)

    time.sleep(0.5)

    if log_level == "trace" or log_level == "debug":
        server = h2.popen(f"/home/justus/Documents/Code/quicheperf-stun/target/debug/quicheperf server --cert /home/justus/Documents/Code/quicheperf-stun/src/cert.crt --key /home/justus/Documents/Code/quicheperf-stun/src/cert.key -l 192.168.1.3:10000 &> /home/justus/Documents/Code/2024-justus-von-der-beek-supplementary-material/{directory}/h2.log", shell=True)
        client = h1.popen(f"/home/justus/Documents/Code/quicheperf-stun/target/debug/quicheperf client -l 192.168.1.2:20000 -c 192.168.1.3:10000 -b 10MB --mp true -d {quic_duration} &> /home/justus/Documents/Code/2024-justus-von-der-beek-supplementary-material/{directory}/h1.log", shell=True)
    else:
        server = h2.popen(f"/home/justus/Documents/Code/quicheperf-stun/target/debug/quicheperf server --cert /home/justus/Documents/Code/quicheperf-stun/src/cert.crt --key /home/justus/Documents/Code/quicheperf-stun/src/cert.key -l 192.168.1.3:10000 --mp true", stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        client = h1.popen(f"/home/justus/Documents/Code/quicheperf-stun/target/debug/quicheperf client -l 192.168.1.2:20000 -c 192.168.1.3:10000 -b 10MB --mp true -d {quic_duration}", stdout=subprocess.PIPE, stdin=subprocess.PIPE)

        # server = h2.popen(f"/home/justus/Documents/Code/webrtc_unmod/target/debug/examples/ping_pong -c 192.168.1.2 -p", stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        # client = h1.popen(f"/home/justus/Documents/Code/webrtc_unmod/target/debug/examples/ping_pong -c 192.168.1.3 --controlling -p", stdout=subprocess.PIPE, stdin=subprocess.PIPE)

    wait()

    # ip_storage = if_down(net, "h1", "h1-wifi")

    # write_new_ice_cand_file("1.20.30.2:20000")
    # # # TODO: Add the functions to start the interface and probe on the new path
    # set_default_route(net, "h1", "1.20.30.1", "h1-cellular")
    # time.sleep(0.5)
    # Everything else should happen automatically
    wait()
    # wait(10)

    # ip_storage = if_up(net, "h1", "h1-wifi", ip_storage)

    # # WiFi-Direct is 100ms - Internet is 70ms so should be faster
    # write_new_if_file("1.20.30.2:20000", "2.40.60.3:10000")

    # print(f"Waiting {test_duration}s...")
    # time.sleep(test_duration)

    # Testing if the implementation can switch the paths already
    # if_down(net, "h1", "h1-wifi")
    # stop_path(net, "h1", "h2")
    # path_loss(net, "h1", "h1-wifi")
    # wait()

    # Open the CLI and allow user input
    CLI(net)

    terminate(h1_pcap, file_perm=h1_pcap_file)
    terminate(h2_pcap, file_perm=h2_pcap_file)
    terminate(s3_pcap, file_perm=s3_pcap_file)
    terminate(nat1_pcap, file_perm=nat1_pcap_file)
    terminate(nat2_pcap, file_perm=nat2_pcap_file)
    if enable_third_path:
        terminate(nat3_pcap, file_perm=nat3_pcap_file)
    # terminate(turn, "turn/")

    print_nat_table(net, "nat1", directory)
    print_nat_table(net, "nat2", directory)
    if enable_third_path:
        print_nat_table(net, "nat3", directory)

    if log_level == "trace" or log_level == "debug":
        terminate(server)
        terminate(client)
        print(f"Stored logfile to: '{directory}/<host>.log'")
        filter_logfile_positiv(f"{directory}/h1.log", ["webrtc", "restarting"])
        filter_logfile_positiv(f"{directory}/h2.log", ["webrtc", "restarting"])
    else:
        terminate(server, f"{directory}/h2.log")
        terminate(client, f"{directory}/h1.log")

        # terminate(server_unmod, "h2/")
        # terminate(client_unmod, "h1/")

    if enable_turn:
        terminate(turn_pcap, file_perm=turn_pcap_file)
        print("Stopping turn server, this takes a few seconds...")
        terminate(turn, f"{directory}/turn.log")

    net.stop()

    change_rights_test_folder(directory)

    exit(0)

def test_quic_multipath():
    test_duration=5
    topo = DirectAndInternet()
    net = Mininet(topo=topo, controller = OVSController)
    DirectAndInternet.add_directlink(net)
    net.start()

    h1_pcap, h1_pcap_file = capture_pcap(net, "h1")
    h2_pcap, h2_pcap_file = capture_pcap(net, "h2")

    # Kill the second interface on the client
    # TODO: Fix the routes on these interfaces when setting down again
    # if_down(net, "h1", "h1-cellular")

    time.sleep(0.5)

    h1 = net.get("h1")
    h2 = net.get("h2")

    os.environ["RUST_LOG"] = "trace"
    # os.environ["RUST_BACKTRACE"] = "1"
    server = h2.popen(f"/home/ifrit/Documents/Code/quicheperf-stun/target/debug/quicheperf server --cert /home/ifrit/Documents/Code/quicheperf-stun/src/cert.crt --key /home/ifrit/Documents/Code/quicheperf-stun/src/cert.key -l 192.168.1.3:10000 -l 2.40.60.3:10000", stdout=subprocess.PIPE, stdin=subprocess.PIPE)

    client_testfile = open("h1/test.log", "w+")

    client = h1.popen(f"/home/ifrit/Documents/Code/quicheperf-stun/target/debug/quicheperf client -l 192.168.1.2:20000 -l 1.20.30.2:20000 -c 192.168.1.3:10000 -c 2.40.60.3:10000 -b 10MB --mp true &> /home/", stdout=client_testfile, stdin=client_testfile, bufsize=8192)

    # Polling from popen
    # poll_thread1 = threading.Thread(target=poll_output, args=(client, "h1/"))
    # poll_thread1.daemon = True # Terminate as soon as the process terminates
    # poll_thread1.start()

    terminate(client, outfile="h1/", overwrite=True)

    print(f"Waiting {test_duration}s...")
    time.sleep(test_duration)

    # write_new_ice_cand_file("1.20.30.2:20000")
    # # # TODO: Add the functions to start the interface and probe on the new path
    # if_up(net, "h1", "h1-cellular")
    # time.sleep(0.5)
    # Everything else should happen automatically
    # time.sleep(test_duration)

    # # WiFi-Direct is 100ms - Internet is 70ms so should be faster
    # write_new_if_file("1.20.30.2:20000", "2.40.60.3:10000")

    # print(f"Waiting {test_duration}s...")
    # time.sleep(test_duration)

    # Testing if the implementation can switch the paths already
    # if_down(net, "h1", "h1-wifi")
    # stop_path(net, "h1", "h2")
    path_loss(net, "h1", "h1-cellular")
    path_loss(net, "h2", "h2-cellular")
    print(f"Waiting {test_duration}s...")
    time.sleep(test_duration)

    # Open the CLI and allow user input
    CLI(net)

    terminate(h1_pcap, file_perm=h1_pcap_file)
    terminate(h2_pcap, file_perm=h2_pcap_file)
    # terminate(turn, "turn/")
    terminate(server, "h2/", terminate=True)
    # terminate(client, "h1/")
    terminate(client, terminate=True)

    client_testfile.close()

    net.stop()

    exit(0)


# TODO: Repeat the experiment with our own implementation

topologies = { 'quicheperf': (lambda: quicheperf()), "quic-stun": (lambda: quic_stun()), "p2p": (lambda: p2p_webrtc()), 'inet-wifi': (lambda: quic_multiplex()) }

if __name__ == "__main__":

    # Parsing the command line
    # Only options are to disable pcap or log output or debug network
    # TODO:

    # quicheperf()
    # p2p_webrtc()
    # quic_multiplex()
    # quic_stun()
    quic_ice()
    # test_quic_multipath()