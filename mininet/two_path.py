"""
Custom mininet topology for testing path migration.
Creates a topology with two subnets 192.168.1.0/24 (hostA) and 10.0.1.0/24 (hostB)
Both subnets are connected via two paths.
One path is directly connected (simple router, forwarding each request)
One path is abstracted to be "the internet" (router, only allowing one subnet to pass)

   hostA --- router --- hostB
     |------ router ------|

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=migration' from the command line.

To create this topology run:
sudo mn --custom create_quic_topo.py --topo migration (--test pingall)

To visualize the network:

sudo mn --custom create_quic_topo.py --topo <topo-name>
mininet>dump
mininet>links

Paste output here: http://demo.spear.narmox.com/app/?apiurl=demo#!/mininet

To clean everything up again after running experiments use: sudo mn -c
"""

from mininet.topo import Topo
from mininet.node import Node, Switch, OVSController
from mininet.nodelib import NAT
from mininet.net import Mininet
from mininet.cli import CLI
from pathlib import Path
from datetime import datetime

import mininet.net as net
import subprocess
import os
import time

# This setup is inspired by the linuxrouter example: https://github.com/mininet/mininet/blob/master/examples/linuxrouter.py

class LinuxRouter(Node):
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()

class TwoSubnets( Topo ):
    """Creating a two subnets with their own IP addresses"""

    def build(self):
        "Creating custom topo"

        # Adding the router in the middle
        defaultIp = "192.168.1.1/24"
        r1 = self.addNode("router", cls=LinuxRouter, ip=defaultIp)

        # Add the switches (seem to be necessary in mininet)
        s1 = self.addSwitch("s1") # Left subnet
        s2 = self.addSwitch("s2") # Right subnet

        # Adding the links between switches and router (so that the secondary IP is assigned)
        self.addLink(s1, r1, intfName2="router-eth1", params2={"ip" : defaultIp}) # Left subnet
        self.addLink(s2, r1, intfName2="router-eth2", params2={"ip" : "10.0.1.1/24"}) # Right subnet

        # Adding the hosts with default route
        h1 = self.addHost("h1", ip="192.168.1.10/24", defaultRoute="via 192.168.1.1") # Left subnet
        h2 = self.addHost("h2", ip="10.0.1.10/24", defaultRoute="via 10.0.1.1") # Right subnet

        # Linking host to switch
        self.addLink(h1, s1)
        self.addLink(h2, s2)

class TwoConnections( Topo ):
    """
    Two subnets connected via two routers along two different paths. 
    Each host has 2 interfaces with 2 different IP addresses.
    Each interface is connected to a different switch routing packets along one of the two paths.
    """

    def build(self):
        # net = Mininet(topo=self)

        s1 = self.addSwitch("s1") # Left
        s2 = self.addSwitch("s2") # Left
        s3 = self.addSwitch("s3") # Right
        s4 = self.addSwitch("s4") # Right
        
        r1 = self.addHost("r1", ip="192.168.1.1/24")
        # Adding the NAT interface host
        nat = self.addNode("nat", ip="172.16.1.1", cls=NAT, subnet="172.16.1.1/24", inetIntf="nat-eth1", localIntf="nat-eth0")
        # r2 = self.addHost("r2", ip="172.16.1.1/24")

        h1 = self.addHost("h1", ip="192.168.1.10/24", defaultRoute="via 192.168.1.1")
        h2 = self.addHost("h2", ip="10.0.1.10/24", defaultRoute="via 10.0.1.1")

        # Connect the network with links
        # The number behind the parameter (intfName"X") means which of the two hosts/switches we are targeting with this parameter
        self.addLink(h1, s1, intfName1="h1-eth0", delay="15ms")
        self.addLink(h1, s2, intfName1="h1-eth1", delay="5ms")
        self.addLink(h2, s3, intfName1="h2-eth0", delay="15ms")
        self.addLink(h2, s4, intfName1="h2-eth1", delay="5ms")

        self.addLink(s1, r1, intfName2="r1-eth0", params2={"ip" : "192.168.1.1/24"})
        self.addLink(s3, r1, intfName2="r1-eth1", params2={"ip" : "10.0.1.1/24"})
        self.addLink(s2, nat, intfName2="nat-eth0", params2={"ip" : "172.16.1.1/24"})
        self.addLink(s4, nat, intfName2="nat-eth1", params2={"ip" : "172.16.2.1/24"})

        # TODO: Remove r2 and replace with nat
        # self.addLink(nat, s3, intfName2="h1-eth1")
        # self.addLink(nat, s4, intfName2="h2-eth1")
        
        # return net

