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

| Application Tested | When | Devices | SIM Card | Software | Accounts | Tests |
| --- | --- | --- | --- | --- | --- | --- |
| WhatsApp | 04.06.2024 | 2* Pixel 2 XL; I11CM0093 & I11CM0095 | I11CM0093: Telekom & I11CM0095: sim.de (carrier was o2) | WhatsApp: 2.24.10.85 & 2.24.10.85; Magisk 27.0 & 27.0; ADB_ROOT v1 & v1 | My Google Account & MT Google Account | Different Access Technologies (WiFi, WiFi & Cellular, Cellular); Path Migration; Path Finding |
| --- | --- | --- | --- | --- | --- |

Test notes:
- The local AP only supported IPv4, no IPv6 (DHCP Server)
- All tests muted (in video call and audio call)
- Moving hand in front of camera to induce data transfer
- Ring 3 times before accept

Now the tests with findings

| Test | Devices | Direction | Connectivity | Description | Duration | Notes | 
| --- | --- | --- | --- | --- | --- | --- |
| 24.05 18:32 | RaspberryPi, Computer | PC -> Pi | PC: WiFi + LAN, Pi: LAN | 20000:10000 initial communication, allowed through FW, everything else normal | --- | Failed with FW answer ICMP admin. filtered |
| --- | --- | --- | --- | --- | --- | --- |
| 04.06 11:12 | I11CM0093 & I11CM0095 | Test Acc. -> Personal Acc. | Both: WiFi (Adapter with Internet) + Cellular | **Video Call**, Path building: start call next to each other, wait for connection, accept, idle, end call. | 30s after call accept | Should check for path building, idle pings, if both paths can be found |
| 04.06 11:14 | I11CM0093 & I11CM0095 | Test Acc. -> Personal Acc. | Both: WiFi (Adapter with Internet) + Cellular | **Audio Call**, Path building: start call next to each other, wait for connection, accept, idle, end call. | 30s after call accept | Should check for path building, idle pings, if both paths can be found |
| 04.06 11:17 | I11CM0093 & I11CM0095 | Test Acc. -> Personal Acc. | Both: WiFi (Adapter with Internet) + Cellular | **Video Call**, Path building: start call next to each other, wait for connection, accept, idle, end call. | 30s after call accept | Should check for path building, idle pings, if both paths can be found |
| 04.06 11:19 | I11CM0093 & I11CM0095 | Test Acc. -> Personal Acc. | Both: WiFi (Adapter with Internet) + Cellular | **Video Call**, Path building: start call next to each other, wait for connection, accept, idle, end call. | 30s after call accept | Should check for path building, idle pings, if both paths can be found |
| 04.06 15:42 | I11CM0093 & I11CM0095 | Test Acc. -> Personal Acc. | Both: WiFi (Adapter with Internet) + Cellular | **Video Call**, Path building: start call next to each other, wait for connection, accept, idle, end call. | 60s after call accept | Confirm above findings |
| 04.06 16:08 | I11CM0093 & I11CM0095 | Test Acc. -> Personal Acc. | My Account: WiFi (Adapter with Internet) + Cellular, Test Account: only cellular, WiFi off | **Video Call**, Path building: start call next to each other, wait for connection, accept, idle, end call. *Changed to previous tests: Both use less data for video calls* | 30s after call accept | Direct path build in this scenario? Path found? |
| 04.06 16:12 | I11CM0093 & I11CM0095 | Test Acc. -> Personal Acc. | My Account: WiFi (Adapter with Internet) + Cellular, Test Account: only cellular, WiFi off | **Video Call**, Path building: start call next to each other, wait for connection, accept, idle, end call. *Changed to previous tests: Both use less data for video calls* | 30s after call accept | Direct path build in this scenario? Path found? |
| 04.06 16:14 | I11CM0093 & I11CM0095 | Test Acc. -> Personal Acc. | My Account: WiFi (Adapter with Internet) + Cellular, Test Account: only cellular, WiFi off | **Video Call**, Path building: start call next to each other, wait for connection, accept, idle, end call. *Changed to previous tests: Both use less data for video calls* | 30s after call accept | Direct path build in this scenario? Path found? |
| 04.06 17:07 | I11CM0093 & I11CM0095 | Test Acc. -> Personal Acc. | My Account: WiFi (HHG) + Cellular, Test Account: Cellular, WiFi off | **Video Call**, Cellular only path building, IPv6 external *Changed to previous tests: My Account is in HHG WiFi* | 45s after call accept | Confirm no path build |
| 04.06 17:30 | I11CM0093 & I11CM0095 | Test Acc. -> Personal Acc. | My Account: Cellular, Test Account: Cellular | **Video Call**, Cellular only path building, IPv6 external *Changed to previous tests: Both only cellular* | 30s after call accept | Path build? |
| 04.06 17:32 | I11CM0093 & I11CM0095 | Test Acc. -> Personal Acc. | My Account: Cellular, Test Account: Cellular | **Video Call**, Cellular only path building, IPv6 external *Changed to previous tests: Both only cellular* | 30s after call accept | Path build? |
| 04.06 17:34 | I11CM0093 & I11CM0095 | Test Acc. -> Personal Acc. | My Account: Cellular, Test Account: Cellular | **Video Call**, Cellular only path building, IPv6 external *Changed to previous tests: Both only cellular* | 30s after call accept | Path build? |
| 04.06 18:09 | I11CM0093 & I11CM0095 | Test Acc. -> Personal Acc. | My Account: WiFi (HHG) (->off) + Cellular, Test Account: Cellular | **Video Call**, Two paths build? Path Migration? *Changed to previous tests: My Account in WiFi, turning of WiFi with active path* | 15s after call accepted WiFi off, 45s total | Paths on all ifaces build? Path migrated? |
| 04.06 18:12 | I11CM0093 & I11CM0095 | Test Acc. -> Personal Acc. | My Account: WiFi (HHG) (->off) + Cellular, Test Account: Cellular | **Video Call**, Two paths build? Path Migration? *Changed to previous tests: My Account in WiFi, turning of WiFi with active path* | 15s after call accepted WiFi off, 45s total | Paths on all ifaces build? Path migrated? |
| 04.06 18:14 | I11CM0093 & I11CM0095 | Test Acc. -> Personal Acc. | My Account: WiFi (HHG) (->off) + Cellular, Test Account: Cellular | **Video Call**, Two paths build? Path Migration? *Changed to previous tests: My Account in WiFi, turning of WiFi with active path* | 15s after call accepted WiFi off, 45s total | Paths on all ifaces build? Path migrated? |
| 04.06 18:38 | I11CM0093 & I11CM0095 | Test Acc. -> Personal Acc. | My Account: WiFi (HHG) (->off->on) + Cellular, Test Account: Cellular | **Video Call**, Two paths build? Path Migration? *Changed to previous tests: Turning My Account WiFi off and back on* | 15s after call accepted WiFi off, 15s later WiFi on, 45s total | Repeated probing? |
| 04.06 18:55 | I11CM0093 & I11CM0095 | Test Acc. -> Personal Acc. | My Account: WiFi (HHG) (->off->on) + Cellular, Test Account: Cellular | **Video Call**, Two paths build? Path Migration? *Changed to previous tests: Turning My Account WiFi off and back on* | 15s after call accepted WiFi off, 15s later WiFi on, 45s total | Repeated probing? |
| 04.06 18:57 | I11CM0093 & I11CM0095 | Test Acc. -> Personal Acc. | My Account: WiFi (HHG) (->off->on) + Cellular, Test Account: Cellular | **Video Call**, Two paths build? Path Migration? *Changed to previous tests: Turning My Account WiFi off and back on* | 15s after call accepted WiFi off, 15s later WiFi on, 45s total | Repeated probing? |
| 05.06 09:15 | I11CM0093 & I11CM0095 | Test Acc. -> Personal Acc. | My Account: WiFi (Adapter with Internet) (->off->on) + Cellular, Test Account: Adapter + Cellular | **Video Call**, Finding local Path? *Changed to previous tests: Both connected to local AP* | 15s after call accepted WiFi off, 15s later WiFi on, 45s total | Probing on local path after re-connection? Finding this path? |
| 05.06 09:41 | I11CM0093 & I11CM0095 | Test Acc. -> Personal Acc. | My Account: WiFi (Adapter with Internet) (->off->on) + Cellular, Test Account: Adapter + Cellular | **Video Call**, Finding local Path? *Changed to previous tests: Both connected to local AP* | 15s after call accepted WiFi off, 15s later WiFi on, 45s total | Problems with My Account capture (stopped before the end) |
| 05.06 09:45 | I11CM0093 & I11CM0095 | Test Acc. -> Personal Acc. | My Account: WiFi (Adapter with Internet) (->off->on) + Cellular, Test Account: Adapter + Cellular | **Video Call**, Finding local Path? *Changed to previous tests: Both connected to local AP* | 15s after call accepted WiFi off, 15s later WiFi on, 45s total | Problems with My Account capture (stopped before the end, _2 pcap file before WiFi on) |


