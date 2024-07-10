# This file is meant to contain the actual mininet tests
# 
# A test contains the starting of an application as well as
# the logging for the application
# The method must return a list of tuples containing the process
# and the outfile of the logging in case logging is enabled
# 
# Closing the processes and writing the logfile is then done
# by the wrapper function

from config import Logging
from measurement_util import wait, path_loss, iface_down, iface_up, set_conntrack_timeout, print_nat_table, remove_conntrack_entry
from mininet.net import CLI

import subprocess

# Some useful information for testing
username = "justus"
code_dir = f"/home/{username}/Documents/Code"
quicheperf_dir = f"{code_dir}/quicheperf-stun"
testing_dir = f"{code_dir}/2024-justus-von-der-beek-supplementary-material"


def quicheperf(net, directory, conf):
    """
    Starting the actual application we want to test.
    Responsible for starting the application and logging.
    Must return a list of tuple holding (process, logfile)
    which will be terminated by the wrapper. If the logfile
    is 'None' then we expect the application to directly write
    into the logfile and therefore no output is processed by
    the wrapper.
    """

    h1 = net.get("h1")
    h2 = net.get("h2")

    target = conf.build_target
    tp = conf.throughput
    output_processes = []

    # print("Executing: {}".format(f"{quicheperf_dir}/target/{target}/quicheperf server --cert {quicheperf_dir}/src/cert.crt --key {quicheperf_dir}/src/cert.key -l 192.168.1.3:10000 --mp true"))

    if conf.log_level.value > Logging.INFO.value:
        server = h2.popen(f"{quicheperf_dir}/target/{target}/quicheperf server --cert {quicheperf_dir}/src/cert.crt --key {quicheperf_dir}/src/cert.key -l 192.168.1.3:10000 --mp true &> {testing_dir}/{directory}/h2.log", shell=True)

        client = h1.popen(f"{quicheperf_dir}/target/{target}/quicheperf client -l 192.168.1.2:20000 -c 192.168.1.3:10000 --mp true -d {conf.duration} -b {tp} &> {testing_dir}/{directory}/h1.log", shell=True)

        server_capture = (server, None)
        client_capture = (client, None)
        output_processes.append(server_capture)
        output_processes.append(client_capture)
    else:
        server = h2.popen(f"{quicheperf_dir}/target/{target}/quicheperf server --cert {quicheperf_dir}/src/cert.crt --key {quicheperf_dir}/src/cert.key -l 192.168.1.3:10000 --mp true", stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

        client = h1.popen(f"{quicheperf_dir}/target/{target}/quicheperf client -l 192.168.1.2:20000 -c 192.168.1.3:10000 --mp true -d {conf.duration} -b {tp}", stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    
        server_capture = (server, f"{directory}/h2.log")
        client_capture = (client, f"{directory}/h1.log")
        output_processes.append(server_capture)
        output_processes.append(client_capture)

    # path_loss(net, "h1", "h1-wifi")
    wait(20)
    # path_loss(net, "h1", "h1-wifi", loss=0)
    # wait()

    # Finished testing
    return output_processes

def quicheperf_if_test(net, directory, conf):
    """
    Testing the behavior of the implementation in case an interface goes up or down.
    """

    h1 = net.get("h1")
    h2 = net.get("h2")

    target = conf.build_target
    tp = conf.throughput
    output_processes = []

    # ip_storage = iface_down(net, "h1", "h1-eth", directory)
    # Ensure interface is down
    # wait(0.5)

    if conf.log_level.value > Logging.INFO.value:
        server = h2.popen(f"{quicheperf_dir}/target/{target}/quicheperf server --cert {quicheperf_dir}/src/cert.crt --key {quicheperf_dir}/src/cert.key -l 192.168.1.3:10000 --mp true &> {testing_dir}/{directory}/h2.log", shell=True)

        client = h1.popen(f"{quicheperf_dir}/target/{target}/quicheperf client -l 192.168.1.2:20000 -c 192.168.1.3:10000 --mp true -d {conf.duration} -b {tp} &> {testing_dir}/{directory}/h1.log", shell=True)

        server_capture = (server, None)
        client_capture = (client, None)
        output_processes.append(server_capture)
        output_processes.append(client_capture)
    else:
        server = h2.popen(f"{quicheperf_dir}/target/{target}/quicheperf server --cert {quicheperf_dir}/src/cert.crt --key {quicheperf_dir}/src/cert.key -l 192.168.1.3:10000 --mp true", stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

        client = h1.popen(f"{quicheperf_dir}/target/{target}/quicheperf client -l 192.168.1.2:20000 -c 192.168.1.3:10000 --mp true -d {conf.duration} -b {tp}", stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    
        server_capture = (server, f"{directory}/h2.log")
        client_capture = (client, f"{directory}/h1.log")
        output_processes.append(server_capture)
        output_processes.append(client_capture)

    # Waiting long enough so that we establish some connection on both paths
    wait(7)
    # IFace down
    ip_storage = iface_down(net, "h1", "h1-cellular", directory)
    # Wait more than a single iteration before interface has connection again
    wait(20)
    
    # Restore interface and IP, waiting for ICE to notice
    ip_storage = iface_up(net, "h1", "h1-cellular", directory, ip_storage)
    wait(20)

    # Finished testing
    return output_processes

def quicheperf_if_init_test(net, directory, conf):
    """
    Testing the behavior of the implementation in case an interface goes up or down.
    """

    h1 = net.get("h1")
    h2 = net.get("h2")

    target = conf.build_target
    tp = conf.throughput
    output_processes = []

    ip_storage = iface_down(net, "h1", "h1-eth", directory)
    # Ensure interface is down
    wait(0.5)

    if conf.log_level.value > Logging.INFO.value:
        server = h2.popen(f"{quicheperf_dir}/target/{target}/quicheperf server --cert {quicheperf_dir}/src/cert.crt --key {quicheperf_dir}/src/cert.key -l 192.168.1.3:10000 --mp true &> {testing_dir}/{directory}/h2.log", shell=True)

        client = h1.popen(f"{quicheperf_dir}/target/{target}/quicheperf client -l 192.168.1.2:20000 -c 192.168.1.3:10000 --mp true -d {conf.duration} -b {tp} &> {testing_dir}/{directory}/h1.log", shell=True)

        server_capture = (server, None)
        client_capture = (client, None)
        output_processes.append(server_capture)
        output_processes.append(client_capture)
    else:
        server = h2.popen(f"{quicheperf_dir}/target/{target}/quicheperf server --cert {quicheperf_dir}/src/cert.crt --key {quicheperf_dir}/src/cert.key -l 192.168.1.3:10000 --mp true", stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

        client = h1.popen(f"{quicheperf_dir}/target/{target}/quicheperf client -l 192.168.1.2:20000 -c 192.168.1.3:10000 --mp true -d {conf.duration} -b {tp}", stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    
        server_capture = (server, f"{directory}/h2.log")
        client_capture = (client, f"{directory}/h1.log")
        output_processes.append(server_capture)
        output_processes.append(client_capture)

    # Waiting long enough so that we don't match the re-gathering exactly
    wait(15)
    # Restore interface and IP, waiting for ICE to notice
    ip_storage = iface_up(net, "h1", "h1-eth", directory, ip_storage)
    wait(20)

    # Finished testing
    return output_processes


def quicheperf_path_loss_test(net, directory, conf):
    """
    Testing what happens if we lose a path for more than 30s
    so that the program decides that we no longer can use the path.
    Should result in re-gathering on this path because no connection
    exists anymore.
    """

    h1 = net.get("h1")
    h2 = net.get("h2")

    target = conf.build_target
    tp = conf.throughput
    output_processes = []

    set_conntrack_timeout(net, "nat3", timeout=25)

    if conf.log_level.value > Logging.INFO.value:
        server = h2.popen(f"{quicheperf_dir}/target/{target}/quicheperf server --cert {quicheperf_dir}/src/cert.crt --key {quicheperf_dir}/src/cert.key -l 192.168.1.3:10000 --mp true &> {testing_dir}/{directory}/h2.log", shell=True)

        client = h1.popen(f"{quicheperf_dir}/target/{target}/quicheperf client -l 192.168.1.2:20000 -c 192.168.1.3:10000 --mp true -d {conf.duration} -b {tp} &> {testing_dir}/{directory}/h1.log", shell=True)

        server_capture = (server, None)
        client_capture = (client, None)
        output_processes.append(server_capture)
        output_processes.append(client_capture)
    else:
        server = h2.popen(f"{quicheperf_dir}/target/{target}/quicheperf server --cert {quicheperf_dir}/src/cert.crt --key {quicheperf_dir}/src/cert.key -l 192.168.1.3:10000 --mp true", stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

        client = h1.popen(f"{quicheperf_dir}/target/{target}/quicheperf client -l 192.168.1.2:20000 -c 192.168.1.3:10000 --mp true -d {conf.duration} -b {tp}", stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    
        server_capture = (server, f"{directory}/h2.log")
        client_capture = (client, f"{directory}/h1.log")
        output_processes.append(server_capture)
        output_processes.append(client_capture)

    # Waiting long enough so that at least one path has been found
    # Should be done 5 seconds after start
    wait(7)
    
    # Now lose all packets on the Ethernet path (NAT3)
    nat_to_lose_packets="nat3"
    path_loss(net, f"{nat_to_lose_packets}", f"{nat_to_lose_packets}-local", loss=100)
    path_loss(net, f"{nat_to_lose_packets}", f"{nat_to_lose_packets}-ext", loss=100)

    # Wait for all bindings to timeout
    # See: https://unix.stackexchange.com/questions/524295/how-long-does-conntrack-remember-a-connection
    # Disable the Wi-Fi path as well (but be fair to our implementation and not intervene)
    # with the sending of synchronization frames at second 11
    wait(5)

    # Also lose all packets on the Wi-Fi direct link (Switch 1)
    nat2_to_lose_packets="s1"
    path_loss(net, f"{nat2_to_lose_packets}", f"{nat2_to_lose_packets}-wifi1", loss=100)
    path_loss(net, f"{nat2_to_lose_packets}", f"{nat2_to_lose_packets}-wifi2", loss=100)
    
    # Wait for the next ICE probing    
    wait(19) # Second 31
    
    # Helping the timeout and remove the established path (in case any was established)
    remove_conntrack_entry(net, f"{nat_to_lose_packets}", "-u ASSURED")
    print_nat_table(net, f"{nat_to_lose_packets}", outpath=directory, outfile=f"{nat_to_lose_packets}_temp_nat.log")
    # Then, restore the Ethernet path to be rebuild
    path_loss(net, f"{nat_to_lose_packets}", f"{nat_to_lose_packets}-local", loss=0)
    path_loss(net, f"{nat_to_lose_packets}", f"{nat_to_lose_packets}-ext", loss=0)
    
    # Now, disable the Wi-Fi interface, to show that it is not considered during probing
    # if it is down
    wait(2) # Second 33
    ip_storage = iface_down(net, "h1", "h1-wifi", directory)
    
    # Wait for next probing to re-enable the Wi-Fi path and interface again
    wait(12) # Second 45, 3s into probing
    
    # Enable Wi-Fi path
    # path_loss(net, f"{nat2_to_lose_packets}", f"{nat2_to_lose_packets}-wifi1", loss=0)
    # path_loss(net, f"{nat2_to_lose_packets}", f"{nat2_to_lose_packets}-wifi2", loss=0)
    ip_storage = iface_up(net, "h1", "h1-wifi", directory, ip_storage)
    
    # Now only wait to see that we find the path in the next iteration
    wait(30)
    set_conntrack_timeout(net, f"{nat_to_lose_packets}", timeout=120)

    # Finished testing
    return output_processes

def quicheperf_loss_on_probing(net, directory, conf):
    """
    This test is meant to reproduce an scheduling error when packets are
    lost at the beginning of the ICE probing. This leads to a loss in ICE
    synchronization frames exchanged via QUIC and a freeze in path probing
    """
    
    h1 = net.get("h1")
    h2 = net.get("h2")

    target = conf.build_target
    tp = conf.throughput
    output_processes = []

    set_conntrack_timeout(net, "nat3", timeout=25)

    if conf.log_level.value > Logging.INFO.value:
        server = h2.popen(f"{quicheperf_dir}/target/{target}/quicheperf server --cert {quicheperf_dir}/src/cert.crt --key {quicheperf_dir}/src/cert.key -l 192.168.1.3:10000 --mp true &> {testing_dir}/{directory}/h2.log", shell=True)

        client = h1.popen(f"{quicheperf_dir}/target/{target}/quicheperf client -l 192.168.1.2:20000 -c 192.168.1.3:10000 --mp true -d {conf.duration} -b {tp} &> {testing_dir}/{directory}/h1.log", shell=True)

        server_capture = (server, None)
        client_capture = (client, None)
        output_processes.append(server_capture)
        output_processes.append(client_capture)
    else:
        server = h2.popen(f"{quicheperf_dir}/target/{target}/quicheperf server --cert {quicheperf_dir}/src/cert.crt --key {quicheperf_dir}/src/cert.key -l 192.168.1.3:10000 --mp true", stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

        client = h1.popen(f"{quicheperf_dir}/target/{target}/quicheperf client -l 192.168.1.2:20000 -c 192.168.1.3:10000 --mp true -d {conf.duration} -b {tp}", stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    
        server_capture = (server, f"{directory}/h2.log")
        client_capture = (client, f"{directory}/h1.log")
        output_processes.append(server_capture)
        output_processes.append(client_capture)

    # Waiting long enough so that both paths are found
    # Should be done 5 seconds after the start
    wait(7)
    
    # Now lose all packets on the Ethernet path (NAT3) and enforce migration onto Wi-Fi
    nat_to_lose_packets="nat3"
    path_loss(net, f"{nat_to_lose_packets}", f"{nat_to_lose_packets}-local", loss=100)
    path_loss(net, f"{nat_to_lose_packets}", f"{nat_to_lose_packets}-ext", loss=100)
    
    # Wait until the next gathering iteration starts and kill the sending Wi-Fi interface exactly at
    # that time
    wait(4)

    # Also lose all packets on the Wi-Fi direct link (Switch 1)
    nat2_to_lose_packets="s1"
    path_loss(net, f"{nat2_to_lose_packets}", f"{nat2_to_lose_packets}-wifi1", loss=100)
    path_loss(net, f"{nat2_to_lose_packets}", f"{nat2_to_lose_packets}-wifi2", loss=100)
    
    # Now, all gathering should fail because we are missing an ICE synchronization
    # Wait until path becomes disabled
    wait(15)
    
    # Even after enabling the path, should not be found again
    remove_conntrack_entry(net, f"{nat_to_lose_packets}", "-u ASSURED")
    print_nat_table(net, f"{nat_to_lose_packets}", outpath=directory, outfile=f"{nat_to_lose_packets}_temp_nat.log")
    # Then, restore the Ethernet path to be rebuild
    path_loss(net, f"{nat_to_lose_packets}", f"{nat_to_lose_packets}-local", loss=0)
    path_loss(net, f"{nat_to_lose_packets}", f"{nat_to_lose_packets}-ext", loss=0)
    
    wait(20)

def start_ping_pong(net, directory, conf):
    """
    Starting the WebRTC Ping Pong example which acts as a baseline
    to debug and check what features are missing.
    """

    h1 = net.get("h1")
    h2 = net.get("h2")

    target = conf.build_target

    server = h2.popen(f"{code_dir}/webrtc_unmod/target/{target}/examples/ping_pong -c 192.168.1.2 -p", stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    client = h1.popen(f"{code_dir}/webrtc_unmod/target/{target}/examples/ping_pong -c 192.168.1.3 --controlling -p", stdout=subprocess.PIPE, stdin=subprocess.PIPE)

    wait(20)

    server_capture = (server, f"{directory}/h2.log")
    client_capture = (client, f"{directory}/h1.log")
    captures = [server_capture, client_capture]
    return captures

def start_debug(net, directory, conf):
    """
    Starting the debug session with the CLI enabled to allow
    for manual input.
    """

    CLI(net)

    return []

def quicheperf_real_world(net, directory, conf):
    """
    Starting the actual application we want to test.
    Responsible for starting the application and logging.
    Must return a list of tuple holding (process, logfile)
    which will be terminated by the wrapper. If the logfile
    is 'None' then we expect the application to directly write
    into the logfile and therefore no output is processed by
    the wrapper.
    """

    h1 = net.get("h1")

    target = conf.build_target
    tp = conf.throughput
    output_processes = []

    # print("Executing: {}".format(f"{quicheperf_dir}/target/{target}/quicheperf server --cert {quicheperf_dir}/src/cert.crt --key {quicheperf_dir}/src/cert.key -l 192.168.1.3:10000 --mp true"))

    if conf.log_level.value > Logging.INFO.value:
        # server = h2.popen(f"{quicheperf_dir}/target/{target}/quicheperf server --cert {quicheperf_dir}/src/cert.crt --key {quicheperf_dir}/src/cert.key -l 192.168.1.3:10000 --mp true &> {testing_dir}/{directory}/h2.log", shell=True)

        client = h1.popen(f"{quicheperf_dir}/target/{target}/quicheperf client -l 192.168.1.2:20000 -c 192.168.1.3:10000 --mp true -d {conf.duration} -b {tp} &> {testing_dir}/{directory}/h1.log", shell=True)

        # server_capture = (server, None)
        client_capture = (client, None)
        # output_processes.append(server_capture)
        output_processes.append(client_capture)
    else:
        # server = h2.popen(f"{quicheperf_dir}/target/{target}/quicheperf server --cert {quicheperf_dir}/src/cert.crt --key {quicheperf_dir}/src/cert.key -l 192.168.1.3:10000 --mp true", stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

        client = h1.popen(f"{quicheperf_dir}/target/{target}/quicheperf client -l 192.168.1.2:20000 -c 192.168.1.3:10000 --mp true -d {conf.duration} -b {tp}", stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    
        # server_capture = (server, f"{directory}/h2.log")
        client_capture = (client, f"{directory}/h1.log")
        # output_processes.append(server_capture)
        output_processes.append(client_capture)

    # path_loss(net, "h1", "h1-wifi")
    # wait(20)
    # path_loss(net, "h1", "h1-wifi", loss=0)
    # wait()

    # Finished testing
    return output_processes