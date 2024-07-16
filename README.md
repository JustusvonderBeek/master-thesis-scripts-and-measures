# Scripts and Measurement Information for Master Thesis: Seamless Migration of Peer-To-Peer QUIC Connections in Mobile Environments
This repository contains the measurement scripts and additional information for the tests performed. 

## Structure
The repository is structured as follows:

```
├── box_measurements
├── mininet
├── notes
├── pixelRooting
├── plotting
└── README.md
```

## Getting started
The Mininet setup and test evaluation is performed by the scripts in **mininet**. The command line features and output is shown in below.

```
sudo python3 main.py -h
usage: main.py [-h] [-s SETUP] [-t TEST] [-l DURATION] [--disable-pcap] [-d] [-c] [-p] [--disable-turn] [-n] [-k] [--logging LOGGING] [--build-target BUILD_TARGET] [--throughput THROUGHPUT]
               [--scenario SCENARIO] [--real]

Creating measurement environment for the master thesis and executing tests

options:
  -h, --help            show this help message and exit
  -s SETUP, --setup SETUP
  -t TEST, --test TEST
  -l DURATION, --duration DURATION
  --disable-pcap
  -d, --debug
  -c, --cli
  -p, --permissions
  --disable-turn
  -n, --snat
  -k, --log-sslkeys
  --logging LOGGING
  --build-target BUILD_TARGET
  --throughput THROUGHPUT
  --scenario SCENARIO
  --real
```

Notes regarding the different tests performed and their respective outcome can be found under **notes**. We also include the plotting script for the data extraction and displaying under **plotting**.

The scripts relevant for the peer-to-peer application analysis and real-world evaluation are located in **box_measurements**.
