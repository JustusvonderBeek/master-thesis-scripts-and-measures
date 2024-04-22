# This file includes the topologies for our mininet environment testing
# 
# TwoSubnets:
# Creates a topology with two subnets 192.168.1.0/24 (hostA) and 10.0.1.0/24 (hostB)
# Both subnets are connected via a single paths.
# This path is directly connected (simple router, forwarding each request)
# 
# hostA --- router --- hostB
#
#
# TwoConnections:
# Creates a topology with two subnets 192.168.1.0/24 + 172.16.1.0 (hostA) and 10.0.1.0/24 + 172.16.2.0 (hostB)
# Both are connected via two paths.
# One path is directly connected via the first router, without any firewall or blocking
# One path is abstracted to be "the internet" (router, only allowing one subnet to pass)
# 
# hostA --- router --- hostB
#   |------ router ------|
#
#

from mininet.topo import Topo
from mininet.node import Node, Switch, OVSController
from mininet.nodelib import NAT

import mininet.net as net


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
        """
        This function configures the routing tables and firewalls of the two paths topology
        """

        h1 = net.get("h1")
        h1.setIP("172.16.1.10/24", intf="h1-eth1")
        h1.cmd("ip route add 172.16.2.0/24 via 172.16.1.1 dev h1-eth1")
        h2 = net.get("h2")
        h2.setIP("172.16.2.20/24", intf="h2-eth1")
        h2.cmd("ip route add 172.16.1.0/24 via 172.16.2.1 dev h2-eth1")

        nat = net.get("nat")
        r1 = net.get("r1")

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

        # if internet:
            # print("Adding NAT to network")
            # # The nat for host 1 (using the 10.100.0 subnet)
            # inat1 = net.addHost("inat1", cls=NAT, ip="10.100.0.1", subnet="10.100.0.0/24", inetIntf="inat1--eth1", localIntf="inat1-eth0")
            # sInat1 = net.addSwitch("sInat1")
            # net.addLink(sInat1, "h1")
            # net.addLink(inat1, sInat1)

            # inat2 = net.addHost("inat2", cls=NAT, ip="192.168.100.1", subnet="192.168.100.0/24", inetIntf="inat2--eth1", localIntf="inat2-eth0")
            # sInat2 = net.addSwitch("sInat2")
            # net.addLink(sInat2, "h2")
            # net.addLink(inat2, sInat2)

            # # Configure the routing etc.
            # inat1 = net.get("inat1")
            # inat1.cmd('sysctl net.ipv4.ip_forward=1')
            # inat1.cmd('iptables -t nat -A POSTROUTING -o {} -j MASQUERADE'.format("inat1-eth1"))

            # h1.cmd("ip route flush table all")
            # h1.cmd("ip route add default via 192.168.100.1 dev h1-eth2")

        # r2.cmd("ip route add 172.16.1.0/24 via 172.16.2.1")
        net["r1"].cmd("ip route add 10.0.1.0/24 via 192.168.1.1")
        # net["nat"].cmd("ip route add 172.16.1.0/24 via 10.0.1.1")

