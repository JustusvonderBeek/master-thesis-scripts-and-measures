#!/bin/bash

# Commands to execute inside the mininet environment
# Get a new shell window: xterm h2
# Execute a command on a specific host: h1 <command>

h1 cd ../quiche-cm/target/debug

h1 ./quiche-server --cert ../../apps/src/bin/cert.crt --key ../../apps/src/bin/cert.key --listen 192.168.1.10:4433

# Or to server some HTML

h1 ./quiche-server --cert ../../apps/src/bin/cert.crt --key ../../apps/src/bin/cert.key --listen 192.168.1.10:4433 --root ../../apps/src/bin/root/

h1 ./quicheperf server --cert ../../src/cert.crt --key ../../src/cert.key -l 127.0.0.1:9999

# For multipath:
h1 ../quicheperf/target/release/quicheperf server -l 192.168.1.10:443 -l 172.16.1.10:443 --mp true --scheduler blest --cert ../quicheperf/src/cert.crt --key ../quicheperf/src/cert.key 

# --

xterm h2

h2 cd ../quiche-cm/target/debug
h2 ./quiche-client https://192.168.1.10:4433 --no-verify

h2 cd ../quicheperf/target/release
h2 ./quicheperf client -no-verify -c 192.168.1.10:9999

# For multipath
h2 ../quicheperf/target/release/quicheperf client -c 192.168.1.10:443 -c 172.168.1.10:443 -l 10.0.1.10:0 -l 172.16.2.20:0 --mp true