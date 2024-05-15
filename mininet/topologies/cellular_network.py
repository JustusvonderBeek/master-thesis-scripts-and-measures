from mininet.net import Mininet

class Cellular:
    """
    Takes the default network (or modified) and expands the network to 
    include an additional connection via a two NATs between both
    hosts and an emulated internet connection in between the NATs.

    Both NATs allow outgoing packets to the internet but incoming 
    packets are blocked until a connection has been established.
    
    Additionally this network path can include a STUN/TURN server
    host allowing to resolve the public IP address and port combination.

                 TURN Server Host
                         |
    h1 ------- NAT |> ------- <| NAT ------- h2

    
    Configuration:
    - delay on the local paths to the NAT
    - delay on the external path between the NATs
    - TURN Server host
    """

    @staticmethod
    def build(net: Mininet, configuration):
        """
        Adding the link between the first and second host.
        Applies any relevant configuration given to this path
        """

        if not configuration.enable_internet_path:
            return

        # Creating the additional hosts
        Cellular._create_hosts(net, configuration)

        # Creating the links
        Cellular._create_links(net, configuration)

        # Performing the routing table actions
        Cellular._setup_routing_table(net, configuration)

    @staticmethod
    def _create_hosts(net: Mininet, configuration):
        """
        Adding the required hosts to the network
        """
        
        # Naming convention taken from earlier iterations
        net.addHost("nat1")
        net.addHost("nat2")

        net.addSwitch("s2") # H1 <-> Nat1
        net.addSwitch("s3") # Nat1 <-> Nat2
        net.addSwitch("s4") # Nat2 <-> H2

        if configuration.enable_turn_host:
            net.addHost("turn")
        
    @staticmethod
    def _create_links(net: Mininet, configuration):
        """
        Adding the required links between the hosts in the network
        """

        net.addLink(node1="h1", node2="s2", intfName1="h1-cellular", params1={"ip":"1.20.30.2/28"}, delay=f"{configuration.internet_path_local_delay}ms", use_htb=True)
        net.addLink(node1="h2", node2="s4", intfName1="h2-cellular",  params1={"ip":"2.40.60.3/28"}, delay=f"{configuration.internet_path_local_delay}ms", use_htb=True)

        net.addLink("s2", "nat1", intfName2="nat1-local", params2={"ip":"1.20.30.1/28"}, delay=f"{configuration.internet_path_local_delay}ms", use_htb=True)
        net.addLink("s4", "nat2", intfName2="nat2-local", params2={"ip":"2.40.60.1/28"}, delay=f"{configuration.internet_path_local_delay}ms", use_htb=True)

        net.addLink("nat1", "s3", intfName1="nat1-ext", params1={"ip":"1.20.50.10/24"}, delay=f"{configuration.internet_path_ext_delay}ms", use_htb=True)
        net.addLink("nat2", "s3", intfName1="nat2-ext", params1={"ip":"1.20.50.20/24"}, delay=f"{configuration.internet_path_ext_delay}ms", use_htb=True)
        net.addLink("turn", "s3", intfName1="turn-eth0", params1={"ip":"1.20.50.100/24"}, delay=f"{configuration.internet_path_turn_delay}ms", use_htb=True)


    @staticmethod
    def _setup_routing_table(net, configuration):
        """
        Performing setups for the routing table and NAT configuration
        """

        h1 = net.get("h1")
        h2 = net.get("h2")
        nat1 = net.get("nat1")
        nat2 = net.get("nat2")
        
        h1.cmd("ip route add default via 1.20.30.1 dev h1-cellular")
        h2.cmd("ip route add default via 2.40.60.1 dev h2-cellular")

        nat1.cmd('sysctl net.ipv4.ip_forward=1')
        nat1.cmd("iptables -F")
        nat1.cmd("iptables -t nat -F")

        if configuration.snat:
            nat1.cmd('iptables -t nat -A POSTROUTING -o {} -s 1.20.30.2 -d 1.20.50.0/24 -j SNAT --to-source 1.20.50.10'.format("nat1-ext"))
            nat1.cmd('iptables -t nat -A PREROUTING -i {} -d 1.20.50.10 -s 1.20.50.0/24 -j DNAT --to-destination 1.20.30.2'.format("nat1-ext"))
            # nat1.cmd('iptables -t nat -A PREROUTING -i {} -m conntrack --ctstate NEW -j REJECT'.format("nat1-ext"))
            # nat1.cmd('iptables -A FORWARD -i {} -m conntrack --ctstate SNAT -j ACCEPT'.format("nat1-ext"))
        else:
            nat1.cmd('iptables -t nat -A POSTROUTING -o {} -j MASQUERADE'.format("nat1-ext"))
            nat1.cmd("iptables -A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT")
            # nat1.cmd("iptables -A FORWARD -m conntrack --ctstate NEW,RELATED,ESTABLISHED -j LOG --log-prefix='[mininet] '")
            nat1.cmd("iptables -A FORWARD -i nat1-local -j ACCEPT")
            nat1.cmd("iptables -A FORWARD -j REJECT")

        nat2.cmd('sysctl net.ipv4.ip_forward=1')
        nat2.cmd("iptables -F")
        nat2.cmd("iptables -t nat -F")

        if configuration.snat:
            nat2.cmd('iptables -t nat -A POSTROUTING -o {} -s 2.40.60.3 -d 1.20.50.0/24 -j SNAT --to-source 1.20.50.20'.format("nat2-ext"))
            nat2.cmd('iptables -t nat -A PREROUTING -i {} -d 1.20.50.20 -s 1.20.50.0/24 -j DNAT --to-destination 2.40.60.3'.format("nat2-ext"))
        else:
            nat2.cmd('iptables -t nat -A POSTROUTING -o {} -j MASQUERADE'.format("nat2-ext"))
            nat2.cmd("iptables -A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT")
            # nat2.cmd("iptables -A FORWARD -m conntrack --ctstate NEW,RELATED,ESTABLISHED -j LOG --log-prefix='[mininet] '")
            nat2.cmd("iptables -A FORWARD -i nat2-local -j ACCEPT")
            nat2.cmd("iptables -A FORWARD -j REJECT")