class TwoConnectionWithInternet(Topo):
    def build(self):
        """Building a topology with 2 connection between the hosts and additionally internet access"""

        s1 = self.addSwitch("s1") # Left
        s2 = self.addSwitch("s2") # Left
        s3 = self.addSwitch("s3") # Left
        s4 = self.addSwitch("s4") # Right
        s5 = self.addSwitch("s5") # Right
        s6 = self.addSwitch("s6") # Right

        routerWithoutNat = self.addHost("noNAT", ip="192.168.100.1/24")

        # Adding the NAT interface host
        routerWithNAT = self.addNode("withNAT", ip="172.16.100.1/24", cls=NAT, subnet="172.16.100.0/24", localIntf="withNAT-eth0", inetIntf="withNAT-eth1")
        # inetNATh1 = self.addNode("inetNATh1", ip="10.0.100.1", cls=NAT, subnet="10.0.100.1/24", localIntf="inetNATh1-eth0", inetIntf="inetNATh1-eth1")
        # inetNATh2 = self.addHost("inetNATh2", ip="10.0.101.1", cls=NAT, subnet="10.0.101.1/24", localIntf="inetNATh2-eth0", inetIntf="inetNATh2-eth1")

        # Adding our two hosts
        h1 = self.addHost("h1", ip="192.168.100.10/24")
        h2 = self.addHost("h2", ip="100.0.200.20/24")

        # Connect the network with links
        # The number behind the parameter (intfName"X") means which of the two hosts/switches we are targeting with this parameter
        self.addLink(h1, s1, intfName1="h1-eth0", delay="15ms")
        self.addLink(h1, s2, intfName1="h1-eth1", delay="5ms")
        self.addLink(h1, s3, intfName1="h1-eth2", delay="5ms")
        self.addLink(h2, s4, intfName1="h2-eth0", delay="15ms")
        self.addLink(h2, s5, intfName1="h2-eth1", delay="5ms")
        self.addLink(h2, s6, intfName1="h2-eth2", delay="5ms")

        self.addLink(s1, routerWithoutNat, intfName2="noNAT-eth0", params2={"ip" : "192.168.100.1/24"})
        self.addLink(s4, routerWithoutNat, intfName2="noNAT-eth1", params2={"ip" : "100.0.200.1/24"})
        self.addLink(s2, routerWithNAT, intfName2="withNAT-eth0", params2={"ip" : "172.16.100.1/24"})
        self.addLink(s5, routerWithNAT, intfName2="withNAT-eth1", params2={"ip" : "200.0.100.1/24"})
        # self.addLink(s3, inetNATh1, intfName2="inetNATh1-eth0", params2={"ip" : "10.0.100.1/24"})
        # self.addLink(s6, inetNATh2, intfName2="inetNATh2-eth0", params2={"ip" : "10.0.101.1/24"})

    def configure_routing(net):
        """Configure the routing to enable internet"""
        
        # Enable sending data via the first and second interface
        h1 = net.get("h1")
        h1.setIP("1.20.30.10/28", intf="h1-eth2")
        h1.setIP("172.16.100.10/24", intf="h1-eth1")
        h1.cmd("ip route add 100.0.200.0/24 via 192.168.100.1 dev h1-eth0")
        h1.cmd("ip route add 200.0.100.0/24 via 172.16.100.1 dev h1-eth1")
        
        h2 = net.get("h2")
        h2.setIP("2.40.60.20/27", intf="h2-eth2")
        h2.setIP("200.0.100.20/24", intf="h2-eth1")
        # h2.cmd("ip route add 192.168.100.0/24 via 100.0.200.1 dev h2-eth0")
        # h2.cmd("ip route add 172.16.100.0/24 via 200.0.100.1 dev h2-eth1")

        # Allow easy forwarding on the router without NAT
        routerWithoutNat = net.get("noNAT")
        routerWithoutNat.cmd("iptables -t nat -A POSTROUTING -o {} -j MASQUERADE".format("noNAT-eth1"))
        # The "no" NAT rule to establish a connection
        routerWithoutNat.cmd("iptables -t nat -A PREROUTING -d 100.0.200.1 -p tcp -j DNAT --to-destination 192.168.100.10")
        routerWithoutNat.cmd('sysctl net.ipv4.ip_forward=1')

        routerWithNat = net.get("withNAT")
        routerWithNat.cmd("iptables -t nat -A POSTROUTING -o {} -j MASQUERADE".format("withNAT-eth1"))
        routerWithNat.cmd("sysctl net.ipv4.ip_forward=1")

    def configure_firewall(net):
        """Configuration of the firewall on the NAT host"""

        routerWithNAT = net.get("withNAT")

        routerWithNAT.cmd("iptables -F")
        routerWithNAT.cmd("iptables -A FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT")
        # routerWithNAT.cmd("iptables -A FORWARD -i noNAT-eth1 -p tcp -j ACCEPT")
        # routerWithNAT.cmd("iptables -A FORWARD -i noNAT-eth1 -p udp -j ACCEPT")
        routerWithNAT.cmd("iptables -A FORWARD -j DROP")
        
        routerWithNAT.cmd("iptables -t nat -A POSTROUTING -o {} -j MASQUERADE".format("withNAT-eth1"))

    def add_internet(net):
        """Configure internet access for the clients"""
        
        h1 = net.get("h1")
        h2 = net.get("h2")

        # Configure the NAT and Internet access
        # Found this script online: https://gist.github.com/lantz/5640610
        inetNATh1 = net.addNAT(name="inetNATh1", ip="1.20.30.1/28", inetIntf="wlp2s0", localIntf="inetNATh1-eth0")
        net.addLink("s3", inetNATh1, params2={"ip" : "1.20.30.1/28"})

        inetNATh2 = net.addNAT(name="inetNATh2", ip="2.40.60.1/27", inetIntf="wlp2s0", localIntf="inetNATh2-eth0")
        net.addLink("s6", inetNATh2, params2={"ip" : "2.40.60.1/27"})
        net.addLink(inetNATh1, inetNATh2, intfName="inetNATh1-eth2", intfName2="inetNATh2-eth2", params1={"ip":"1.20.50.10/24"}, params2={"ip":"1.20.50.20/24"})
        h1.cmd("ip route add default via 1.20.30.1 dev h1-eth2")
        h2.cmd("ip route add default via 2.40.60.1 dev h2-eth2")

        inat1 = net.get("inetNATh1")
        inat1.cmd('iptables -t nat -A POSTROUTING -o {} -j MASQUERADE'.format("wlp2s0"))
        inat1.cmd('sysctl net.ipv4.ip_forward=1')

        inat2 = net.get("inetNATh2")
        inat2.cmd('iptables -t nat -A POSTROUTING -o {} -j MASQUERADE'.format("wlp2s0"))
        inat2.cmd('sysctl net.ipv4.ip_forward=1')

        inat1.cmd("ip route add default via 131.159.196.38 dev wlp2s0")
        inat1.cmd("ip route add 2.40.60.0/24 via 1.20.50.20 dev inetNATh1-eth2")
        inat2.cmd("ip route add default via 131.159.196.38 dev wlp2s0")
        inat2.cmd("ip route add 1.20.30.0/24 via 1.20.50.10 dev inetNATh2-eth2")

