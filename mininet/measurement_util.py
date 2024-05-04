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


def create_new_test_folder(path=None):
    """Creating a testfolder where all logfiles and pcap are stored in."""

    if path is None:
        path = "mininet_measurements/"

    folder_name = path + datetime.today().strftime("%d_%m_%H_%M")
    iteration = 1
    iteration_fn = folder_name
    while True:
        if Path(iteration_fn).exists():
            iteration_fn = f"{folder_name}_({iteration})"
            iteration += 1
        else:
            folder_name = iteration_fn
            break

    Path(folder_name).mkdir(parents=True, exist_ok=False)
    
    return folder_name

def change_rights_test_folder(path):
    """Setting the rights of the test folder so that everyone can delete the folder."""
    
    if path is None:
        return
    
    # Change the file access write
    os.chmod(path, 0o777)

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

def capture_pcap(net, host, interfaces=None, outpath=None, outfile=None):
    """Capturing packets on the specified host. 
    Interfaces can be specified in a list of strings.: ["eth0", "eth1"]
    """

    h = net.get(host)
    if h is None:
        return
    if outpath is None:
        outpath = f"{host}/"
    Path(outpath).mkdir(parents=True, exist_ok=True)
    file_name = f"{host}.pcap"
    if outfile is None:
        outfile = file_name
    else:
        outfile = outfile + "_" + file_name
    outfile = Path(outpath).joinpath(outfile)
    # print(f"Outfile: {outfile}")
    # host_pcap = h.popen(f"tcpdump -i any -w {outfile}")
    listen_interfaces = "-i any"
    if interfaces is not None:
        listen_interfaces = ""
        for iface in interfaces:
            listen_interfaces += f"-i {iface} "
    
    cmd = f"tshark {listen_interfaces} -w {outfile}"
    print(f"Capturing: {cmd}")
    host_pcap = h.popen(f"tshark {listen_interfaces} -w {outfile} -n")

    return host_pcap, outfile

def terminate(process, outfile=None, file_perm=None, terminate=True, overwrite=False):
    """Ending the running 'pcap capturing' process"""

    if terminate:
        process.terminate()

    if outfile is not None:
        text, err = process.communicate()
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
        
def wait(sleep=5):
    """Pausing the executing thread for *time* seconds"""
    
    print(f"Waiting for {sleep}s...")
    time.sleep(sleep)
    
def print_nat_table(net, host, outpath=None):
    """Printing the current state of connection tracking"""
    
    h = net.get(host)
    # Check where the output is going to?
    if outpath is None:
        outpath = "mininet_measurements/unknown/"
        
    outfile = f"{host}_nat.log"
    outfile = Path(outpath).joinpath(outfile)
    
    output = h.cmd("conntrack -L")
    nat_output = h.cmd("conntrack -L -j")
    
    # print(output)
    with open(outfile, "w") as out:
        out.write(output)
        out.write("------------\n")
        out.write(nat_output)
        
        
    print(f"Wrote NAT table state of host {host} to '{outfile}'")
    
def delete_ext_conntrack_entry(net, host, ext, itn, repetition=0.1):
    """
    Executing a task in a loop which scans and deletes all external
    NAT table entries to enable connections on the internet path.
    """
    
    h = net.get(host)
    
    while True:
        # This might help, but we still have the problem that then internal connection
        # is mapped to the incorrect external port and will eventually fail, therefore
        # this mapping must be deleted as well
        h.cmd(f"conntrack --delete --orig-src {ext} --proto udp --status UNREPLIED")
        # This will also delete correct connection that are trying to build
        # so we need a more clever method here
        h.cmd(f"conntrack --delete --orig-src {itn} --proto udp --status UNREPLIED")
        time.sleep(repetition)