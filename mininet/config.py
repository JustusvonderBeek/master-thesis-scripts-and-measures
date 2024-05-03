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

class Logging(Enum):
    ERROR = 1
    WARN = 2
    INFO = 3
    DEBUG = 4
    TRACE = 5