## Analysis
This section contains the conclusions and analysis of our testing for the different apps.

| Application | Tests Considered | Test | Observation | Special Attributes |
| --- | --- | --- | --- | --- |
| WhatsApp Video Call | 04.06 11:12-15:42 | WiFi Path Probing | Performed for Local WiFi (direct path + TURN server), always the same port | TURN server unknown **attributes** (allocation, probably mapping WA call), Local WiFi plain STUN request (0x0001; 0x0101) without ANY **attributes** besides integrity
| WhatsApp Video Call | 04.06 11:12-15:42 | Cellular Path Probing | Not probed, Path MTU Probe to idle TURN server address seen >33s after call start, every 50ms, total 10 times, only once on one phone | Probing on idle cellular path with message type 0x0801 (path MTU discovery), attribute 0x4003 (unknown), server responds with message type 0x0802 (path MTU report) attributes 0x4002 (unknown) and 0x4003 (unknown) |
| WhatsApp Video Call | 04.06 11:12-15:42 | Path Building Time | TURN server path, build for initial exchange: <100ms | --- |
| WhatsApp Video Call | 04.06 11:12-15:42 | Path Building Time | Local WiFi path, ~400-1000ms after call started (depending on side, callee takes longer), Probing **ENDS** after one path is successfully found, Only after active path down switching and re-gathering, max. probes 20  | --- |
| WhatsApp Video Call | 04.06 11:12-15:42 | Idle Path Maintenance | Actively probed with STUN every ~1s (TURN server path) | **Message type** 0x0801 (path MTU discovery) from client, **message type** 0x0802 (path MTU report) from server |
| WhatsApp Video Call | 04.06 11:12-15:42 | Active Path Maintenance | Half as frequently probed. First probe after 15.4s, then every 2s | Callee makes binding request **message type** (0x0001), Priority **attribute** set to 1, caller replies binding success (0x0101) and same priority |
| --- | --- | --- | --- | --- |
| WhatsApp **Audio** Call | 04.06 11:14 | Different Behavior | Local Path after 13.2, then every 2s, otherwise identical | Initial STUN binding include message type 0x0003 allocation request, attribute 0x4000, new attribute 0x4024 (unknown) |
| --- | --- | --- | --- | --- |
| WhatsApp Video Call | 04.06 16:08-16:14 | Non-local Path only, General | General structure identical, Test Account uses cellular iface + IPv6 | No new attributes observed |
| WhatsApp Video Call | 04.06 16:08-16:14 | Non-local Path only, Cellular to WiFi Path Probing | Cellular uses IPv4 and IPv6, always the same Src. port!, probing external IPv4 of eduroam 11-12 times, every 3s, mobile of My Account **NEVER** probed,    | Plain STUN request 0x0001 with message integrity |
| WhatsApp Video Call | 04.06 16:08-16:14 | Non-local Path only, WiF to Cellular Path Probing | Probing all 600ms for Telekom endpoint, 20 STUN packets, 10s | Plain STUN request 0x0001 with message integrity |
| WhatsApp Video Call | 04.06 16:08-16:14 | Non-local Path only, Path Building Time | Direct Path **NOT** found, Probing ~10s for direct path, 15-20 STUN packets, relayed path used, no re-gathering | No direct STUN packet arrived at Test Account, no direct STUN packet arrived at My Account |
| WhatsApp Video Call | 04.06 17:07 | Non-local Path only, **WiFi has external IPv6**, Path Probing | Simple STUN on IPv6 addresses, IPv4 **NOT** found with 12 STUN packet sent, stop probing for new path after IPv6 found, IPv6 of Cellular on My Account **NOT** probed | Plain STUN with message integrity |
| WhatsApp Video Call | 04.06 17:07 | Non-local Path only, **WiFi has external IPv6**, TURN Allocation | First IPv4, IPv6 only STUN no allocation | IPv4 same as before, IPv6 no allocation, only plain STUN |
| WhatsApp Video Call | 04.06 17:07 | Non-local Path only, WiFi has external IPv6, Path Maintenance | Simple STUN after 15s, then every 2s for active path, every 1s for idle path | Plain STUN binding request 0x0001 response 0x0101 with priority att. 1 |
| WhatsApp Video Call | 04.06 17:07 | Non-local Path only, WiFi has external IPv6, Path Building Time | Direct Path found ~600ms after call start | --- |
| --- | --- | --- | --- | --- |
| WhatsApp Video Call | 04.06 17:30-17:34 | Cellular, General | If not listed, only confirmed from before | General behavior, timings, etc. identical to before |
| WhatsApp Video Call | 04.06 17:30-17:34 | Cellular, Path Probing | STUN requests, IPv4 preferred, IPv6 to Telekom first not received! IPv4 path **NOT** found | Plain STUN with request response and integrity |
| WhatsApp Video Call | 04.06 17:30-17:34 | Cellular, Path Building Time | ~600ms for IPv6 | --- |
| WhatsApp Video Call | 04.06 17:30-17:34 | Cellular, Path Maintenance | First pause 14.7s, then every 2s, idle path every 1s | As before, plain STUN with prio. 1 on active path, idle path is 0x0802 path MTU probe with 0x0802 path MTU report message type return |
| --- | --- | --- | --- | --- |
| WhatsApp Video Call | 04.06 18:09-18:14 | Cellular+WiFi IPv6 to Cellular **Migration Test**, Path Building | Only IPv6 WiFi to IPv6 cellular found, 12 probings from My Account to Telekom, IPv4 **NOT** found, Telefonica public IPv6 not probed only Telekom one probed (probably not announced); Cellular path on My Account is only build after the WiFi interface is down with same procedure as before | Same plain STUN as before |
| WhatsApp Video Call | 04.06 18:09-18:14 | Cellular+WiFi IPv6 to Cellular **Migration Test**, Path Migration | No migration, after connection loss switch to TURN server on both sides. No more probing attempts only path maintenance | --- |
| WhatsApp Video Call | 04.06 18:09-18:14 | Cellular+WiFi IPv6 to Cellular **Migration Test**, Interruption | Roughly 500ms to build new cellular path for device that switches WiFi off | --- |
| --- | --- | --- | --- | --- |
| WhatsApp Video Call | 04.06 18:38-18:57 | WiFi off->on **Migration Test**, Path Building | Initially on IPv6 WiFi -> Cellular, after WiFi off probing IPv6 Cellular o2 -> Telekom 6 times, but **NOT** found, IPv4 to TURN probed as soon as WiFi interface up, path switched to this relay path | STUN probes plain requests |
| WhatsApp Video Call | 04.06 18:38-18:57 | WiFi off->on **Migration Test**, Path Migration | No **real** migration, rebuilding path when WiFi interface back up, reusing identifiers from beginning of connection (allocations?), rest similar | --- |
| --- | --- | --- | --- | --- |
| WhatsApp Video Call | 05.06 09:15-09:45 | Local WiFi off->on **Migration Test**, Path Building | First TURN, then local, no cellular until WiFi off | --- |
| WhatsApp Video Call | 05.06 09:15-09:45 | Local WiFi off->on **Migration Test**, Path Migration | On WiFi down, switch to TURN relay via cellular interface, have to build path first (not established), building takes ~500ms, on WiFi up building TURN relay via WiFi and probing local Link but no answer and no switch to local path | --- |
| WhatsApp Video Call | 05.06 09:15-09:45 | Local WiFi off->on **Migration Test**, Path Probing after Interface change | Only phone with iface change probes STUN, other phone no response (**even though STUN is received!**), local path is **NOT** found again, only relay after connection break | --- |
| --- | --- | --- | --- | --- |

