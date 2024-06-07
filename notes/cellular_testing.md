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
| WhatsApp | 04.06.2024 | 2* Pixel 2 XL; I11CM0093 & I11CM0095 | I11CM0093: Telekom & I11CM0095: sim.de (carrier was o2) | WhatsApp: 2.24.10.85 & 2.24.10.85; Magisk 27.0 & 27.0; ADB_ROOT v1 & v1 | My Google Account & MT Google Account | Different Access Technologies (WiFi, WiFi & Cellular, Cellular); Path Building; Path Migration; Path Finding |
| WhatsApp | 05.06.2024 | 2* Pixel 2 XL; I11CM0093 & I11CM0095 | I11CM0093: Telekom & I11CM0095: sim.de (carrier was o2) | WhatsApp: 2.24.10.85 & 2.24.10.85; Magisk 27.0 & 27.0; ADB_ROOT v1 & v1 | My Google Account & MT Google Account | WiFi & Cellular: Path Migration |
| QuickShare | 05.06.2024 | 2* Pixel 2 XL; I11CM0093 & I11CM0095 | I11CM0093: Telekom & I11CM0095: sim.de (carrier was o2) | QuickShare ?; Play Store: 41.2.21-29 & 41.2.21-29 Magisk 27.0 & 27.0; ADB_ROOT v1 & v1 | My Google Account & MT Google Account | Default Behavior (With WiFi, Without WiFi) |
| QuickShare | 06.06.2024 | Motorola G54 5G; 2* Pixel 2 XL; I11CM0093 & I11CM0095 | I11CM0093: Telekom & I11CM0095: sim.de (carrier was o2) | QuickShare ?; Files: ; Play Store: 41.2.21-31 & 41.2.21-29 & 41.2.21-29; Magisk 27.0 & 27.0; ADB_ROOT v1 & v1 | My Google Account & My Google Account & MT Google Account | Sharing small files, sharing between own devices (only single device captured) |
| ICE Prototype | 06.06.2024 | Laptop & Desktop | Laptop: sim.de (carrier was o2) & Desktop: Telekom (via Tethering from Pixel 2 Test Account) | quicheperf commit 9084207d | Laptop: Client & Desktop: Server | Testing connection building, local path via LAN is initial one, cellular should be build |
| --- | --- | --- | --- | --- | --- |

# ICE Prototype
Test Notes:

