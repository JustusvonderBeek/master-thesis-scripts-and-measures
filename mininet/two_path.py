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
from mininet.node import Node, Switch
from mininet.nodelib import NAT
from mininet.net import Mininet
from mininet.cli import CLI
import mininet.net as net

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
        r2 = self.addHost("r2", ip="172.16.1.1/24")

        h1 = self.addHost("h1", ip="192.168.1.10/24", defaultRoute="via 192.168.1.1")
        h2 = self.addHost("h2", ip="10.0.1.10/24", defaultRoute="via 10.0.1.1")

        # Adding the NAT interface host
        nat = self.addNode("nat", cls=NAT, subnet="172.16.1.1/24", inetIntf="nat-eth0", localIntf="nat-eth1")

        # Connect the network with links
        # The number behind the parameter (intfName"X") means which of the two hosts/switches we are targeting with this parameter
        self.addLink(h1, s1, intfName1="h1-eth0")
        self.addLink(h1, s2, intfName1="h1-eth1")
        self.addLink(h2, s3, intfName1="h2-eth0")
        self.addLink(h2, s4, intfName1="h2-eth1")

        self.addLink(s1, r1, intfName2="r1-eth0", params2={"ip" : "192.168.1.1/24"})
        self.addLink(s3, r1, intfName2="r1-eth1", params2={"ip" : "10.0.1.1/24"})
        self.addLink(s2, r2, intfName2="r2-eth0", params2={"ip" : "172.16.1.1/24"})
        self.addLink(s4, r2, intfName2="r2-eth1", params2={"ip" : "172.16.2.1/24"})

        # TODO: Remove r2 and replace with nat
        self.addLink(nat, s3, intfName2="h1-eth1")
        self.addLink(nat, s4, intfName2="h2-eth1")
        
        # return net

def configure_routing(net):
    "Creating custom routing logic"

    h1 = net.get("h1")
    h1.setIP("172.16.1.10/24", intf="h1-eth1")
    h2 = net.get("h2")
    h2.setIP("172.16.2.20/24", intf="h2-eth1")
    h2.cmd("ip route add 172.16.1.0/24 via 172.16.2.1 dev h2-eth1")

    r2 = net.get("r2")
    # r2.cmd("ip route add 172.16.1.0/24 via 172.16.2.1")
    net["r1"].cmd("ip route add 10.0.1.0/24 via 192.168.1.1")
    net["r2"].cmd("ip route add 192.168.1.0/24 via 10.0.1.1")
    

def run_two_conn_topo():
    topo = TwoConnections()
    net = Mininet(topo=topo)
    net.start()
    configure_routing(net)
    CLI(net)
    net.stop()
    exit(0)

# TODO: Create mobility with: https://github.com/mininet/mininet/blob/master/examples/mobility.py
class HostMobility( Topo ):
    """Creating a host and a server that is mobile"""

    def build(self):

        defaultIp = "192.168.1.1/24"

        # TODO:

# TODO: Mobility not yet ready
topos = { 'migration': ( lambda: TwoSubnets() ), 'two_conns' : (lambda: run_two_conn_topo()),  'mobility(todo)' : (lambda: HostMobility()) }

if __name__ == "__main__":
    run_two_conn_topo()