### General Flow
The default flow of WhatsApp Video Calls. For audio calls different!

Both in the same local WiFi AP

Caller:
1. TCP connection to WhatsApp (XMPP ports)
2. Probably SIP or other protocol to exchange call information via TCP
3. Reserve resources on Facebook TURN servers (always same port)
4. Success responses from the TURN servers
5. First data is transferred via TURN servers
6. Accept (or send) and return STUN Binding request (Binding Success, Binding request)
7. Exchange data via local WiFi AP
8. Sometimes exchange with Facebook TURN via TCP
9. Respond to local STUN binding refresh
10. Ending call
11. ICMP unreachable received
12. De-allocate STUN bindings on servers

Callee:
1. TCP Connection to WhatsApp (XMPP ports)
2. Receive call information via TCP
3. Reserve resources on Facebook TURN servers
4. Success responses from the TURN servers
5. First data is transferred via TURN servers
6. Send (or accept) Local STUN Binding request
7. Exchange data via local WiFi AP
8. Sometimes exchange with Facebook TURN via TCP
9. (Only in one tests) Make PATH MTU probe on cellular path towards Facebook TURN server, but don't use path
10. Send local STUN binding refresh
11. Ending call
12. ICMP unreachable received
13. De-allocate STUN bindings on servers


### Notes
During the analysis the following interesting information were found (for video calls):

