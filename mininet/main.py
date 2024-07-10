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
# from topologies import TwoConnections, TwoConnectionWithInternet, DirectAndInternet, InternetTopo, DirectAndInternetAndTURN
from measurement_util import capture_pcap, capture_ssl, terminate, stop_path, start_path, path_loss, wait, print_nat_table, create_new_test_folder, change_rights_test_folder
from topologies.topologies import create_test_scenario
from config import Scenarios, Logging, Tests, TestConfiguration
from logfile import filter_logfile_positiv
from experiment import start_test


from mininet.net import Mininet
from mininet.cli import CLI
from pathlib import Path

import time
import os
import subprocess
import argparse

# def start_quicheperf_server(net):
#     """Starting the quicheperf server"""

#     h2 = net.get("h2")
#     Path("h2").mkdir(parents=True, exist_ok=True)
#     os.environ["RUST_LOG"] = "debug"
#     scheduler = "round-robin"
#     server = h2.popen(f"../quicheperf/target/release/quicheperf server -l 10.0.1.10:443 -l 172.16.2.20:443 --mp true --scheduler {scheduler} --cert ../quicheperf/src/cert.crt --key ../quicheperf/src/cert.key", stdout=subprocess.PIPE)

#     return server

# def start_quicheperf_client(net):
#     """Starting the quicheperf client"""

#     h1 = net.get("h1")
#     # Path is .../Code/..supplementary-material
#     Path("h1").mkdir(parents=True, exist_ok=True)
#     os.environ["RUST_LOG"] = "debug"
#     duration = "10"
#     bitrate = "1MB"
#     scheduler = "round-robin"
#     print(f"Duration: {duration}s , Bitrate {bitrate}")
#     client = h1.popen(f"../quicheperf/target/release/quicheperf client -c 10.0.1.10:443 -c 172.168.2.20:443 -l 192.168.1.10:0 -l 172.16.1.10:0 --mp true --scheduler {scheduler} --duration {duration} --bitrate {bitrate}", stdout=subprocess.PIPE)

#     return client

# def start_webrtc_server(net):
#     """
#     Starting the WebRTC answerer
#     """

#     h2 = net.get("h2") # Should be the one without firewall
#     Path("h2").mkdir(parents=True, exist_ok=True)
#     os.environ["RUST_LOG"] = "debug"
#     # server = h2.popen(f"../webrtc/target/debug/examples/answer --offer-address 1.20.30.10:50000", stdout=subprocess.PIPE)
#     server = h2.popen(f"../webrtc/target/debug/examples/answer --offer-address 192.168.1.2:50000", stdout=subprocess.PIPE)
#     return server

# def start_webrtc_client(net):
#     """
#     Starting the WebRTC questioner
#     """

#     h1 = net.get("h1") # Should be the one behind the firewall
#     Path("h1").mkdir(parents=True, exist_ok=True)
#     os.environ["RUST_LOG"] = "debug"
#     # client = h1.popen(f"../webrtc/target/debug/examples/offer --debug --answer-address 2.40.60.20:60000", stdout=subprocess.PIPE)
#     client = h1.popen(f"../webrtc/target/debug/examples/offer --debug --answer-address 192.168.1.3:60000", stdout=subprocess.PIPE)
#     return client

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

# ------------------------------------------------------------------------------------
# Predefined scenarios
# ------------------------------------------------------------------------------------

def test_failure_nat_webrtc_example(args):
    """
    Creating the configuration so that the strange NAT behavior can
    be shown
    """

    args.setup = "single+internet"
    # Use the default ping to show that it's not our implementation but rather the NAT itself
    args.test = "ice_ping"
    # args.test = "quicheperf"
    args.logging = 3
    args.debug = False
    args.disable_turn = False
    args.cli = False
    args.disable_pcap = False
    args.snat = False

    config = TestConfiguration(args)
    # This should create enough delay to show the wrong NAT behavior
    config.internet_path_ext_delay = 10
    config.internet_path_ext_2_delay = 10
    # If the one path is >= than the entire other path towards the host it breaks
    # Here 1:1 in comparison should be enough (here > 20)
    config.internet_path_local_delay = 35
    config.internet_path_local_2_delay = 10
    config.internet_path_turn_delay = 10
    config.wifi_direct_path_delay = 3

    return config

