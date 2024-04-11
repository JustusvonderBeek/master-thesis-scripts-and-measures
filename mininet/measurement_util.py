# This file contains functionality to capture network traffic,
# capture the sslkeylogfiles, terminate processes and 
# store the output to logfiles or to emulate the breakdown 
# of network paths.

from pathlib import Path
from datetime import datetime

import mininet.net as net
import subprocess, select
import os
import time
import re


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

    return host_pcap, outfile

def terminate(process, outfile=None, file_perm=None, terminate=True, overwrite=False):
    """Ending the running 'pcap capturing' process"""

    if terminate:
        process.terminate()

    if outfile is not None:
        text, err = process.communicate()
        outfile = outfile + datetime.today().strftime("%d_%m_%H_%M") + ".log"
        if overwrite:
            with open(outfile, "w") as proc_out:
                proc_out.write(text.decode("utf-8"))
                proc_out.write("\n---------------------\n\n")
                proc_out.write(err.decode("utf-8"))
        else:
            with open(outfile, "a") as proc_out:
                proc_out.write(text.decode("utf-8"))
                proc_out.write("\n---------------------\n\n")
                proc_out.write(err.decode("utf-8"))
            
            os.chmod(outfile, 0o666)
            print("Wrote logfile to: '{}'".format(outfile))
    
    if file_perm is not None:
        # Change the file access write
        os.chmod(file_perm, 0o666)


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

def path_loss(net, host, iface, loss=100):
    """Applying the given loss rate to the given interface on the host specified"""

    h = net.get(host)
    cmd = "tc qdisc add dev {} root netem loss {}%".format(iface, loss)
    print("Executing: {}".format(cmd))
    h.cmd(cmd)

def parse_ip(cmd_output):
    """Parsing the output of the 'ip a' command. Returns the first found IP."""

    ipv4_addresses = re.findall(r'inet (\d+\.\d+\.\d+\.\d+/\d+)', cmd_output)
    return ipv4_addresses

def if_down(net, host, iface, ip_storage=None):
    """Disabling the specified interface on the given host.
    Also removes the IP from the interface and stores it in dictionary
    """

    print(f"Disabling interface {iface} on {host}")
    h = net.get(host)
    output = h.cmd(f"ip a s {iface}")
    ips = parse_ip(output)
    h.cmd(f"ip link set dev {iface} down")
    h.cmd(f"ip addr flush dev {iface}")
    
    if ip_storage is None:
        ip_storage = {(host, iface): list()}
        
    for ip in ips:
        ip_storage[(host,iface)].append(ip)

    # print(ip_storage)
    return ip_storage

def if_up(net, host, iface, ip_storage=None):
    """Enabling the specified interface on the given host"""

    print(f"Enabling interface {iface} on {host}")
    h = net.get(host)
    h.cmd(f"ip link set dev {iface} up")
    
    if ip_storage is not None:
        ips = ip_storage[(host, iface)]
        for ip in ips:
            # print(f"Executing: ip addr add {ip} dev {iface}")
            h.cmd(f"ip addr add {ip} dev {iface}")

        ip_storage[(host, iface)] = list()

    return ip_storage

def set_default_route(net, host, gateway, iface):
    """Setting the default route of a host via a specific gateway."""

    h = net.get(host)
    cmd = f"ip route add default via {gateway} dev {iface}"
    # print(f"Executing: {cmd}")
    h.cmd(cmd)

def write_new_if_file(local_addr, peer_addr):
    """Writing a new local and remote address into the file that is read by quiche.
    Allows creating a new path mid connection.
    """

    with open("mininet/new_socket.txt", "w") as if_file:
        if_file.write(local_addr + "\n")
        if_file.write(peer_addr)

def write_new_ice_cand_file(local_addr):
    """
    Writing the given address into the specified file which leads to quiche sending this information to the other end.
    """

    with open("mininet/ice_addrs.txt", "w") as addr_file:
        addr_file.write(local_addr + "\n")