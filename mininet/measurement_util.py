# This file contains functionality to capture network traffic,
# capture the sslkeylogfiles, terminate processes and 
# store the output to logfiles or to emulate the breakdown 
# of network paths.

from pathlib import Path
from datetime import datetime

import mininet.net as net
import subprocess
import os
import time


def capture_ssl(net, host, outpath=None, outfile=None):
    """Exporting the session SSL keys"""

    h = net.get(host)
    if h is None:
        return
    if outpath is None:
        outpath = f"{host}/"
    Path(outpath).mkdir(parents=True, exist_ok=True)
    file_name = datetime.today().strftime("%d_%m_%H_%M") + "_sslkeys.txt"
    if outfile is None:
        outfile = file_name
    else:
        outfile = outfile + "_" + file_name
    outfile = Path(outpath).joinpath(outfile)
    os.environ["SSLKEYLOGFILE"] = f"{outfile}"

def capture_pcap(net, host, outpath=None, outfile=None):
    """Capturing packets on the specified host"""

    h = net.get(host)
    if h is None:
        return
    if outpath is None:
        outpath = f"{host}/"
    Path(outpath).mkdir(parents=True, exist_ok=True)
    file_name = datetime.today().strftime("%d_%m_%H_%M") + ".pcap"
    if outfile is None:
        outfile = file_name
    else:
        outfile = outfile + "_" + file_name
    outfile = Path(outpath).joinpath(outfile)
    # print(f"Outfile: {outfile}")
    host_pcap = h.popen(f"tcpdump -i any -w {outfile}")

    return host_pcap

def terminate(process, outfile=None):
    """Ending the running 'pcap capturing' process"""

    process.terminate()

    if outfile is not None:
        text, err = process.communicate()
        outfile = outfile + datetime.today().strftime("%d_%m_%H_%M") + ".log"
        with open(outfile, "w") as proc_out:
            proc_out.write(text.decode("utf-8"))
            proc_out.write("\n---------------------\n\n")
            proc_out.write(err.decode("utf-8"))
    

def stop_path(net, host, switch):
    """Disabling the routing / traffic via the given path"""

    print(f"Stopping path from {host}<->{switch}")
    net.configLinkStatus(host, switch, 'down')
    # net.cmd(f"link {host} {switch} down")

def start_path(net, host, switch):
    """Enabling the routing / traffic via the given path"""

    print(f"Starting path from {host}<->{switch}")
    net.configLinkStatus(host, switch, 'up')
    # net.cmd(f"link {host} {switch} up")

def if_down(net, host, iface):
    """Disabling the specified interface on the given host"""

    print(f"Disabling interface {iface} on {host}")
    h = net.get(host)
    h.cmd(f"ip link set dev {iface} down")

def if_up(net, host, iface):
    """Enabling the specified interface on the given host"""

    print(f"Enabling interface {iface} on {host}")
    h = net.get(host)
    h.cmd(f"ip link set dev {iface} up")

def write_new_if_file(local_addr, peer_addr):
    """Writing a new local and remote address into the file that is read by quiche.
    Allows creating a new path mid connection.
    """

    with open("new_socket.txt", "w") as if_file:
        if_file.write(local_addr + "\n")
        if_file.write(peer_addr)