class DirectAndInternet(Topo):
    """A topology where two hosts are directly connected 
    emulating a wireless network and have access to the internet via
    a second interface (cellular). 
    
    h1 ------ Internet ------- h2
     |----- Local Network -----|

    """
    
    def build(self):
        """Creating the class topology"""

        s1 = self.addSwitch("s1") # Internet H1
        s2 = self.addSwitch("s2") # Internet H2
        s3 = self.addSwitch("s3") # nat1 <-> nat2 + TURN

        # Adding our two hosts
        h1 = self.addHost("h1", ip="192.168.1.2/24")
        h2 = self.addHost("h2", ip="192.168.1.3/24")
        turn = self.addHost("turn", ip="1.20.30.10/28")

        # Adding the link between the hosts
        self.addLink(h1, h2, intfName1="h1-wifi", intfName2="h2-wifi", delay="10ms")
        # Adding the link into the internet
        self.addLink(h1, s1, intfName1="h1-cellular", params1={"ip":"1.20.30.2/28"}, delay="30ms")
        self.addLink(h2, s2, intfName1="h2-cellular", params1={"ip":"2.40.60.3/28"}, delay="30ms")

    def add_directlink(net):
        """Instead of adding a internet link which needs to be discovered by ICE, add a direct link
        for testing
        """

        r1 = net.addHost("r1")

        net.addLink("s1", "r1", params2={"ip":"1.20.30.1/28"})
        net.addLink("s2", "r1", params2={"ip":"2.40.60.1/28"})

        h1 = net.get("h1")
        h1.cmd("ip route add 2.40.60.0/28 via 1.20.30.1 dev h1-cellular")
        h2 = net.get("h2")
        h2.cmd("ip route add 1.20.30.0/28 via 2.40.60.1 dev h2-cellular")
        # r1 = net.get("r1")
        # r1.cmd("ip route add 2.40.60.0/28 ")


    def add_internet(net):
        """
        Adding the blue part in the schematic. Connecting both devices to the internet
        and to each other.
        """

        internet = False

        # Adding the internet links
        inetNATh1 = net.addNAT(name="natH1", ip="1.20.30.1/28", inetIntf="enp5s0", localIntf="natH1-eth0")
        net.addLink("s1", inetNATh1, params2={"ip" : "1.20.30.1/28"})
        net.addLink(inetNATh1, "s3", params1={"ip" : "1.20.50.10/24"})

        inetNATh2 = net.addNAT(name="natH2", ip="2.40.60.1/28", inetIntf="enp5s0", localIntf="natH2-eth0")
        net.addLink("s2", inetNATh2, params2={"ip" : "2.40.60.1/28"})
        net.addLink(inetNATh2, "s3", params2={"ip" : "1.20.50.20/24"})
        # Connect the "internet"
        net.addLink("turn", "s3", intfName1="turn-eth1", params1={"ip":"1.20.50.30/24"}, delay="1ms")

        # net.addLink(inetNATh1, inetNATh2, intfName="natH1-eth2", intfName2="natH2-eth2", params1={"ip":"1.20.50.10/24"}, params2={"ip":"1.20.50.20/24"}, delay="30ms")

        h1 = net.get("h1")
        h2 = net.get("h2")
        h1.cmd("ip route add default via 1.20.30.1 dev h1-cellular")
        h2.cmd("ip route add default via 2.40.60.1 dev h2-cellular")
        
        nath1 = net.get("natH1")
        nath1.cmd('iptables -t nat -A POSTROUTING -o {} -j MASQUERADE'.format("enp5s0"))
        nath1.cmd('sysctl net.ipv4.ip_forward=1')

        nath2 = net.get("natH2")
        nath2.cmd('iptables -t nat -A POSTROUTING -o {} -j MASQUERADE'.format("enp5s0"))
        nath2.cmd('sysctl net.ipv4.ip_forward=1')

        # Add some toggle to specify if we need internet or not
        # and disable it in case we don't have it to allow for offline testing
        networkIP = "131.159.196.38"
        wifiIf = "wlp0s20f3"
        if internet:
            nath1.cmd(f"ip route add default via {networkIP} dev {wifiIf}")
            nath2.cmd(f"ip route add default via {networkIP} dev {wifiIf}")
        # Emulate the internet connection via a direct conn between the two nat hosts
        nath1.cmd("ip route add 2.40.60.0/24 via 1.20.50.20 dev natH1-eth2")
        nath2.cmd("ip route add 1.20.30.0/24 via 1.20.50.10 dev natH2-eth2")


