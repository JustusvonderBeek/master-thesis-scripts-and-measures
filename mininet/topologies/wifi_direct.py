from mininet.net import Mininet

class WiFiPath:
    """
    Takes the default network and expands the network to have a single link between the
    two hosts. Allows to specify if features need to be disabled

    h1 ------- s1 -------- h2

    Configuration:
    - delay
    - blocking STUN

    """

    @staticmethod
    def build(net: Mininet, configuration):
        """
        Adding the link between the first and second host in the default network.
        Applies any relevant configuration given to this path
        """

        if not configuration.enable_wifi_direct_path:
            return

        # Creating the links
        WiFiPath._create_links(net, configuration)

        # Performing the routing table actions
        WiFiPath._setup_routing_table(net, configuration)

    @staticmethod
    def _create_hosts(net, configuration):
        """
        Adding the required hosts to the network
        """

        pass

    @staticmethod
    def _create_links(net, configuration):
        """
        Adding the required links between the hosts in the network
        """

        net.addLink(node1="h1", node2="s1", intfName1="h1-wifi", intfName2="s1-wifi1", params1={"ip": "192.168.1.2/24"}, delay=f"{configuration.wifi_direct_path_delay}ms")
        net.addLink(node1="h2", node2="s1", intfName1="h2-wifi", intfName2="s1-wifi2", params1={"ip": "192.168.1.3/24"}, delay=f"{configuration.wifi_direct_path_delay}ms")


    @staticmethod
    def _setup_routing_table(net, configuration):
        """
        Performing setups for the routing table
        """

        if configuration.block_stun_on_first_path:
            h1 = net.get("h1")
            h2 = net.get("h2")
            h1.cmd("iptables -A OUTPUT -o h1-wifi -p udp -d 192.168.1.0/24 -j DROP")
            h2.cmd("iptables -A OUTPUT -o h2-wifi -p udp -d 192.168.1.0/24 -j DROP")