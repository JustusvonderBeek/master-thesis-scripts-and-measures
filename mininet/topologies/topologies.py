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

from config import Scenarios
from dataclasses import dataclass

from mininet.topo import Topo
from mininet.node import OVSController
from mininet.net import Mininet

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
    enable_turn_host: bool = True
    block_stun_on_first_path: bool = False

    # Path delays
    wifi_direct_path_delay: int = 3
    local_network_path_delay: int = 5
    internet_path_local_delay: int = 1
    internet_path_ext_delay: int = 100
    internet_path_turn_delay: int = 1


def create_test_scenario(scenario, logging):
    """
    Creating the mininet setup given.
    Returns the ready but not unstarted network
    """

    print(f"Creating the {scenario} network scenario")

    match scenario:
        case Scenarios.SINGLE_PATH:
            configuration = NetworkConfiguration(
                enable_local_network_path=False,
                enable_internet_path=False,
                enable_turn_host=False,
                block_stun_on_first_path=False
            )
        case Scenarios.SINGLE_PATH_WITH_LOCAL:
            configuration = NetworkConfiguration(
                enable_internet_path=False,
                enable_turn_host=False,
                block_stun_on_first_path=False
            )
        case Scenarios.SINGLE_PATH_WITH_INTERNET:
            configuration = NetworkConfiguration(
                enable_local_network_path=False,
                block_stun_on_first_path=False
            )
        case Scenarios.FULL_NETWORK:
            configuration = NetworkConfiguration()
        case _:
            print(f"'{scenario}' is no valid scenario name!")
            return ValueError

    network = create_network(configuration)
    return network

def create_network(configuration):
    """
    Creating the given network from from the given configuration
    """

    default_topo = DefaultNetwork()
    net = Mininet(default_topo, controller= OVSController)
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

        self.addHost("h1")
        self.addHost("h2")
        
        self.addSwitch("s1")