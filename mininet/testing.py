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
from measurement_util import wait, path_loss, iface_down, iface_up

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

    ip_storage = iface_down(net, "h1", "h1-eth", directory)

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

    # Configure waiting etc. here

    wait()
    # path_loss(net, "h1", "h1-wifi")
    ip_storage = iface_up(net, "h1", "h1-eth", directory, ip_storage)
    wait(20)
    # path_loss(net, "h1", "h1-wifi", loss=0)
    # wait()
    # Setting the interface down, etc.

    # Finished testing

    return output_processes