| Time | Test | Devices | Direction | Connectivity | Data Size | Status | Test Description | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 06.06 11:30 | ICE Prototype \w both cellular | Laptop & Desktop | Laptop (Client) -> Desktop (Server) | Laptop: Ethernet LAN + Cellular & Desktop: Ethernet LAN + Cellular (tethered) | Duration max. 100s | Failure | Start on local path, search for path on cellular | Ethernet Path prio is too high, all probes are sent on the ethernet path |
| 06.06 11:46 | ICE Prototype \w both cellular | Laptop & Desktop | Laptop (Client) -> Desktop (Server) | Laptop: Ethernet LAN + Cellular & Desktop: Ethernet LAN + Cellular (tethered) | Duration max. 100s | Failure | Start on local path, search for path on cellular | STUN now observed outgoing on both cellular paths, but never observed incoming on cellular paths |
| 06.06 11:59 | ICE Prototype \w both cellular | Laptop & Desktop | Laptop (Client) -> Desktop (Server) | Laptop: Ethernet LAN + Cellular & Desktop: Ethernet LAN + Cellular (tethered) | Duration max. 100s | Failure | Start on local path, search for path on cellular | Same problem with metric as before |
| 06.06 12:05 | ICE Prototype \w both cellular | Laptop & Desktop | Laptop (Client) -> Desktop (Server) | Laptop: Ethernet LAN + Cellular & Desktop: Ethernet LAN + Cellular (tethered) | Duration max. 100s | Failure | Start on local path, search for path on cellular |  |
| 06.06 12:09 | ICE Prototype \w both cellular | Laptop & Desktop | Laptop (Client) -> Desktop (Server) | Laptop: Ethernet LAN + Cellular & Desktop: Ethernet LAN + Cellular (tethered) | Duration max. 100s | Failure | Start on local path, search for path on cellular | Again not found |
| 06.06 12:12 | ICE Prototype \w both cellular | Laptop & Desktop | Laptop (Client) -> Desktop (Server) | Laptop: Ethernet LAN + Cellular & Desktop: Ethernet LAN + WiFi (HHG) (tethered) | Duration max. 100s | Failure | Start on local path, search for path on cellular | Again not found |
| 06.06 14:07 | ICE Prototype \w both cellular | Laptop & Desktop | Laptop (Client) -> Desktop (Server) | Laptop: Ethernet LAN + Cellular & Desktop: Ethernet LAN + Cellular (tethered) | Duration max. 100s | Failure | Confirm before | Both Cellular STUN probes do not reach the other endpoint |
| 06.06 14:15 | ICE Prototype \w both cellular | Laptop & Desktop | Laptop (Client) -> Desktop (Server) | Laptop: Ethernet LAN + Cellular & Desktop: Ethernet LAN + WiFi (HHG) (tethered) | Duration max. 100s | Failure | Confirm o2 blocking STUN | Using Ethernet route instead of handy, might block incoming STUN |
| 06.06 14:21 | ICE Prototype \w both cellular | Laptop & Desktop | Laptop (Client) -> Desktop (Server) | Laptop: Ethernet LAN + Cellular & Desktop: Ethernet LAN + WiFi (HHG) (tethered) | Duration max. 100s | Failure | Confirm o2 blocking STUN | Confirmed before with correct routes |
| 06.06 14:27 | ICE Prototype \w both cellular | Laptop & Desktop | Laptop (Client) -> Desktop (Server) | Laptop: Ethernet LAN + WiFi (HHG) & Desktop: Ethernet LAN + Cellular (tethered) | Duration max. 100s | Failure | Confirm Telekom blocking STUN | --- |
| 06.06 14:30 | ICE Prototype \w both cellular | Laptop & Desktop | Laptop (Client) -> Desktop (Server) | Laptop: Ethernet LAN + WiFi (HHG) & Desktop: Ethernet LAN + Cellular (tethered) | Duration max. 100s | Failure | Confirm Telekom blocking STUN | Confirmed before |
| 06.06 14:45 | ICE Prototype \w both cellular | Laptop & Desktop | Laptop (Client) -> Desktop (Server) | Laptop: Ethernet LAN + Cellular & Desktop: Ethernet LAN + Cellular (tethered) | Duration max. 100s | Failure | Confirm ISPs blocking STUN | Setting 0x40 in first byte of STUN packets to known cellular addresses, problems with route again |
| 06.06 14:50 | ICE Prototype \w both cellular | Laptop & Desktop | Laptop (Client) -> Desktop (Server) | Laptop: Ethernet LAN + Cellular & Desktop: Ethernet LAN + Cellular (tethered) | Duration max. 100s | Failure | Confirm ISPs blocking STUN | Setting 0x40 in first byte of STUN packets to known cellular addresses |
| 06.06 14:58 | ICE Prototype \w both cellular | Laptop & Desktop | Laptop (Client) -> Desktop (Server) | Laptop: Ethernet LAN + Cellular & Desktop: Ethernet LAN + Cellular (tethered) | Duration max. 100s | Failure | Confirm ISPs blocking STUN | Setting 0x40 in first byte of STUN packets to known cellular addresses, overwrite 2 bytes of magic cookie |
| 06.06 15:19 | ICE Prototype \w both cellular | Laptop & Desktop | Laptop (Client) -> Desktop (Server) | Laptop: Ethernet LAN + Cellular & Desktop: Ethernet LAN + WiFi (HHG) (tethered) | Duration max. 100s | Failure | Confirm ISPs blocking STUN | Setting 0x40 in first byte of STUN packets to known cellular addresses, overwrite 2 bytes of magic cookie |
| 06.06 15:32 | ICE Prototype \w both cellular | Laptop & Desktop | Laptop (Client) -> Desktop (Server) | Laptop: Ethernet LAN + WiFi (HHG) & Desktop: Ethernet LAN + Cellular (tethered) | Duration max. 100s | Failure | Confirm ISPs blocking STUN | Default STUN behavior, blocked |
| 06.06 15:43 | ICE Prototype \w both cellular | Laptop & Desktop | Laptop (Client) -> Desktop (Server) | Laptop: Ethernet LAN + WiFi (HHG) & Desktop: Ethernet LAN + Cellular (tethered) | Duration max. 100s | Failure | Confirm ISPs blocking STUN | Setting 0x40 in first byte of STUN packets to known cellular addresses, overwrite 2 bytes of magic cookie to confirm STUN blocked |
| 06.06 15:52 | ICE Prototype \w both cellular | Laptop & Desktop | Laptop (Client) -> Desktop (Server) | Laptop: Ethernet LAN + Cellular (HHG) & Desktop: Ethernet LAN + WiFi (HHG) (tethered) | Duration max. 100s | Failure | Confirm ISPs blocking STUN | Setting 0x40 in first byte of STUN packets to known cellular addresses, overwrite 2 bytes of magic cookie to confirm STUN blocked |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Analysis
The analysis for the ICE prototype.