class DirectAndInternetAndTURN(Topo):

    def build(self):
        """Building the same topology as the DirectAndInternet but including a TURN server
        at the internet location
        
        The internet path includes a TURN server
        
        R1-------------------------R2
        |           TURN           | 
        |              |           |
        h1 ------ Internet ------- h2
        |----- Local Network ------|
        
        """

        s1 = self.addSwitch("s1") # Directlink
        s2 = self.addSwitch("s2") # H1 <-> Nat1
        s3 = self.addSwitch("s3") # Nat1 <-> Nat2
        s4 = self.addSwitch("s4") # Nat2 <-> H2
        # s5 = self.addSwitch("s5") # Nat1 <-> Nat2 without Firewall/NAT
        
        # Adding our two hosts
        h1 = self.addHost("h1", ip="192.168.1.2/24")
        # h1 = self.addHost("h1", ip="1.20.30.2/28")
        h2 = self.addHost("h2", ip="192.168.1.3/24")
        # h2 = self.addHost("h2", ip="2.40.60.3/28")
        turn = self.addHost("turn", ip="1.20.50.100/24")
        nat1 = self.addHost("nat1", ip="1.20.30.1/28")
        nat2 = self.addHost("nat2", ip="2.40.60.1/28")
        nat3 = self.addNode("nat3", cls=LinuxRouter, ip="172.16.1.1/24")
        
        # Adding the link between the hosts
        self.addLink(h1, s1, intfName1="h1-wifi", intfName2="s1-wifi1", params1={"ip":"192.168.1.2/24"}, delay="2ms")
        self.addLink(h2, s1, intfName1="h2-wifi", intfName2="s1-wifi2", params1={"ip":"192.168.1.3/24"}, delay="2ms")
        
        # Adding the link into the internet
        self.addLink(h1, s2, intfName1="h1-cellular", params1={"ip":"1.20.30.2/28"},  delay="2ms")
        self.addLink(h2, s4, intfName1="h2-cellular", params1={"ip":"2.40.60.3/28"}, delay="2ms")
        
        # Connect the hosts with the nats
        self.addLink(s2, nat1, intfName2="nat1-local", params2={"ip":"1.20.30.1/28"}, delay="3ms")
        self.addLink(s4, nat2, intfName2="nat2-local", params2={"ip":"2.40.60.1/28"}, delay="3ms")

        # Connect the internet / routes with each other        
        self.addLink(nat1, s3, intfName1="nat1-ext", params1={"ip":"1.20.50.10/24"}, delay="3ms")
        self.addLink(nat2, s3, intfName1="nat2-ext", params1={"ip":"1.20.50.20/24"}, delay="3ms")
        # Connect the turn server with the "internet"
        self.addLink(turn, s3, intfName1="turn-eth0", params1={"ip":"1.20.50.100/24"}, delay="7ms")
        
        self.addLink(h1, nat3, intfName1="h1-eth", intfName2="nat3-local", params1={"ip":"172.16.1.10/24"}, params2={"ip":"172.16.1.1/24"}, delay="8ms")
        self.addLink(h2, nat3, intfName1="h2-eth", intfName2="nat3-ext", params1={"ip":"172.16.2.20/24"}, params2={"ip":"172.16.2.1/24"}, delay="8ms")

    def add_internet(net):
        """
        Adding the blue part in the schematic. Connecting both devices to the internet
        and to each other.
        """

        # http://mininet.org/api/classmininet_1_1net_1_1Mininet.html#a91f71b8107312feffe76c4cd2369d1c4
        # nat1 = net.addNAT("nat1", ip="1.20.30.1/28", connect=False, inNamespace=True, inetIntf="nat1-ext", localIntf="nat1-local") # The connect prevents a connection to s1
        # nat2 = net.addNAT("nat2", ip="2.40.60.1/28", connect=False, inNamespace=True, inetIntf="nat1-ext", localIntf="nat2-local")

        # net.addLink("s2", nat1, intfName2="nat1-local", params2={"ip":"1.20.30.1/28"}, delay="3ms")
        # net.addLink("s4", nat2, intfName2="nat2-local", params2={"ip":"2.40.60.1/28"}, delay="3ms")

        # net.addLink(nat1, "s3", intfName1="nat1-ext", params1={"ip":"1.20.50.10/24"}, delay="5ms")
        # net.addLink(nat2, "s3", intfName1="nat2-ext", params1={"ip":"1.20.50.20/24"}, delay="5ms")

        h1 = net.get("h1")
        h2 = net.get("h2")
        h1.cmd("ip route add default via 1.20.30.1 dev h1-cellular")
        h1.cmd("ip route add 172.16.2.0/24 via 172.16.1.1 dev h1-eth")
        h2.cmd("ip route add default via 2.40.60.1 dev h2-cellular")
        h2.cmd("ip route add 172.16.1.0/24 via 172.16.2.1 dev h2-eth")

        nat1 = net.get("nat1")
        nat1.cmd('sysctl net.ipv4.ip_forward=1')
        # nat1.cmd('sysctl net.ipv6.ip_forward=1') # Not necessary for now
        nat1.cmd('iptables -t nat -A POSTROUTING -o {} -j MASQUERADE'.format("nat1-ext"))

        nat2 = net.get("nat2")
        nat2.cmd('sysctl net.ipv4.ip_forward=1')
        nat2.cmd('iptables -t nat -A POSTROUTING -o {} -j MASQUERADE'.format("nat2-ext"))

        # nat1.cmd("ip route add 2.40.60.0/24 via 1.20.50.20 dev nat1-ext")
        # Should not be known to the nat at this time
        # nat2.cmd("ip route add 1.20.30.0/24 via 1.20.50.10 dev nat2-ext")

        # turn = net.get("turn")
        # turn.cmd("ip route add default via 1.20.50.10 dev turn-eth0")

        nat3 = net.get("nat3")
        nat3.cmd("sysctl net.ipv4.ip_forward=1")
        nat3.cmd("iptables -t nat -A POSTROUTING -o {} -j MASQUERADE".format("nat3-ext"))
        
        # nat3.cmd("ip route add default via 172.16.2.1 dev nat3-ext")
        # h2.cmd("ip route add 172.16.1.0/24 via 172.16.1.1 dev h2-eth")

    def enable_nat(net):
        """
        Disabling any NAT settings from before and only allow packets to flow from h2 -> internet -> h1 if
        h1 has sent packets before.
        """
        
        # For now, only enable such a strict nat for the host1
        nat1 = net.get("nat1")
        nat1.cmd("iptables -F")
        nat1.cmd("iptables -t nat -F")
        
        # Now enable packet forwarding only after we have seen some outgoing packets before
        nat1.cmd('iptables -t nat -A POSTROUTING -o {} -j MASQUERADE'.format("nat1-ext"))
        nat1.cmd("iptables -A FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT")
        nat1.cmd("iptables -A FORWARD -i nat1-local -j ACCEPT")
        nat1.cmd("iptables -A FORWARD -j DROP")
        
        nat2 = net.get("nat2")
        nat2.cmd("iptables -F")
        nat2.cmd("iptables -t nat -F")
        
        nat2.cmd('iptables -t nat -A POSTROUTING -o {} -j MASQUERADE'.format("nat2-ext"))
        nat2.cmd("iptables -A FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT")
        nat2.cmd("iptables -A FORWARD -i nat2-local -j ACCEPT")
        nat2.cmd("iptables -A FORWARD -j DROP")

        nat3 = net.get("nat3")
        nat3.cmd("iptables -F")
        nat3.cmd("iptables -t nat -F")
        
        nat3.cmd("iptables -t nat -A POSTROUTING -o {} -j MASQUERADE".format("nat3-ext"))
        nat3.cmd("iptables -A FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT")
        nat3.cmd("iptables -A FORWARD -i nat3-local -j ACCEPT")
        nat3.cmd("iptables -A FORWARD -j DROP")
        
