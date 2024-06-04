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

| Application Tested | When | Devices | Software | Accounts | Tests |
| --- | --- | --- | --- | --- | --- |
| WhatsApp | 04.06.2024 | 2* Pixel 2 XL; I11CM0093 & I11CM0095 | WhatsApp: 2.24.10.85 & 2.24.10.85; Magisk 27.0 & 27.0; ADB_ROOT v1 & v1 | My Google Account & MT Google Account | Different Access Technologies (WiFi, WiFi & Cellular, Cellular); Path Migration; Path Finding |
| --- | --- | --- | --- | --- | --- |


| Test | Devices | Direction | Connectivity | Description | Duration | Notes | 
| --- | --- | --- | --- | --- | --- | --- |
| 24.05 18:32 | RaspberryPi, Computer | PC -> Pi | PC: WiFi + LAN, Pi: LAN | 20000:10000 initial communication, allowed through FW, everything else normal | --- | Failed with FW answer ICMP admin. filtered |
| --- | --- | --- | --- | --- | --- | --- |
| 04.06 11:12 | I11CM0093 & I11CM0095 | Test Acc. -> Personal Acc. | Both: WiFi (Adapter with Internet) + Cellular | Video Call, Path building: start call next to each other, wait for connection, accept, idle, end call. | 30s after call accept | Should check for path building, idle pings, if both paths can be found |
| 04.06 11:14 | I11CM0093 & I11CM0095 | Test Acc. -> Personal Acc. | Both: WiFi (Adapter with Internet) + Cellular | Audio Call, Path building: start call next to each other, wait for connection, accept, idle, end call. | 30s after call accept | Should check for path building, idle pings, if both paths can be found |
| 04.06 11:17 | I11CM0093 & I11CM0095 | Test Acc. -> Personal Acc. | Both: WiFi (Adapter with Internet) + Cellular | Video Call, Path building: start call next to each other, wait for connection, accept, idle, end call. | 30s after call accept | Should check for path building, idle pings, if both paths can be found |
| 04.06 11:19 | I11CM0093 & I11CM0095 | Test Acc. -> Personal Acc. | Both: WiFi (Adapter with Internet) + Cellular | Video Call, Path building: start call next to each other, wait for connection, accept, idle, end call. | 30s after call accept | Should check for path building, idle pings, if both paths can be found |

## Analysis
This section contains the conclusions and analysis of our testing for the different apps.

| Application | Tests Considered | Behavior | Conclusion | Special Attributes |
| --- | --- | --- | --- | --- |
| WhatsApp | 24.05 11:12-11:19 | WiFi Path Probing | Performed for Local WiFi (direct path + TURN server) | TURN server unknown **attributes** (allocation, probably mapping WA call), Local WiFi plain STUN request (0x0001; 0x0101) without ANY **attributes** besides integrity
| WhatsApp | 24.05 11:12-11:19 | Cellular Path Probing | Not probed, no path build | --- |
| WhatsApp | 24.05 11:12-11:19 | Path Building Time | TURN server path | Build for initial exchange: <100ms |
| WhatsApp | 24.05 11:12-11:19 | Path Building Time | Local WiFi path | ~400ms after call started  | --- |
| WhatsApp | 24.05 11:12-11:19 | Idle Path Maintenance | Actively probed with STUN every ~1s (TURN server path) | **Message type** 0x0801 (unknown) from client, **message type** 0x0802 (unknown) from server |
| WhatsApp | 24.05 11:12-11:19 | Active Path Maintenance | Half as frequently probed. First probe after 15.4s, then every 2s | Callee makes binding request **message type** (0x0001), Priority **attribute** set to 1, caller replies binding success (0x0101) and same priority |
| --- | --- | --- | --- | --- |

### General Flow
The default flow of WhatsApp Video Calls.

Both in the same local WiFi AP

Caller:
1. TCP connection to WhatsApp (XMPP ports)
2. Probably SIP or other protocol to exchange call information via TCP
3. Reserve resources on Facebook TURN servers
4. Success responses from the TURN servers
5. First data is transferred via TURN servers
6. Accept and return STUN Binding request (Binding Success, Binding request)
7. Exchange data via local WiFi AP
8. Sometimes exchange with Facebook TURN via TCP
9. Ending call
10. ICMP unreachable received
11. De-allocate STUN bindings on servers

Callee:
1. TCP Connection to WhatsApp (XMPP ports)
2. Receive call information via TCP
3. Reserve resources on Facebook TURN servers
4. Success responses from the TURN servers
5. First data is transferred via TURN servers
6. Send Local STUN Binding request
7. Exchange data via local WiFi AP
8. Sometimes exchange with Facebook TURN via TCP
9. Ending call
10. ICMP unreachable received
11. De-allocate STUN bindings on servers


### Notes
During the analysis the following interesting information were found:

- WhatsApp uses an unknown STUN attribute 0x4000. This attribute is in the range of non-optional attributes, but must not be registered by the IETF, rather by expert review (aka. should not be assigned by others). The purpose of this attribute is unclear
- 0x4000 is send at the beginning and end of the call, probably free the allocations, including a 150 byte identifier?
- Further attributes 0x4002, 0x4004, 0x4007 are observed but unclear what they mean
- 0x4002 is 8 bytes and corresponds with the TURN server address, for the same server it is the same in the response
- 0x4004 is padding of 452 bytes 0?
- 0x4007 is 2 bytes and in our case **always** 01f4 == 500