| Tests Considered | Status | Characteristics Analyzed | Findings | Notes |
| --- | --- | --- | --- | --- |
| 06.06 11:30 | Failure | Path Probing | Ethernet Priority is too high, all STUN probings are sent on the ethernet path with Cellular never found | For next tests reduce ethernet path prio below cellular prio |
| 06.06 11:46-14:07 | Failure | Path Probing | STUN probes sent on cellular path but never received on cellular path | Carriers might block STUN IPv4? |
| 06.06 14:15-14:21 | Failure | Path Probing | Confirmed o2 STUN not arriving | Carriers blocks STUN IPv4? |
| 06.06 14:27-14:30 | Failure | Path Probing | Confirmed Telekom STUN not arriving | Carriers blocks STUN IPv4? |
| 06.06 14:45-15:52 | Failure | Confirm STUN blocked | With STUN or random UDP still blocked, even if only a single side is behind carrier | Carrier blocks IPv4 P2P |
| --- | --- | --- | --- | --- |


# QuickShare
Test Notes:
- Location enabled on all devices in every test
- Configuration options regarding Cellular are removed

| Time | Test | Devices | Direction | Connectivity | Data Size | Status | Test Description | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 05.06 10:35 | QuickShare \w WiFi | I11CM0093 & L11CM0095 | My Account -> Test Acc. | Both WiFi (HHG) + Bluetooth + Cellular | 35MB | Failed | Enabled Bluetooth, **Visibility contacts**, Start Transfer, Timeout, Failed but TCP was gracefully finished? | Devices are directly next to each other and no changes to the network were done |
| 05.06 10:46 | QuickShare \w WiFi | I11CM0093 & L11CM0095 | My Account -> Test Acc. | Both WiFi (Local AP \w Internet) + Bluetooth + Cellular | 35MB | Success | Bluetooth already enabled, **Visibility contacts**, Start Transfer | Devices are directly next to each other and no changes to the network were done |
| 05.06 12:10 | QuickShare \w WiFi | I11CM0093 & L11CM0095 | My Account -> Test Acc. | Both WiFi (Local AP \w Internet) + Bluetooth + Cellular | 35MB | Success | Bluetooth already enabled, **Visibility contacts**, Start Transfer | Devices are directly next to each other and no changes to the network were done |
| 05.06 15:16 | QuickShare \w WiFi | I11CM0093 & L11CM0095 | My Account -> Test Acc. | Both WiFi (Local AP \w Internet) + Bluetooth + Cellular | 35MB | Success | Bluetooth already enabled, **Visibility contacts**, Start Transfer next to each other | ~7000 and ~3000 packets dropped by kernel? |
| 05.06 15:21 | QuickShare \w WiFi | I11CM0093 & L11CM0095 | My Account -> Test Acc. | Both WiFi (Local AP \w Internet) + Bluetooth + Cellular | 35MB | Success | Bluetooth already enabled, **Visibility contacts**, Start Transfer next to each other | Less loss, File deleted before transfer |
| 05.06 15:27 | QuickShare \w WiFi | I11CM0093 & L11CM0095 | My Account -> Test Acc. | Both WiFi (HHG) + Bluetooth + Cellular | 35MB | Success | Bluetooth already enabled, **Visibility contacts**, Start Transfer next to each other | No TCP start exchange seen? No ICMP Pings before transfer |
| 05.06 15:58 | QuickShare \w WiFi | I11CM0093 & L11CM0095 | My Account -> Test Acc. | Both WiFi (HHG) + Bluetooth + Cellular | 35MB | Success | Bluetooth already enabled, **Visibility contacts**, Start Transfer next to each other | Slower than usual, interrupted in transfer shortly (without changes in test config) |
| 05.06 16:28 | QuickShare \wo WiFi | I11CM0093 & L11CM0095 | My Account -> Test Acc. | Bluetooth + Cellular | 35MB | Success | Bluetooth already enabled, **Visibility contacts**, Start Transfer next to each other | QuickShare asks for WiFi enabled on sender, allowed |
| 05.06 16:58 | QuickShare \w WiFi | I11CM0093 & L11CM0095 | My Account -> Test Acc. | WiFi (Test: HHG & My: Adapter) + Bluetooth + Cellular | 35MB | Success | Bluetooth already enabled, **Visibility contacts**, Start Transfer next to each other in different WiFis | Switched WiFi off mid transfer, afterwards transfer is faster |
| 05.06 17:11 | QuickShare \w WiFi | I11CM0093 & L11CM0095 | My Account -> Test Acc. | WiFi (Test: HHG & My: Adapter) + Bluetooth + Cellular | 35MB | Success | Bluetooth already enabled, **Visibility contacts**, Start Transfer next to each other in different WiFis | Confirm findings from before |
| 05.06 17:21 | QuickShare \w WiFi | I11CM0093 & L11CM0095 | My Account -> Test Acc. | WiFi (Test: HHG & My: Adapter) + Bluetooth + Cellular | 35MB | Success | Bluetooth already enabled, **Visibility contacts**, Start Transfer next to each other in different WiFis | Confirm findings from before |
| 05.06 17:34 | QuickShare \wo WiFi | I11CM0093 & L11CM0095 | My Account -> Test Acc. | Bluetooth + Cellular | 35MB | Success | Bluetooth already enabled, **Visibility contacts**, Start Transfer next to each other, WiFi off on both devices | Deny WiFi on sender |
| 05.06 17:50 | QuickShare \wo WiFi | I11CM0093 & L11CM0095 | My Account -> Test Acc. | Bluetooth + Cellular | 35MB | Success | Bluetooth already enabled, **Visibility contacts**, Start Transfer next to each other, WiFi off on both devices, moving away from sender with receiver | Not far enough |
| 05.06 17:58 | QuickShare \wo WiFi | I11CM0093 & L11CM0095 | My Account -> Test Acc. | Bluetooth + Cellular | 35MB | Success | Bluetooth already enabled, **Visibility contacts**, Start Transfer next to each other, WiFi off on both devices, moving away from sender with receiver | Again, not far enough (end of terrace) |
| 05.06 18:07 | QuickShare \wo WiFi | I11CM0093 & L11CM0095 | My Account -> Test Acc. | Bluetooth + Cellular | 35MB | Failure | Bluetooth already enabled, **Visibility contacts**, Start Transfer next to each other, WiFi off on both devices, moving away from sender with receiver | Moving too far interrupts transfer, Cellular doesn't seem to be used |
| 05.06 18:22 | QuickShare \wo WiFi | I11CM0093 & L11CM0095 | My Account -> Test Acc. | WiFi (HHG) + Bluetooth + Cellular | 35MB | Failure | Bluetooth already enabled, **Visibility contacts**, Start Transfer next to each other, WiFi off on both devices, moving away from sender with receiver | Moving too far interrupts transfer, Cellular doesn't seem to be used |
| 05.06 18:33 | QuickShare \wo WiFi | I11CM0093 & L11CM0095 | My Account -> Test Acc. | Bluetooth + Cellular | 35MB | Failure | Bluetooth already enabled, **Visibility contacts**, Start Transfer next to each other, WiFi off on both devices, moving away from sender with receiver | Moving too far interrupts transfer, Cellular doesn't seem to be used |
| 05.06 19:32 | QuickShare \w WiFi | I11CM0093 & L11CM0095 | My Account -> Test Acc. | WiFi (HHG) + Bluetooth + Cellular | 35MB | Failure | Bluetooth already enabled, **Visibility contacts**, Start Transfer next to each other, WiFi on both devices | Trying to reproduce transfer via AP, success, but receiver went offline? |
| 05.06 19:40 | QuickShare \w WiFi | I11CM0093 & L11CM0095 | My Account -> Test Acc. | WiFi (HHG) + Bluetooth + Cellular | 35MB | Success | Bluetooth already enabled, **Visibility contacts**, Start Transfer next to each other, WiFi on both devices | Reproduce results, if moving phones apart at the beginning of connection, switch to AP? Fin other AP |
| 05.06 19:43 | QuickShare \w WiFi | I11CM0093 & L11CM0095 | My Account -> Test Acc. | WiFi (HHG) + Bluetooth + Cellular | 35MB | Success | Bluetooth already enabled, **Visibility contacts**, Start Transfer next to each other, WiFi on both devices | Reproduce results, Not moving at beginning |
| 05.06 19:46 | QuickShare \w WiFi | I11CM0093 & L11CM0095 | My Account -> Test Acc. | WiFi (HHG) + Bluetooth + Cellular | 35MB | Success | Bluetooth already enabled, **Visibility contacts**, Start Transfer next to each other, WiFi on both devices | Reproduce results, Moving at beginning |
| 05.06 19:49 | QuickShare \w WiFi | I11CM0093 & L11CM0095 | My Account -> Test Acc. | WiFi (HHG) + Bluetooth + Cellular | 35MB | Success | Bluetooth already enabled, **Visibility contacts**, Start Transfer next to each other, WiFi on both devices | Reproduce results, Moving at beginning |
| 05.06 19:57 | QuickShare \w WiFi | I11CM0093 & L11CM0095 | My Account -> Test Acc. | WiFi (HHG) + Bluetooth + Cellular | 35MB | Success | Bluetooth already enabled, **Visibility everyone** | Anything different from before? |
| 06.06 10:47 | QuickShare \w WiFi | Motorola &  L11CM0095 | My Account (Moto) -> My Account | WiFi (HHG) + Bluetooth | 2MB | Success | Bluetooth already enabled, **Visibility own devices** | Behavior of sharing between own devices |
| 06.06 11:04 | QuickShare \w WiFi | Motorola &  L11CM0095 | My Account (Moto) -> My Account | WiFi (HHG) + Bluetooth + (Moto) Cellular | 35MB | xx | Bluetooth already enabled, **Visibility own devices** | Sharing to Pixel larger file, moving apart after start and switch AP |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Analysis
The Analysis of the tests before

