#!/bin/bash

# Commands to execute inside the mininet environment
# Get a new shell window: xterm h2
# Execute a command on a specific host: h1 <command>

h1 cd ../quiche-cm/target/debug

h2 ./quiche-server --cert ../../apps/src/bin/cert.crt --key ../../apps/src/bin/cert.key --listen 10.0.1.10:4433

# Or to server some HTML
h2 ./quiche-server --cert ../../apps/src/bin/cert.crt --key ../../apps/src/bin/cert.key --listen 10.0.1.10:443 --root ../../apps/src/bin/root/

h2 ./quicheperf server --cert ../../src/cert.crt --key ../../src/cert.key -l 127.0.0.1:9999

# For multipath: (to use both paths use round-robin)
h2 ../quicheperf/target/release/quicheperf server -l 10.0.1.10:443 -l 172.16.2.20:443 --mp true --scheduler round-robin --cert ../quicheperf/src/cert.crt --key ../quicheperf/src/cert.key 

# --

xterm h1

h1 cd ../quiche-cm/target/debug
h1 ./quiche-client https://10.0.1.10:443 --no-verify

h1 cd ../quicheperf/target/release
h1 ./quicheperf client -no-verify -c 10.0.1.10:9999

# For multipath
h1 ../quicheperf/target/release/quicheperf client -c 10.0.1.10:443 -c 172.168.2.20:443 -l 192.168.1.10:0 -l 172.16.1.10:0 --mp true --scheduler round-robin