from mininet.net import Mininet

class Ethernet:
    """
    Takes the default network (or modified) and expands the network to 
    include an additional connection via a single NAT between both
    hosts.
    This NAT allows outgoing packets from host1 to host2
    but only incoming packets to traverse the NAT after a connection
    has been established

    h1 ------- NAT |> ----------- h2

    Configuration:
    - delay
    - blocking Direction
    - TODO:

    """

    @staticmethod
    def build(net: Mininet, configuration):
        """
        Adding the link between the first and second host.
        Applies any relevant configuration given to this path
        """

        if not configuration.enable_local_network_path:
            return

        # Creating the additional hosts
        Ethernet._create_hosts(net, configuration)

        # Creating the links
        Ethernet._create_links(net, configuration)

        # Performing the routing table actions
        Ethernet._setup_routing_table(net, configuration)

    @staticmethod
    def _create_hosts(net: Mininet, configuration):
        """
        Adding the required hosts to the network
        """

        # Naming convention taken from earlier iterations
        net.addHost("nat3")

    @staticmethod
    def _create_links(net: Mininet, configuration):
        """
        Adding the required links between the hosts in the network
        """

        net.addLink(node1="h1", node2="nat3", intfName1="h1-eth", intfName2="nat3-local", params1={"ip": "172.16.1.10/24"},  params2={"ip":"172.16.1.1/24"}, delay=f"{configuration.local_network_path_delay}ms")
        net.addLink(node1="h2", node2="nat3", intfName1="h2-eth", intfName2="nat3-ext", params1={"ip": "172.16.2.20/24"}, params2={"ip":"172.16.2.1/24"}, delay=f"{configuration.local_network_path_ext_delay}ms")


    @staticmethod
    def _setup_routing_table(net, configuration):
        """
        Performing setups for the routing table
        """

        h1 = net.get("h1")
        h2 = net.get("h2")
        nat3 = net.get("nat3")

        h1.cmd("ip route add 172.16.2.0/24 via 172.16.1.1 dev h1-eth")
        h2.cmd("ip route add 172.16.1.0/24 via 172.16.2.1 dev h2-eth")

        nat3.cmd("sysctl net.ipv4.ip_forward=1")

        nat3.cmd("iptables -F")
        nat3.cmd("iptables -t nat -F")
        
        nat3.cmd("iptables -t nat -A POSTROUTING -o {} -j MASQUERADE".format("nat3-ext"))
        # nat3.cmd("iptables -A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j LOG --log-prefix='[mininet-fw] '")
        nat3.cmd("iptables -A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT")
        nat3.cmd("iptables -A FORWARD -i nat3-local -j ACCEPT")
        nat3.cmd("iptables -A FORWARD -j REJECT")