- WhatsApp uses an unknown STUN attribute 0x4000. This attribute is in the range of non-optional attributes, but must not be registered by the IETF, rather by expert review (aka. should not be assigned by others). The purpose of this attribute is unclear
- 0x4000 is send at the beginning and end of the call, probably free the allocations, including a 150 byte identifier?
- Further attributes 0x4002, 0x4003, 0x4004, 0x4005, 0x4007, 0x4024 are observed but unclear what they mean
- 0x4002 is 8 bytes and corresponds with the TURN server address, for the same server it is the same in the response
- 0x4003 is observed on cellular link and WiFi at beginning of connection, probably telling that some mapping did not work? Length 9 byte on cellular later in connection, 1 byte on wifi with value 0xFF (-1 == error or not existent?) from server
- 0x4004 is padding of 452 bytes 0?
- 0x4007 is 2 bytes and in our case **always** 01f4 == 500
- Message Types 0x0801 and 0x0802, 0x0805 are observed
- 0x0801 has class request b00 and method 0x201, 0x0802 has class request b00 and method 0x202, 0x0805 has class b00 request and method 0x205
- All in value range where non-optional and assigned by IETF
- 0x801 is path MTU probe (Changed the delay between Probe indication and Report request to be RTO/2 or 50 milliseconds) confirmed above
- 0x802 is path MTU report

---
Audio calls have different attributes
- 0x4024 observed
---
- Cellular one sided constantly switches between IPv4 and IPv6 (IPv4 mapped into IPv6), native IPv6 only for STUN
- Once STUN on loopback?
- Rapid and seamless switching between TURN endpoints in a **single** connection. Once Fra5, then the next chunk ams4, then back to fra, then muc...