def configure_routing(net, firewall=False):
    "Creating custom routing logic"

    h1 = net.get("h1")
    h1.setIP("172.16.1.10/24", intf="h1-eth1")
    h1.cmd("ip route add 172.16.2.0/24 via 172.16.1.1 dev h1-eth1")
    h2 = net.get("h2")
    h2.setIP("172.16.2.20/24", intf="h2-eth1")
    h2.cmd("ip route add 172.16.1.0/24 via 172.16.2.1 dev h2-eth1")

    nat = net.get("nat")

    # Setting the NAT rules for R2/NAT
    # See details either 'man iptables' or https://gist.github.com/tomasinouk/eec152019311b09905cd
    # -t table
    # -A <chain> rule (append rule to chain: PREROUTING, before anything happens with the packet)
    # -i <in-interface>
    # -4 IPv4 / -6 IPv6
    # -p the protocol (in our case QUIC ~= UDP)
    # -s <src address> (can be a whole network)
    # -d <dst address> (can be a whole network)
    nat.cmd("iptables -F")
    if firewall:
        nat.cmd("iptables -A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT")
        nat.cmd("iptables -A INPUT -p udp -i nat-eth0 -s 172.16.1.0/24 -d 172.16.2.0/24 -j ACCEPT")
        nat.cmd("iptables -A INPUT -p icmp -i nat-eth0 -s 172.16.1.0/24 -d 172.16.2.0/24 -j ACCEPT")
        nat.cmd("iptables -A INPUT -j DROP")
        
        nat.cmd("iptables -A FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT")
        nat.cmd("iptables -A FORWARD -p udp -i nat-eth0 -s 172.16.1.0/24 -d 172.16.2.0/24 -j ACCEPT")
        nat.cmd("iptables -A FORWARD -p icmp -i nat-eth0 -s 172.16.1.0/24 -d 172.16.2.0/24 -j ACCEPT")
        nat.cmd("iptables -A FORWARD -j DROP")

        nat.cmd("iptables -t nat -A PREROUTING -p udp -i nat-eth0 -d 172.16.2.0/24 -j SNAT --to 172.16.2.1")
    else:
        nat.cmd("ip route add 172.16.1.0/24 via 172.16.1.1 dev nat-eth0")
        nat.cmd("ip route add 172.16.2.0/24 via 172.16.2.1 dev nat-eth1")

    # r2.cmd("ip route add 172.16.1.0/24 via 172.16.2.1")
    net["r1"].cmd("ip route add 10.0.1.0/24 via 192.168.1.1")
    # net["nat"].cmd("ip route add 172.16.1.0/24 via 10.0.1.1")
    

def run_two_conn_topo():
    topo = TwoConnections()
    net = Mininet(topo=topo)
    net.start()
    configure_routing(net)
    CLI(net)
    net.stop()
    exit(0)

def run_ice():
    topo = TwoConnections()
    net = Mininet(topo=topo, controller=OVSController)
    net.start()
    configure_routing(net)

    # Starting the ice agents
    tasks = list()
    client, controller = start_ice_agents(net)
    tasks.append({"proc":client, "name": "h1/ice_"})
    tasks.append({"proc":controller, "name": "h2/ice_"})
    time.sleep(0.5)
    # Processes require the enter key to start
    client.communicate(input=b"\n")
    controller.communicate(input=b"\n")
    time.sleep(5)
    # CLI(net)
    for task in tasks:
        terminate(task["proc"], task["name"])

    net.stop()
    exit(0)

def run_quicheperf():
    topo = TwoConnections()
    net = Mininet(topo=topo, controller = OVSController)
    net.start()
    configure_routing(net)

    procs = list()
    capture_ssl(net, "h2")
    cap = capture_pcap(net, "h2")
    cap1 = capture_pcap(net, "h1")
    procs.append({"proc" : cap, "name" : None })
    procs.append({"proc" : cap1, "name" : None })
    # This is required to be able to capture the handshake and the initial packets of the connection
    time.sleep(0.5)
    server = start_server(net)
    procs.append({"proc" : server, "name" : "h2"})
    client = start_client(net)
    procs.append({"proc" : client, "name" : "h1"})
    CLI(net)
    for proc in procs:
        if proc["name"] is not None:
            terminate(proc["proc"], proc["name"] + "/")
        else:
            terminate(proc["proc"])
    
    net.stop()
    exit(0)

def start_ice_agents(net):
    """Starting the client & server on a specific host"""

    h1 = net.get("h1")
    h2 = net.get("h2")

    client = h1.popen(f"../webrtc/target/debug/examples/ping_pong -s 192.168.1.10 --controlling", stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    controller = h2.popen(f"../webrtc/target/debug/examples/ping_pong -s 10.0.1.10", stdout=subprocess.PIPE, stdin=subprocess.PIPE)

    return client, controller

def start_client(net):
    """Starting the quicheperf client"""

    h1 = net.get("h1")
    # Path is .../Code/..supplementary-material
    Path("h1").mkdir(parents=True, exist_ok=True)
    os.environ["RUST_LOG"] = "debug"
    duration = "10"
    bitrate = "1MB"
    scheduler = "round-robin"
    print(f"Duration: {duration}s , Bitrate {bitrate}")
    client = h1.popen(f"../quicheperf/target/release/quicheperf client -c 10.0.1.10:443 -c 172.168.2.20:443 -l 192.168.1.10:0 -l 172.16.1.10:0 --mp true --scheduler {scheduler} --duration {duration} --bitrate {bitrate}", stdout=subprocess.PIPE)
    
    return client

def start_server(net):
    """Starting the quicheperf server"""

    h2 = net.get("h2")
    Path("h2").mkdir(parents=True, exist_ok=True)
    os.environ["RUST_LOG"] = "debug"
    scheduler = "round-robin"
    server = h2.popen(f"../quicheperf/target/release/quicheperf server -l 10.0.1.10:443 -l 172.16.2.20:443 --mp true --scheduler {scheduler} --cert ../quicheperf/src/cert.crt --key ../quicheperf/src/cert.key", stdout=subprocess.PIPE)

    return server

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

# TODO: Create mobility with: https://github.com/mininet/mininet/blob/master/examples/mobility.py
class HostMobility( Topo ):
    """Creating a host and a server that is mobile"""

    def build(self):

        defaultIp = "192.168.1.1/24"

        # TODO:

# TODO: Mobility not yet ready
topos = { 'migration': ( lambda: TwoSubnets() ), 'two_conns' : (lambda: run_quicheperf()), 'ice' : (lambda: run_ice()),  'mobility(todo)' : (lambda: HostMobility()) }

if __name__ == "__main__":
    run_two_conn_topo()