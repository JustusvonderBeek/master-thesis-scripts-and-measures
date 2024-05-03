# This class contains the helper functionality to start and perform different
# tests to measure the performance of the current implementation

from config import Tests, Scenarios, Logging, TestConfiguration
from measurement_util import create_new_test_folder, change_rights_test_folder, print_nat_table, wait, terminate
from mininet.cli import CLI
from pathlib import Path

import re, time, os, subprocess

# Some useful information for testing
username = "justus"
code_dir = f"/home/{username}/Documents/Code"
quicheperf_dir = f"{code_dir}/quicheperf-stun"
testing_dir = f"{code_dir}/2024-justus-von-der-beek-supplementary-material"

def start_test(net, conf: TestConfiguration):
    """
    Performing the given test on the given network.
    Configuration:
    - Disable the capturing and output of .pcap files
    - Configure and start the network with a CLI, no tests will be performed
    - Disabling or modifying the level of log output
    - Changing the file permissions after testing to 666
    """

    match conf.test:
        case Tests.QUICHEPERF:
            test_function = _start_quicheperf
        case Tests.PING_PONG:
            test_function = _start_ping_pong
        case Tests.DEBUG:
            test_function = _start_debug
        case _:
            print("No correct test given, exiting...")
            return
        
    _test_wrapper(net, test_function, conf)

def _start_turn_server(net, host):
    """
    Starting the TURN server at the dedicated host.
    Using the 'coturn' implementation.
    Current configuration:
    - no logfile
    - no authentication required
    """

    h = net.get(host)

    # The server is correctly configured, nothing needed to answer simple STUN requests
    # And no login required; prevent creation of logfile under /var/log/turn_*
    cmd = f"/home/justus/Documents/Code/coturn/bin/turnserver -z --log-file stdout"
    process = h.popen(cmd)

    return [(process, None)]


def _start_pcap_capture(net, directory, additional_ifs=None):
    """
    Starting capturing network traffic in pcap files
    for all nodes in the network. This includes hosts and router/NATs
    Switches and other possible capturing points are not included.

    In case additional hosts and interfaces are required, they can
    can be given via the additional_ifs parameter. Expecting a list
    of host names. TODO: Maybe at a later point adding specific 
    interfaces only might be possible, for now its not

    Returns a list of tuples, holding the capture processes together 
    with the filename to which the capture takes place.
    """

    capture_hosts = []
    for host in net.values():
        # Filtering switches and other hosts out
        found = re.search("^(s|c)[0-9]+", f"{host}")
        if found is None:
            # Those hosts which are not to filter
            capture_hosts.append(f"{host}")
    
    if additional_ifs is not None:
        for additional, ifs in additional_ifs:
            capture_hosts.append(additional)

    capture_list = []
    for h in capture_hosts:
        host = net.get(h)
        ifs = host.intfNames()
        ifs_str = " -i ".join(ifs)
        outfile = f"{directory}/{h}.pcap"
        # Capturing all given interfaces but into a single pcap file
        # Allows for differentiation in the analysis
        capture_cmd = f"tshark -i {ifs_str} -w {outfile} -n"
        print(f"Capturing {capture_cmd}")
        host_pcap = host.popen(f"{capture_cmd}")
        capture = (host_pcap, outfile)
        capture_list.append(capture)

    return capture_list

def _stop_pcap_capture(captures, modify_file_perm=False):
    """
    Terminating the pcap packet captures.
    If specified, setting the file permission to allow everyone
    to read and write the file.
    """

    for process, outfile in captures:
        process.terminate()
        
        if outfile is None:
            return
        
        if modify_file_perm and Path(outfile).exists():
            os.chmod(outfile, 0o666)
            print(f"Wrote pcap to '{outfile}'")

def _set_log_level(logging: Logging):
    """
    Setting the log level according to the specified value.
    Changing the RUST_LOG variable in order to be effective
    """

    match logging:
        case Logging.NONE:
            # Do not output anything later on but also allow 
            # only as little output as possible
            os.environ["RUST_LOG"] = "error" 
        case Logging.ERROR:
            os.environ["RUST_LOG"] = "error" 
        case Logging.WARN:
            os.environ["RUST_LOG"] = "warn" 
        case Logging.INFO:
            os.environ["RUST_LOG"] = "info" 
        case Logging.DEBUG:
            os.environ["RUST_LOG"] = "debug" 
        case Logging.TRACE:
            os.environ["RUST_LOG"] = "trace" 
        case _:
            os.environ["RUST_LOG"] = "info" 
    
def _print_all_nat_tables(net, directory):
    """
    Searching for all hosts with 'nat' in the name and
    printing the NAT table to a file 
    """

    for host in net.values():
        # Filtering NATs
        found = re.search("^nat", f"{host}")
        if found is not None:
            print_nat_table(net, f"{host}", directory)


def _terminate_processes(captures):
    """
    Terminating all given processes and writing the output
    (if given) to the included file.
    Expecting a list of tuples holding the process and logfile
    name in the format (process, logfile).
    In case the logfile is 'None' no logfile is written.
    """

    for process, logfile in captures:
        terminate(process, logfile, overwrite=True)


def _test_wrapper(net, test_function, conf: TestConfiguration):
    """
    Starting quicheperf in the given network configuration.
    Logging with the given log level into a newly created
    directory.
    After the test the network is NOT stopped. 
    Must be performed additionally
    """

    net.start()

    test_dir = create_new_test_folder()
    _set_log_level(conf.log_level)

    if conf.enable_turn_server:
        turn_server = _start_turn_server(net, "turn")

    if conf.enable_pcap:
        pcap_captures = _start_pcap_capture(net, test_dir)


    # Allows to capture the earliest packets, otherwise some might miss
    time.sleep(1)

    # Performing the actual test
    processes = test_function(net, test_dir, conf)

    if conf.enable_cli_after_test:
        CLI(net)

    _terminate_processes(processes)

    # Stopping all the captures
    if conf.enable_pcap:
        _stop_pcap_capture(pcap_captures, conf.change_file_permissions)

    if conf.enable_turn_server:
        _stop_pcap_capture(turn_server)

    _print_all_nat_tables(net, test_dir)

    change_rights_test_folder(test_dir)


def _start_quicheperf(net, directory, conf):
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

    # Configure waiting etc. here

    wait()
    wait()
    # Setting the interface down, etc.

    # Finished testing

    return output_processes


def _start_ping_pong(net, directory, conf):
    """
    Starting the WebRTC Ping Pong example which acts as a baseline
    to debug and check what features are missing.
    """

    h1 = net.get("h1")
    h2 = net.get("h2")

    target = conf.build_target

    server = h2.popen(f"{code_dir}/webrtc_unmod/target/{target}/examples/ping_pong -c 192.168.1.2 -p", stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    client = h1.popen(f"{code_dir}/webrtc_unmod/target/{target}/examples/ping_pong -c 192.168.1.3 --controlling -p", stdout=subprocess.PIPE, stdin=subprocess.PIPE)

    server_capture = (server, f"{directory}/h2.log")
    client_capture = (client, f"{directory}/h1.log")
    captures = [server_capture, client_capture]
    return captures

def _start_debug(net, directory, conf):
    """
    Starting the debug session with the CLI enabled to allow
    for manual input.
    """

    CLI(net)

    return []