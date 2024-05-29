# Notes Regarding the Cellular Real-Life Tests
Some information to look up later on and find infos during writing

## Setup
The setup was kinda hard. Driver was installed, but the card was not recognized at first. Turns out one had to switch the SIM card to another slot first. Then, the modem firmware was not accessible because of some US regulation requirements. This could be unlocked by running a script from the Lenovo website. Afterwards, the connection could be established via the nmcli tool or GUI. Now it seems the modem is working. Comments about the bad connectivity seemed to be not true for my device.

```bash
mmcli -m 0 # Showing output of the modem
mmcli -m 1 --set-primary-sim-slot=1 # Switching to the hardware sim card instead of some bogus eSim
nmcli -m 0 radio wwan0 on # <- My memory only, check if cmd correct
nmcli -m 0 connection wwan0 up "Drillisch"
```


## Test Overview
The following section contains information regarding the devices, interfaces & configurations used for testing.

| Test | Devices | Direction | Description | Notes | 
| --- | --- | --- | --- | --- |
| 24.05 18:32 | RaspberryPi, Computer | PC -> Pi | 20000:10000 initial communication, allowed through FW, everything else normal | Failed with FW answer ICMP admin. filtered |
| TODO | TODO | TODO | TODO | TODO |