| Tests Considered | Status | Characteristics Analyzed | Findings | Notes |
| --- | --- | --- | --- | --- |
| 05.06 10:35 | Failed | Robustness | Fails even under perfect conditions, with TCP closing gracefully? | Using TCP, no migration is possible. Packet or data inspection which *could* fail? |
| 05.06 10:35 | Failed | Default Behavior | When connected to 10.0.0.0/8 WiFi sometimes using TCP via AP to share data, no WiFi Hotspot, Cellular Data not considered on default | Fails |
| 05.06 10:46-12:10 | Success | Default Behavior | When in 192.168.0.0/16 network, using TCP via WiFi-Hotspot (Device AP) to share data | Transfer not encrypted, fast & successful |
| 05.06 10:46-12:10 | Success | Transfer Speed | Via WiFi-Hotspot fast, via AP slower | --- |
| 05.06 10:46-12:10 | Success | Path Building | Using mDNS in local network to find other peer, testing connection with ICMP ping, no STUN used | Only in local AP adapter mDNS etc. |
| 05.06 15:27-15:58 | Success | Path Building | mDNS + TCP + ICMP is not always observed when in 10.0.0.0/24 HHG network | Transfer is encrypted via AES-256-CRC (exchanged parameter) |
| 05.06 16:58-17:21 | Success | Path Building | Exchange with Google after failed mDNS (trying >10s), *must contain WiFi IP*, trying TCP directly to WiFi IP (different WiFi), **fails**, no STUN no path building, takes >35-50s to shut down WiFi and switch to WiFi-Hotspot with one phone being AP | Transfer is slow at first, then WiFi turned off in top bar, then faster |
| 05.06 17:30-17:34 | Success | Path Building | Building WiFi-Hotspot, without DHCP, then mDNS and TCP again | Transfer is fast |
| 05.06 17:50-18:33 | Failure | Migration | Building WiFi-Hotspot, increase distance between devices, transfer stops, no cellular data used, failed after 20-30s | WiFi not enabled but also no probing on cellular performed |
| 05.06 18:22 | Failure | Migration | WiFi connectivity doesn't make a difference, no path being build, no migration | Both in WiFi, moving into different WiFi but no more connection |
| 05.06 19:32-19:49 | Success/Failure | Path Building | If moving the devices before the data transfer apart, using WiFi AP route, otherwise using WiFi-Hotspot | This is not always 100% reliable but my best explanation, sometimes still enabling the WiFi-Hotspot communication |
| 05.06 19:57 | Success | General Behavior of Everyone Mode | Can use mDNS and WiFi AP without WiFi-Hotspot, when closer? also WiFi-Hotspot |  |
| 06.06 10:47 | Success | Sharing between own devices | Using same AP path as before, same mechanisms as before | Small file, directly shared via AP, different section in UI to select own devices, doesn't show up in devices nearby section |
| 06.06 11:04 | Failure | Sharing between own devices | Using same AP path as before when moving apart fails and no path is found | No different behavior than sharing between contacts or other devices |
| --- | --- | --- | --- | --- |

