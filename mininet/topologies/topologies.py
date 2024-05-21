# This class allows to create the testing topology with different
# difficulties in types of NATs and NAT setups
# 
# Via the configuration, many options can be enabled or disabled
# to allow for specific scenario testing
#
# Currently the following paths and setups are available:
#
# Single Path: h1 -- wifi-direct -- h2
#
# Ethernet: h1 -- NAT |> -- h2
#
# Internet: h1 -- NAT |> -- <| NAT -- h2
#
# Every path can be enabled or disabled resulting in the required
# final network configuration

from config import Scenarios, Tests, TestConfiguration
from dataclasses import dataclass
from .old_topologies import DirectAndInternetAndTURN

from mininet.topo import Topo, MinimalTopo
from mininet.node import OVSController
from mininet.net import Mininet
from mininet.link import TCLink

from .wifi_direct import WiFiPath
from .ethernet_network import Ethernet
from .cellular_network import Cellular

@dataclass
class NetworkConfiguration:
    """
    The configuration class for mininet networks.
    Should allow to precisely specify which paths to enable,
    which NATs and paths to include and which difficulty each
    path should have
    """

    # Paths
    enable_wifi_direct_path: bool = True
    enable_local_network_path: bool = True
    enable_internet_path: bool = True
    
    # Features
    enable_turn_host: bool = False
    block_stun_on_first_path: bool = False
    snat = False

    # Path delays
    wifi_direct_path_delay: int = 3
    local_network_path_delay: int = 5
    internet_path_local_delay: int = 2
    internet_path_local_2_delay: int = 2
    internet_path_ext_delay: int = 12
    internet_path_ext_2_delay: int = 12
    internet_path_turn_delay: int = 1


def create_test_scenario(test_conf: TestConfiguration):
    """
    Creating the mininet setup given.
    Returns the ready but not unstarted network
    """

    print(f"Creating the {test_conf.scenario} network scenario")

    match test_conf.scenario:
        case Scenarios.SINGLE_PATH:
            configuration = NetworkConfiguration(
                enable_local_network_path=False,
                enable_internet_path=False,
                block_stun_on_first_path=False
            )
        case Scenarios.SINGLE_PATH_WITH_LOCAL:
            configuration = NetworkConfiguration(
                enable_internet_path=False,
                block_stun_on_first_path=False
            )
        case Scenarios.SINGLE_PATH_WITH_INTERNET:
            configuration = NetworkConfiguration(
                enable_local_network_path=False,
                enable_turn_host=True,
                block_stun_on_first_path=False
            )
        case Scenarios.FULL_NETWORK:
            configuration = NetworkConfiguration(
                enable_turn_host=True,
            )
        case _:
            print(f"'{test_conf.scenario}' is no valid scenario name!")
            return ValueError

    if test_conf.enable_turn_server:
        configuration.enable_turn_host = True
    else:
        configuration.enable_turn_host = False

    # Taking the configuration values from the TestConfig
    configuration.wifi_direct_path_delay = test_conf.wifi_direct_path_delay
    configuration.local_network_path_delay = test_conf.local_network_path_delay
    configuration.internet_path_local_delay = test_conf.internet_path_local_delay
    configuration.internet_path_local_2_delay = test_conf.internet_path_local_2_delay
    configuration.internet_path_ext_delay = test_conf.internet_path_ext_delay
    configuration.internet_path_ext_2_delay = test_conf.internet_path_ext_2_delay

    configuration.snat = test_conf.enable_snat

    if test_conf.test == Tests.PING_PONG:
        # If STUN not blocked this won't work since we will always
        # find a path via the first connection
        configuration.block_stun_on_first_path = True

    network = create_network(configuration)

    # topo = DirectAndInternetAndTURN(second_path=True, third_path=True, save_delay=True, block_stun=False)
    # network = Mininet(topo=topo, controller= OVSController)
    # DirectAndInternetAndTURN.add_internet(network)
    # DirectAndInternetAndTURN.enable_nat(network)
    return network

def create_network(configuration):
    """
    Creating the given network from from the given configuration
    """

    default_topo = DefaultNetwork()
    # Requires TCLink to enable delays
    net = Mininet(default_topo, controller=OVSController, link=TCLink, autoSetMacs=True)
    # Now, expand the default configuration to the desired size and configuration
    WiFiPath.build(net, configuration)
    Ethernet.build(net, configuration)
    Cellular.build(net, configuration)
    
    return net

class DefaultNetwork(Topo):
    """
    The very basic default network, including two hosts and a single
    switch without any connection.
    This is only meant as a base which can then be expanded further
    """

    def build(self):
        """
        Building the default network with two hosts
        No links between the hosts are made
        """

        self.addHost("h1", ip="192.168.1.2/24")
        self.addHost("h2", ip="192.168.1.2/24")
        # self.addSwitch("s1")
        
        # self.addLink(node1="h1", node2="s1", intfName1="h1-wifi", intfName2="s1-wifi1", params1={"ip": "192.168.1.2/24"}, delay=f"{5}ms")
        # self.addLink(node1="h2", node2="s1", intfName1="h2-wifi", intfName2="s1-wifi2", params1={"ip": "192.168.1.3/24"}, delay=f"{5}ms")
