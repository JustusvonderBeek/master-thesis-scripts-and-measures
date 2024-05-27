from dataclasses import dataclass
from enum import Enum

class Scenarios(Enum):
    SINGLE_PATH = 1
    SINGLE_PATH_WITH_LOCAL = 2
    SINGLE_PATH_WITH_INTERNET = 3
    FULL_NETWORK = 4

class Tests(Enum):
    QUICHEPERF = 1
    PING_PONG = 2
    DEBUG = 3
    QUICHEPERF_IF = 4
    QUICHEPERF_LOSS = 5
    QUICHEPERF_IF_INIT = 6

class Logging(Enum):
    NONE = 0
    ERROR = 1
    WARN = 2
    INFO = 3
    DEBUG = 4
    TRACE = 5

@dataclass
class TestConfiguration:
    # General
    scenario: Scenarios
    test: Tests

    # Path delays
    wifi_direct_path_delay: int = 6
    local_network_path_delay: int = 3
    local_network_path_ext_delay: int = 6
    internet_path_local_delay: int = 2
    # For the right path (h2 <-> nat2)
    internet_path_local_2_delay: int = 2
    internet_path_ext_delay: int = 12
    # For the right path (nat2 <-> s3) 
    internet_path_ext_2_delay: int = 12
    internet_path_turn_delay: int = 1

    # Features
    enable_pcap: bool = True
    enable_turn_server: bool = True
    block_stun_on_first_path: bool = False
    enable_cli_after_test: bool = False
    enable_snat : bool = False

    change_file_permissions: bool = False

    log_level: Logging = Logging.INFO
    build_target: str = "debug"
    throughput: str = "10MB"
    duration: int = 100

    def __init__(self, args):
        """
        Initialize the test configuration from the given command-line arguments
        """

        match args.logging:
            case 0:
                print("Disabling logging")
                self.log_level = Logging.NONE
            case 1:
                print("Logging level 'error'")
                self.log_level = Logging.ERROR
            case 2:
                print("Logging level 'warn'")
                self.log_level = Logging.WARN
            case 3:
                print("Logging level 'info'")
                self.log_level = Logging.INFO
            case 4:
                print("Logging level 'debug'")
                self.log_level = Logging.DEBUG
            case _:
                print("Logging level 'info'")
                self.log_level = Logging.INFO

        match args.setup:
            case "full":
                print(f"Starting the '{args.setup}' test scenario")
                self.scenario = Scenarios.FULL_NETWORK
            case "single":
                print(f"Starting the '{args.setup}' test scenario")
                self.scenario = Scenarios.SINGLE_PATH
            case "single+internet":
                print(f"Starting the '{args.setup}' test scenario")
                self.scenario = Scenarios.SINGLE_PATH_WITH_INTERNET
            case "single+local":
                print(f"Starting the '{args.setup}' test scenario")
                self.scenario = Scenarios.SINGLE_PATH_WITH_LOCAL
            case _:
                print(f"No exact scenario given, choosing 'default'")
                self.scenario = Scenarios.FULL_NETWORK

        match args.test:
            case "quicheperf":
                print(f"Starting the '{args.test}' scenario")
                self.test = Tests.QUICHEPERF
            case "ice_ping":
                print(f"Starting the '{args.test}' scenario")
                self.test = Tests.PING_PONG
            case "quicheperf_if_init":
                print(f"Starting the '{args.test}' scenario")
                self.test = Tests.QUICHEPERF_IF_INIT
            case "quicheperf_loss":
                print(f"Starting the '{args.test}' scenario")
                self.test = Tests.QUICHEPERF_LOSS
            case "quicheperf_if":
                print(f"Starting the '{args.test}' scenario")
                self.test = Tests.QUICHEPERF_IF
            case _:
                print(f"No test given, starting the 'debugging' scenario")
                self.test = Tests.DEBUG

        self.build_target = args.build_target
        self.duration = args.duration
        self.throughput = args.throughput
        self.enable_snat = args.snat

        if args.debug:
            # Irrelevant what scenario was given, debug the network
            self.test = Tests.DEBUG

        if args.permissions:
            self.change_file_permissions = True

        if args.disable_turn:
            self.enable_turn_server = False
        
        if args.cli:
            self.enable_cli_after_test = True

        if self.test == Tests.DEBUG:
            # Does not make sense to start this one again afterwards
            self.enable_cli_after_test = False

        if args.disable_pcap:
            self.enable_pcap = False