def test_correct_nat_delay(args):
    """
    Creating a configuration so that the cellular path barely makes
    it from a timing standpoint
    """
    
    args.setup = "full"
    args.test = "quicheperf"
    args.logging = 3
    args.debug = False
    args.disable_turn = False
    args.cli = False
    args.disable_pcap = False

    config = TestConfiguration(args)
    # If the internet path is > local and the wifi is < Host->NAT we should not see errors
    # Roughly 2:1 makes no problems
    config.internet_path_ext_delay = 15
    config.internet_path_ext_2_delay = 15
    config.internet_path_local_delay = 3
    config.internet_path_local_2_delay = 3
    config.internet_path_turn_delay = 1
    config.wifi_direct_path_delay = 5
    
    return config

def test_wifi_path_delay_ratio(args):
    """
    Creating a configuration to test the ratio at which the NAT
    traversal fails due to timing issues
    """
    
    args.setup = "single+internet"
    args.test = "quicheperf"
    args.logging = 3
    args.debug = False
    args.disable_turn = False
    args.cli = False
    args.disable_pcap = False

    config = TestConfiguration(args)
    # This should create enough delay to show the wrong NAT behavior
    config.internet_path_ext_delay = 10
    config.internet_path_ext_2_delay = 10
    config.internet_path_local_delay = 5
    config.internet_path_local_2_delay = 5
    config.internet_path_turn_delay = 1
    # If the synchronization path is >= than the path Host->NAT it breaks
    # Roughly >2:3 in length but more important for faster paths
    config.wifi_direct_path_delay = 20
    
    return config

# ------------------------------------------------------------------------------------
# Predefined scenarios
# ------------------------------------------------------------------------------------

def main():
    """
    Starting the main function, parsing the command line and starting the relevant tests
    """

    # Parsing the command line
    # Only options are to disable pcap or log output or debug network
    parser = argparse.ArgumentParser(description="Creating measurement environment for the master thesis and executing tests")
    parser.add_argument('-s', '--setup', type=str, default="default")
    parser.add_argument('-t', '--test', type=str, default="quicheperf")
    parser.add_argument('-l', '--duration', type=int, default=100)
    parser.add_argument('--disable-pcap', action='store_true', default=False)
    parser.add_argument('-d', '--debug', action='store_true', default=False)
    parser.add_argument('-c', '--cli', action='store_true', default=False)
    parser.add_argument('-p', '--permissions', action='store_true', default=True)
    parser.add_argument('--disable-turn', action='store_true', default=False)
    parser.add_argument('-n', '--snat', action='store_true', default=False)
    parser.add_argument('-k', '--log-sslkeys', action='store_true', default=False)
    parser.add_argument('--logging', type=int, default=3)
    parser.add_argument('--build-target', type=str, default="debug")
    parser.add_argument('--throughput', type=str, default="1MB")
    parser.add_argument('--scenario', type=str)
    parser.add_argument('--real', action='store_true', default=False)
    args = parser.parse_args()

    if args.scenario is None:
        test_conf = TestConfiguration(args)
    else:
        match args.scenario:
            case "nat_fail":
                test_conf = test_failure_nat_webrtc_example(args)
            case "default":
                test_conf = test_correct_nat_delay(args)
            case "delay_wifi":
                test_conf = test_wifi_path_delay_ratio(args)
            case _:
                print(f"Incorrect scenario '{args.scenario}' given")
                exit(1)
                          
    net = create_test_scenario(test_conf)
    start_test(net, test_conf)

    # Try to avoid halve closed networks or other problems
    net.stop()

    print("All tests completed...")

if __name__ == "__main__":
    main()