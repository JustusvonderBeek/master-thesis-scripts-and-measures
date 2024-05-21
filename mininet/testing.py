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
    wait(15)
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
    wait(12)
    # Restore interface and IP, waiting for ICE to notice
    ip_storage = iface_up(net, "h1", "h1-eth", directory, ip_storage)
    wait(15)

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
    wait(5)
    # Now lose all packets at the NAT
    path_loss(net, "nat3", "nat3-local", loss=100)
    path_loss(net, "nat3", "nat3-ext", loss=100)
    # Wait for all bindings to timeout
    # See: https://unix.stackexchange.com/questions/524295/how-long-does-conntrack-remember-a-connection
    # Modified to 25s for this test with (TODO: Doesn't work at the moment)
    wait(35)
    # Helping the timeout and remove the established path (in case any was established)
    remove_conntrack_entry(net, "nat3", "-u ASSURED")
    print_nat_table(net, "nat3", outpath=directory, outfile="nat3_temp_nat.log")
    # Restore the path and allow for packets to flow
    path_loss(net, "nat3", "nat3-local", loss=0)
    path_loss(net, "nat3", "nat3-ext", loss=0)
    # Give enough time to restart and find the path
    wait(15)
    set_conntrack_timeout(net, "nat3", timeout=120)

    # Finished testing
    return output_processes
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