### General Flow
The default flow of QuickShare transfers. Depends on the connection status

(If connected to WiFi)

0. Exchange with google contains infos like local IP...
1. Receiver starts mDNS discovery in local Network asking for \<unknown strings\>_tcp.local (IPv4 & IPv6); This is tried 
2. Sender responds with only the second part of the string
3. Sender sends 2 ICMP ping to receiver (ttl=64) resulting in ARP
4. Receiver responds with 2 ICMP echo replies ttl=64
5. Sender builds TCP connection to receiver
6. Initial data like Phone Name, etc are exchanged **in plaintext**

*Start of transfer*

7. Then, the sender builds a WiFi-Direct network
8. Sender offers DHCP IPv4 to receiver and therefore knows the IP of the other end
9. Transfer is performed on this direct channel with new IPv4 (**not encrypted**, PDF can be restored with actual number of pages but currently blank due to some error I didn't look into)
10. TCP connection is gracefully closed with Fin/Fin Ack


# WhatsApp

Test notes:
- The local AP only supported IPv4, no IPv6 (DHCP Server)
- All tests muted (in video call and audio call)
- Moving hand in front of camera to induce data transfer
- Ring 3 times before accept

## Tests
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
| WhatsApp Video Call | 05.06 09:15-09:45 | Local WiFi off->on **Migration Test**, Path Migration | On WiFi down, switch to TURN relay via cellular interface, have to build path first (not established), building takes ~500ms, on WiFi up building TURN relay via WiFi and probing local Link but no answer from established device, no switch to local path | --- |
| WhatsApp Video Call | 05.06 09:15-09:45 | Local WiFi off->on **Migration Test**, Path Probing after Interface change | Only phone with iface change probes STUN, other phone no response (**even though STUN is received!**), local path is **NOT** found again, only relay after connection break | Again, plain STUN |
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
- Cellular one sided constantly switches between IPv4 and IPv6 (IPv4 mapped into IPv6), native IPv6 only for STUN
- Once STUN on loopback?
- Rapid and seamless switching between TURN endpoints in a **single** connection. Once Fra5, then the next chunk ams4, then back to fra, then muc...
---
Audio calls have different attributes
- 0x4024 observed

