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

    net.cmd(f"link {host} {switch} down")

def start_path(net, host, switch):
    """Enabling the routing / traffic via the given path"""

    net.cmd(f"link {host} {switch} up")
