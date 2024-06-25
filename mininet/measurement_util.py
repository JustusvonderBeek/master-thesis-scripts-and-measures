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
import pwd
import grp

def create_new_test_folder(path=None):
    """Creating a testfolder where all logfiles and pcap are stored in."""

    if path is None:
        path = "mininet_measurements/"

    day_name = path + datetime.today().strftime("%d_%m")
    time_name = datetime.today().strftime("%H_%M")

    username = "justus"
    uid = pwd.getpwnam(username).pw_uid
    gid = grp.getgrnam(username).gr_gid

    iteration = 1
    base_folder = Path(day_name)
    base_folder.mkdir(parents=True, exist_ok=True)
    os.chown(base_folder, uid, gid)
    folder_name = Path(base_folder).joinpath(time_name)
    base_folder_name = folder_name
    while True:
        if Path(folder_name).exists():
            time_folder_name = Path(base_folder_name).stem
            time_folder_name_iter = f"{time_folder_name}_({iteration})"
            time_folder_name_iter = Path(day_name).joinpath(time_folder_name_iter)
            folder_name = time_folder_name_iter
            iteration += 1
        else:
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

    # Get all links in the network
    links = net.links
    # Filter the correct link
    for link in links:
        # Every link has two interfaces, intf1 and intf2
        if iface in f"{link.intf1}":
            # print("Found link: {}: {}".format(link, link.intf1))
            # Doesn't make a difference if we apply loss to the
            # first or second interface
            if loss > 0:
                link.intf1.config(loss=loss)
            else:
                h = net.get(host)
                h.cmd("tc qdisc change dev {} root netem loss {}%".format(iface, loss))
            print("Set loss of link {} to {}%".format(link, loss))
        elif iface in f"{link.intf2}":
            if loss > 0:
                link.intf2.config(loss=loss)
            else:
                h = net.get(host)
                h.cmd("tc qdisc change dev {} root netem loss {}%".format(iface, loss))

            print("Set loss of link {} to {}%".format(link, loss))

    # h = net.get(host)
    # cmd = "tc qdisc add dev {} root netem loss {}%".format(iface, loss)
    # print("Executing: {}% loss on link {}<->{}".format(loss, host, iface))
    # h.cmd(cmd)

def set_conntrack_timeout(net, host, timeout):
    """
    Allowing to set the timeout in seconds after which connections will be forgotten and
    a new connection has to be build.
    """

    h = net.get(host)
    # sudo sysctl -w net.netfilter.nf_conntrack_udp_timeout_stream=30
    # Defaults to 120 for stream (established), 30s not established
    h.cmd("sysctl -w net.netfilter.nf_conntrack_udp_timeout_stream={}".format(timeout))

def remove_conntrack_entry(net, host, filter):
    """
    Removing conntrack entries that match the given filter
    """

    h = net.get(host)
    h.cmd("conntrack -D {}".format(filter))

def parse_ip(cmd_output):
    """Parsing the output of the 'ip a' command. Returns the first found IP."""

    ipv4_addresses = re.findall(r'inet (\d+\.\d+\.\d+\.\d+/\d+)', cmd_output)
    return ipv4_addresses

def store_routes_for_interface(net, host, dir):
    """
    Storing all routes for a given interface which might get lost during the
    interface being set down.
    """

    print(f"Storing routes for host '{host}'")
    h = net.get(host)
    h.cmd(f"ip route save > {dir}/{host}-ip-routes.log")

def restore_routes_for_interface(net, host, dir):
    """
    Expecting a dictionary of (host,iface):routes()
    Restoring the given routes on the given interface.
    """

    print(f"Restoring routes for host '{host}'")
    h = net.get(host)
    h.cmd(f"ip route restore < {dir}/{host}-ip-routes.log")
    router_storage = Path(dir).joinpath(f"{host}-ip-routes.log")
    if router_storage.exists():
        os.remove(router_storage)


def iface_down(net, host, iface, directory, ip_storage=None):
    """Disabling the specified interface on the given host.
    Also removes the IP from the interface and stores it in dictionary
    """

    print(f"Disabling interface {iface} on {host}")
    store_routes_for_interface(net, host, directory)
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

def iface_up(net, host, iface, directory, ip_storage=None):
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

    restore_routes_for_interface(net, host, directory)

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
    
def print_nat_table(net, host, outpath=None, outfile=None):
    """Printing the current state of connection tracking"""
    
    h = net.get(host)
    # Check where the output is going to?
    if outpath is None:
        outpath = "mininet_measurements/unknown/"
        
    if outfile is None:
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
    
def print_routing_table(net, directory):
    """
    Printing the routing current routing table of all hosts in the network.
    """
    
    with open(f"{directory}/routing-tables.log", "w") as logfile:
        for host in net.values():
            found = re.search("^(s|c)[0-9]+", f"{host}")
            if found is None:
                output = host.cmd("route")
                logfile.write(f"Host: {host}\n")
                logfile.write(output)
                logfile.write("------------------\n")


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

def combineHostPcaps(directory):
    """
    Expecting the test directory.
    Combining both host files H1 and H2 into a single pcap file
    stored in the same directory
    """

    outfile = f"{directory}/h1_h2_combined.pcapng"
    subprocess.run(f"mergecap -w {outfile} {directory}/h1.pcap {directory}/h2.pcap", shell=True)
    return outfile

def injectSSLKeysPcap(filename, keyfile, outfile=None):
    """
    Injecting the ssl keylog into the pcap file for easier decryption afterwards
    """

    if outfile is None:
        path = os.path.dirname(filename)
        outfile = os.path.join(path, "tmp.pcap")
        rename = True

    subprocess.run(f"editcap --inject-secrets tls,{keyfile} {filename} {outfile}", shell=True)

    if rename:
        os.remove(filename)
        os.rename(outfile, filename)