# This class contains the helper functionality to start and perform different
# tests to measure the performance of the current implementation

from config import Tests, Scenarios, Logging, TestConfiguration
from measurement_util import create_new_test_folder, change_rights_test_folder, print_nat_table, print_routing_table, terminate, path_loss, combineHostPcaps, injectSSLKeysPcap
from testing import quicheperf, quicheperf_if_test, quicheperf_if_init_test, quicheperf_path_loss_test, start_ping_pong, start_debug, quicheperf_real_world
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
            test_function = quicheperf
        case Tests.PING_PONG:
            test_function = start_ping_pong
        case Tests.DEBUG:
            test_function = start_debug
        case Tests.QUICHEPERF_IF_INIT:
            test_function = quicheperf_if_init_test
        case Tests.QUICHEPERF_IF:
            test_function = quicheperf_if_test
        case Tests.QUICHEPERF_LOSS:
            test_function = quicheperf_path_loss_test
        case Tests.REAL_WORLD:
            test_function = quicheperf_real_world
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
    cmd = f"{code_dir}/coturn/bin/turnserver -z --log-file stdout"
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
    
    # if additional_ifs is not None:
    #     for additional, ifs in additional_ifs:
    #         capture_hosts.append(additional)

    capture_list = []
    for h in capture_hosts:
        host = net.get(h)
        ifs = host.intfNames()
        if additional_ifs is not None and "h" in f"{host}":
            ifs += additional_ifs
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

def _print_success(directory):
    """
    Checking the given logfile and printing if the testing was successful or not
    """

    logfile_path = Path(directory).joinpath("h1.log")
    if not Path(logfile_path).exists:
        print("Logfile to check success not found")
        return
    with open(logfile_path, "r") as logfile:
        content = logfile.readlines()
        findings = re.findall("NominatedPair:", content)
        print(findings)
        # TODO: Introduce more checks depending on the test and allow for
        # custom success scenarios
        if len(findings) > 2:
            print("Test was successful")

def _enable_log_sslkey(directory):
    """
    Enabling the logging of SSL keys into the given
    working directory
    """

    os.environ["SSLKEYLOGFILE"] = f"{directory}/sslkey.log"

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
        pcap_captures = _start_pcap_capture(net, test_dir, ["lo"])

    if conf.log_sslkeys:
        _enable_log_sslkey(test_dir)

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
    print_routing_table(net, test_dir)

    change_rights_test_folder(test_dir)

    if conf.combine_pcaps:
        combinedPcap = combineHostPcaps(test_dir)
    if conf.log_sslkeys and conf.combine_pcaps:
        injectSSLKeysPcap(combinedPcap, f"{test_dir}/sslkey.log")