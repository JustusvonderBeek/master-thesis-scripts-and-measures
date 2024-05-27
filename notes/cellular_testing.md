# Notes Regarding the Cellular Real-Life Tests
Some information to look up later on and find infos during writing

## Setup
The setup was kinda hard. Driver was installed, but the card did not have any configuration loaded. Loading a config on linux seems difficult.

// TODO: Write what we did
Some commands
```bash
mmcli -m 0 # Showing output of the modem
mmcli -m 1 --set-primary-sim-slot=1 # Switching to the hardware sim card instead of some bogus eSim
nmcli -m 0 connection wwan0 up "Drillisch"
```