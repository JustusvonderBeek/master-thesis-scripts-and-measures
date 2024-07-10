from mininet.net import Mininet
from mininet.nodelib import NAT

class RealWorld:
    """
    Creates a host behind a NAT and connect the host to the internet
    allowing to test the cellular network NAT (ADM-APF) with a less
    strict counterpart (EIM-ADF)

    Internet ---- NAT |> ----------- h1

    Configuration:
    - NAT type

    """

    @staticmethod
    def build(net: Mininet, configuration):
        """
        Adding the link between the first host and NAT.
        Applies any relevant configuration given to this path
        """

        if not configuration.enable_real_world_path:
            return

        # Creating the additional hosts
        RealWorld._create_hosts(net, configuration)

        # Creating the links
        RealWorld._create_links(net, configuration)

        # Performing the routing table actions
        RealWorld._setup_routing_table(net, configuration)

    @staticmethod
    def _create_hosts(net: Mininet, configuration):
        """
        Adding the required hosts to the network
        """

        # Delete the default host h2
        net.delHost(net.get("h2"))

        # Naming convention taken from earlier iterations
        net.addHost("nat", cls=NAT, inNamespace=False, subnet="192.168.3.0/24")
        # net.addHost("h1")

    @staticmethod
    def _create_links(net: Mininet, configuration):
        """
        Adding the required links between the hosts in the network
        """

        net.addLink(node1="h1", node2="nat", intfName1="h1-eth", intfName2="nat-local", params1={"ip": "192.168.3.10/24"},  params2={"ip":"192.168.3.1/24"})


    @staticmethod
    def _setup_routing_table(net, configuration):
        """
        Performing setups for the routing table
        """

        h1 = net.get("h1")
        nat = net.get("nat")

        h1.cmd("ip route add 0.0.0.0/0 via 192.168.3.1 dev h1-eth")

        # Prevent the nat from sending everything back to into the net but rather forward to
        # the real internet interface
        nat.cmd("ip route add 0.0.0.0/0 via 192.168.2.10 dev nat-external")
        
        nat.cmd("sysctl net.ipv4.ip_forward=1")

        nat.cmd("iptables -F")
        nat.cmd("iptables -t nat -F")
        
        
        # nat.cmd("iptables -t nat -A POSTROUTING -o {} -j MASQUERADE".format("nat3-ext"))
        # nat3.cmd("iptables -A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j LOG --log-prefix='[mininet-fw] '")
        # nat.cmd("iptables -A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT")
        # nat.cmd("iptables -A FORWARD -i nat3-local -j ACCEPT")
        # nat.cmd("iptables -A FORWARD -j REJECT")
        
        # Source: http://www.joewein.net/info/sw-iptables-full-cone-nat.htm
        internal_iface="nat-local"
        external_iface="enX0"
        # nat.cmd(f"iptables -t nat -A POSTROUTING -o {external_iface} -j MASQUERADE".format(external_iface))
        nat.cmd(f"iptables -t nat -A POSTROUTING -o {external_iface} -j SNAT --to-source 172.31.25.142")
        nat.cmd(f"iptables -t nat -A PREROUTING -i {external_iface} -j DNAT --to-destination 192.168.3.10")