class InternetTopo(Topo):
    "Single switch connected to n hosts."
    # pylint: disable=arguments-differ
    def build(self, n=2, **_kwargs ):
        # set up inet switch
        inetSwitch = self.addSwitch('s0')
        # add inet host
        inetHost = self.addNode('h0', cls=NAT, subnet="192.168.0.0/16", ip="192.168.0.1", localIntf="h0-eth0", inetIntf="h0-eth1")
        self.addLink(inetSwitch, inetHost)

        # add local nets
        for i in range(1, n+1):
            inetIntf = 'nat%d-eth0' % i
            localIntf = 'nat%d-eth1' % i
            localIP = '192.168.%d.1' % i
            localSubnet = '192.168.%d.0/24' % i
            natParams = { 'ip' : '%s/24' % localIP }
            # add NAT to topology
            nat = self.addNode('nat%d' % i, cls=NAT, subnet=localSubnet,
                               inetIntf=inetIntf, localIntf=localIntf)
            switch = self.addSwitch('s%d' % i)
            # connect NAT to inet and local switches
            self.addLink(nat, inetSwitch, intfName1=inetIntf)
            self.addLink(nat, switch, intfName1=localIntf, params1=natParams)
            # add host and connect to local switch
            host = self.addHost('h%d' % i,
                                ip='192.168.%d.100/24' % i,
                                defaultRoute='via %s' % localIP)
            self.addLink(host, switch)
        

    def configure_routing(net):

        nat = net.get("h0")
        nat.cmd("ip route add default via 131.159.196.38 dev wlp2s0")
        nat.cmd("iptables -A FORWARD -o h0-eth0 -j ACCEPT")
        # net.addNAT().configDefault()