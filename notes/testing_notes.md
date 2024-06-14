# Information regarding the test
This file contains a mapping of file name to test

## File Transfer Information

| File | Size | Format |
| --- | --- | --- |
| Mitschrift | ~75mb | pdf |
| Android: 250 | ~250mb | pdf |
| Android: gba | ~33mb | gba |

## Testing output file info

| File | Connectivity | Test | Direction |
| --- | --- | --- | --- |
| Test Setup Zuhause | WiFi on/off | Migration durch bewegung | --- |
| cellular_close_far_close | WiFi (HHG) + Cellular (iphone) | Migration towards iCloud and back? Start QUIC AWDL,  | ipad -> iphone |
| --- | --- | --- | --- |
| gerät_18_01_10_57 | AWDL + WiFi | Verbindungsabbruch, seamless switch, iPad eduroam(wohnheim), iPhone eduroam, Conn established davor (2s nach start) | IPhone > IPad |
| gerät_18_01_11_07 | AWDL + WiFi | Verbindungsabbruch, kein zweiter Pfad, Was genau ist hier passiert? Iface down, WiFi down? | IPhone > IPad |
| gerät_18_01_11_12 | AWDL + WiFi | Kein Verbindungsabbruch | IPhone > IPad |
| gerät_18_01_11_14 | AWDL + WiFi | Verbindungsabbruch nach ~2s, kaum Daten via QUIC, warum? | IPhone > IPad |
| gerät_18_01_11_17 | AWDL + WiFi | Verbindungsabbruch nach ~2s, Fehler und manueller abbruch nach 6+ Minuten | IPhone > IPad |
| gerät_18_01_11_28 | AWDL + WiFi | Verbindungsabbruch nach ~2s, Fehler und manueller Abbruch | IPhone > IPad |
| gerät_18_01_11_35 | AWDL + WiFi | Verbindungsabbruch nach ~2s, schneller Abbruch führt zu schnellem wechsel auf en0, beispiel für fast seamless (600ms), benutzt ICMPv6 für Suche, findet per ICMPv6 ND beide fe80:: & 2001 Addressen, benutzt 2001:: warum ist unklar | IPhone > IPad |
| gerät_18_01_11_38 | AWDL + WiFi | Verbindungsabbruch nach ~2s, baut direkt Verbindung via EN0 auf, kein AWDL link benutzt, wahrscheinlich Signalqualität zu früh zu schlecht? | IPhone > IPad |
| gerät_18_01_11_40 | AWDL + WiFi | Verbindungsabbruch nach ~2s, braucht 400ms um abbruch zu bemerken, baut EN0 Verbindung neu auf | IPhone > IPad |
| gerät_18_01_11_44 | AWDL + WiFi | Verbindungsabbruch nach ~3s, im Trace nach ~6s, braucht ~4s um Verbindung via Wi-Fi zu finden, wieder per ICMPv6 und evtl. Apple? | IPhone > IPad |
| gerät_18_01_11_46 | AWDL + WiFi | Verbindungsabbrucsh nach ~3s, Versuche über AWDL, 8s Migration, not seamless | IPhone > IPad |
| gerät_18_01_11_48 | AWDL + WiFi | Verbindungsabbruch nach ~3s, ~3s Pause am Empfänger, diesmal direkter aufbau ohne ICMPv6  | IPhone > IPad |
| gerät_18_01_11_52 | AWDL + WiFi | Verbindungsabbruch nach ~3s, davor schon QUIC aufgebaut, scheint als wäre die Verbindung instabil geworden und es gab 600ms Pause auf Receiver Seite auf AWDL davor, also eher Switch trigger, nicht präventiv, dann aber seamless switch | IPhone > IPad |
| gerät_18_01_11_54 | AWDL + WiFi | Verbindungsabbruch nach ~3s, Tür offen nach ~20s, Beispiel für keine Migration zurück, TCP fliegt auf AWDL nachdem die Türe aufgeht, es wird nach dem Start kein zweiter (neuer) Pfad gebaut solange die Verbindung stabil ist | IPhone > IPad |
| gerät_18_01_11_57 | AWDL + WiFi | Verbindungsabbruch nach ~3s, Tür offen nach ~20s, QUIC auf AWDL überlebt die 20s sogar, aber wird kurz genutzt und dann abgebaut, Verbindung wieder schwach und neue aufgebaut bevor der eigentliche Wechsel stattfindet | IPhone > IPad |
| gerät_18_01_12_00 | AWDL + WiFi | Verbindungsabbruch nach ~3s, Tür offen nach ~20s, garkeine Verbindung auf AWDL gebaut wahrscheinlich die Tür also zu früh zu | IPhone > IPad |
| gerät_18_01_12_02 | AWDL + WiFi | Verbindungsabbruch nach ~3s, Tür offen nach ~30s (weil davor kein traffic) | IPhone > IPad |
| gerät_18_01_12_12 | AWDL + WiFi | Normal, Kein Internet | IPhone > IPad |
| gerät_18_01_12_13 | AWDL + WiFi | Normal, Kein Internet | IPhone > IPad |
| Pause | --- | --- |
| gerät_18_01_13_26 | AWDL + WiFi | Verbindungsabbruch nach ~3s | IPad > IPhone |
| gerät_18_01_13_28 | AWDL + WiFi | Verbindungsabbruch nach ~3s (davor einmal declined), Fehler beim 2. mal (iPhone kann keine Verbindung zu Apple aufbauen) | IPad > IPhone |
| gerät_18_01_13_35 | AWDL + WiFi | Verbindungsabbruch nach ~3s | IPad > IPhone |
| gerät_18_01_13_39 | AWDL + WiFi | Verbindungsabbruch nach ~3s, Türe auf nach 30s | IPad > IPhone |
| gerät_18_01_13_43 | AWDL + WiFi | Verbindungsabbruch nach ~3s | IPad > IPhone |
| gerät_18_01_13_47 | AWDL + WiFi | Verbindungsabbruch nach ~3s | IPad > IPhone |
| gerät_18_01_13_48 | AWDL + WiFi | Verbindungsabbruch nach ~4s, Türe auf nach ~10s | IPad > IPhone |
| gerät_18_01_13_50 | AWDL + WiFi | Verbindungsabbruch nach ~4s, Türe auf nach ~12s | IPad > IPhone |
| gerät_18_01_13_53| Verbindungsabbruch nach ~4s, Türe auf nach ~12s, keine Pakete zwischendrin | IPad > IPhone |
| gerät_18_01_13_55 | AWDL + WiFi | Verbindungsabbruch nach ~4s, Türe auf nach ~30s | IPad > IPhone |
| --- | --- | --- |
| Setup geändert | NearbyShare | --- |
| location_18_01_14_29 |  | Normaler Transfer, 250mb | Out > Box |
| location_18_01_14_35 |  | Normaler Transfer, 33mb | Out > Box |
| location_18_01_15_02 |  | Beide WLAN, Verbindungsabbruch nach ~5s, Abbruch, 33mb | Box > Out |
| location_18_01_15_04 |  | Beide WLAN, Verbindungsabbruch noch vor dem eigentlichen Transfer, Abbruch, 33mb | Box > Out |
| location_18_01_15_06 |  | Beide WLAN, Verbindungsabbruch nach ~10s, Abbruch, 33mb | Box > Out |
| --- | --- | --- |
| Nochmal iOS | IPad im Bayern WLAN | iPhone > iPad |
| gerät_18_01_15_16 |  | Verbindungsabbruch nach ~2s, beide unters. Netzwerke (iPhone Laptop, iPad Bayern WLAN), sendet NUR TCP via AWDL, keine Migration | iPhone > iPad |
| gerät_18_01_15_25 |  | Verbindungsabbruch nach ~2s, beide unters. Netzwerke (iPhone Laptop, iPad Bayern WLAN). Bricht einfach ab, Partner verschwindet aus dem AirDrop Menü, keine Fehlermeldung. | iPad > iPhone |
| gerät_18_01_15_28 |  | Verbindungsabbruch nach ~2s, beide unters. Netzwerke (iPhone Laptop, iPad Bayern WLAN). Bricht einfach ab, Partner verschwindet aus dem AirDrop Menü, keine Fehlermeldung. Wirklich abbruch? einziger test mit QUIC und unterschiedlichem WLAN | iPad > iPhone |
| ipad_iphone_cellular_close_far_close | | Verbindungsabbruch nach 20s (30s im capture), iPhone hat Cellular, Telefonica, iPad im WiFi; ABER: war das iPhone im Wifi? Müsste man testen... | iPad > iPhone |

## AirDrop Verhalten
Die folgende Tabelle fasst die wichtigsten Verhaltensmuster von AirDrop zusammen.

| Verhalten | Test | Bemerkungen | Problem |
| --- | --- | --- | --- |
| Verwendet QUIC | Senden direkt an die andere ID | --- | --- |
| Verwendet IPv6 | Unabhängig vom Test, es sei denn IPv6 funktioniert im Netzwerk nicht (Annahme) | Auf dem lokalen Link zwischen zwei Geräten funktioniert IPv6 natürlich immer, daher dort immer IPv6 | --- |
| Verwendet TCP | Senden an ein anderes Gerät, nicht die Apple ID | Kann auch passieren wenn beide Geräte nicht im selben WiFi sind (warum?) | Sobald TCP verwendet wird bricht der Transfer bei Verbindungsproblemen ab |
| Sucht Verbindungspartner mit MDNS | Auf Teilen per AirDrop klicken | Gilt sowohl per AWDL als auch WiFi (funktioniert nur wenn im selben Netzwerk) | Limitiert auf lokale Netzwerke |
| Migriert von AWDL auf WiFi | Beide Geräte sind im selben WiFi Netzwerk. Funktioniert ohne neuen Handshake, echte Migration. | Migration zurück nie gesehen | Es scheint dass ausschließlich die vorhandene Verbindung genutzt wird. Erst sobald diese abbricht wird gewechselt. AWDL überlebt teilweise Abbruch aber wird dann sogar abgebaut |
| Migriert **nicht** von AWDL auf WiFi in anderem Netzwerk | Beide Geräte in unterschiedlichen Netzwerken. Nimmt Hilfe von Apple Relay/Tunnel, 17.188... zur Hand, Sender baut Verbindung mit neuem Handshake auf. Wahrscheinlich sowas wie Out-Of-Band Information. | Transfer/Informationsquelle hat im Test nie funktioniert | Obwohl beide Geräte sich mit dem Relay verbinden scheint kein Transfer Zustande zu kommen. Außerdem senden die Geräte in diesem Test teilweise TCP |
| Migriert von AWDL auf Cellular | Kein WiFi wurde verwendet (deaktiviert). Neuer Handshake, keine echte Migration. | Zeigt in UI an dass mobile Daten verwendet werden | Migriert nicht mehr zurück. Verbraucht Datenvolumen obwohl das nicht notwendig ist |
| Migriert nicht mehr zurück | Nach Migration wird nicht mehr zurück gewechselt, auch wenn wieder Kontakt besteht | Betrifft AWDL -> WiFi & AWDL -> Cellular. Beides migriert nicht zurück. Austausch über AWDL per TCP kann beobachtet werden, aber kein Datentransfer. | Dadurch dass die Migration nur in eine Richtung funktioniert ist der Transfer langsamer als nötig |
| *Pause zwischen Migration* | Abhängig von Zustand/Scheduler: Wenn schon Daten übertragen wurden dann wahrscheinlicher, dass kleine Pause entsteht. Bei "neuer" Verbindung direkter Wechsel. | Teilweise auch Probleme in der Addressauflösung beobachtet. Dann wird ein "courier" Service verwendet. Nicht immer erfolgreich | Pause dadurch, dass kein Multi-Path verwendet wird. In Real-Time Scenarios ist die Pause nicht akzeptierbar |
| Verbindungsabbruch + Fehler | Immer dann wenn TCP verwendet wird und die Verbindung unterbrochen wird | Grund für die Verwendung unklar | TCP migriert nicht und kein Versuch die Verbindung erneut aufzubauen |

## NearbyShare Verhalten
Die folgende Tabelle beinhaltet alle Beobachtungen über NearbyShare die wir bisher haben.

| Verhalten | Test | Bemerkungen |
| --- | --- | --- |
| Verwendet TCP | Normaler Transfer | Das sendende Gerät stellt ein lokales WiFi-Netzwerk. Der Empfänger verbindet sich und empfängt Daten per TCP |
| Transfer dauert lange | Normaler Transfer zwischen zwei Handys. Beide sind im WiFi | Die Handys unterstützen keine zwei Verbindungen auf dem selben WiFi Interface. Daher wird wahrscheinlich Bluetooth oder noch langsamere Verbindung gewählt |
| Transfer zwischen mehreren Geräten gleichzeitig möglich | In der Auswahl auf alle verfügbaren Geräte klicken | Verwendet auch TCP. Overlay Struktur wahrscheinlich in Software |
| Verbindung bricht ab + Fehlermeldung | Keine Migration, auch nicht manuell. Sobald die Verbindung abbricht, wird kein Transfer mehr abgeschlossen | Nach einem Timeout erscheint immer ein Fehler. Auch nicht manuell über TCP und/oder Google Relay |
| Transfer auf dem Direktlink ist nicht verschlüsselt | Normaler Transfer | Kann die PDF aus dem Transfer auslesen und in eine funktionierende PDF verwandeln |

## Google Meet Verhalten

| Pakete | Endpunkt | Bemerkungen |
| --- | --- | --- |
| UDP | meet.google.com | Audio und Video Pakete kommen direkt von Google Server |
| STUN | 142.250.82.208 (angeblich in Japan) | Sehr wahrscheinlich von ICE. Und damit von WebRTC |
| TCP | Wieder direkt zu Google Servern / Addressen | Austausch von Nachrichten? |
| QUIC | Ebenfalls nur via Google | Austausch von Audio? |
| RTCP | ... | ... |

## Apple FaceTime Verhalten
Beide Geräte waren im selben WiFi Hotspot. Das iPad hat einen Anruf an das iPhone gestartet. Offiziell verwendet FaceTime eigentlich auch WebRTC, denn die rechtlichen Informationen auf der Website beinhalten diese Informationen: https://www.apple.com/de/legal/privacy/data/de/face-time/

| Dateiname | Test | Richtung |
| --- | --- | --- |
| facetime_23_01_10_26 | FaceTime Anruf 1:1, Beide im selben WiFi | iPad -> iPhone |
| facetime_23_01_10_28 | FaceTime Anruf 1:1, Beide im selben WiFi | iPhone -> iPad |
| facetime_23_01_10_31 | FaceTime Anruf 1:1, iPad wechselt WiFi. Erst lokal auf dem Laptop, dann im selben Wohnheimsnetz | iPhone -> iPad |
| iphone_face_time_migration_idle(_2) | Facetime Anfruf 1:1, beide im lokalen Wifi + iPhone im Cellular, 1min (2:20min im 2. File) idle, Pings/Keep-Alives im Cellular | iPhone -> iPad |
| iphone_face_time_migration_wifi_only | FaceTime Anfruf 1:1, Starten in unterschiedlichen WiFis, wechsel vom iPhone ins Wohnheimnetz, Verbindungsabbruch und Aufbau über Apple, dann wieder lokal | iPhone -> iPad |

Die Erkenntnisse aus den Tests

| Verhalten | Protokoll | Endpunkt | Bemerkung |
| --- | --- | --- | --- |
| Verbindungsaufbau (ausgehend) | TCP | (Apple) 17.138.211.254 = query.ess-apple.com.akadns.net | Vermutlich werden Daten wie Name,Bild und Anrufinfos ausgetauscht |
| Informationsverbindung | QUIC | (Apple) 17.242.208.196 (beide Clients zur selben Adresse) | Wahrscheinlich Transportverbindung für Daten von FaceTime. Wieder direkt von bzw. zu Apple |
| Datenverbindung | RTP via UDP | 10.151.13.199 (iPad) <-> 10.151.12.233 (iPhone) | DIREKTE Datenverbindung nachdem STUN erfolgreich war. Kein Server bzw. Apple involviert |
| Abbruch der Verbindung | --- | --- | Wechsel von Laptop in Wohnheimnetz |
| Verhalten abhängig von Interfaces | --- | Cellular -> Direkte Migration | Abbruch der WiFi Verbindung |
| Verhalten abhängig von Interface | --- | WiFi -> Apple -> Direkte Verbindung | Abbruch der WiFi Verbindung ohne Cellular |
| Anrufer/Empfänger versucht sich zu mit selber Adresse zu verbinden | ICMP | Dest. unreachable | Verbindung über alte Bindings schläft fehl |
| Versucht alte Bindings wieder herzustellen | STUN | 10.151.12.233 | Schlägt fehl |
| Gerät ohne Abbruch verbindet sich zu Apple | TLS | 17.57.146.174 | Wahrscheinlich Wiederaufnahme der Verbindung |
| Verbindung an Apple | QUIC | lokal <-> (Apple) 17.252.29.4 | Transportverbindung. Beide stellen Verbindung an den selben Server her. Initial Handshakes |
| Wiederherstellung der direkten Verbindung | QUIC + RTP | lokal -> iPad | Wenn die Verbindung lange genug weiterläuft, sucht und findet FaceTime auch wieder die lokale Verbindung und benutzt diese statt dem Apple Relay |

---
## Nachtests zum Verhalten von FaceTime mit Rücksicht auf unsere Ergebnisse
Die Tabelle enthält informationen zum Test der durchgeführt wurde

| Dateiname | Test | Richtung | Beobachtungen |
| --- | --- | --- | --- |
| facetime_ipad_desktop_migration_cellular_ap | FaceTime Anruf 1:1, Beide im selben WiFi, HHG, dann Migration auf Cellular AP auf dem Handy für das iPad, dann switch zurück ins HHG | iPad erstellt Link -> Desktop tritt per Chrome (Firefox nicht kompatibel) bei, keine Migration auf Desktopseite | Ich habe aber tatsächlich nie eine direkte Verbindung sowohl beim Cellular AP als auch nach dem switch zurück gesehen. Immer über iCloud bzw. Apple Relays |
| ft_cellular_migration_wohnheim | FaceTime Anruf vom Handy an iPad, Messung auf iPhone. AP auf dem Laptop mit Internet hinter meinem eigenen NAT. Dann AP aus, iPhone cellular enabled. Migration auf Cellular. Migration zurück auf WiFi. Dann wiederholt AP aus, migration und wieder AP an, zurück | iPhone -> iPad nativ | Öffnet alle Interface Pfade, Maintain alle 1s mit STUN binding request die WiFi Pfade, cellular aber nicht?, switch auf IPv6 Cellular innerhalb von ~100ms und direkter Pfad zwischen Cellular iPhone<->IPv6 iPad (stottert trotzdem in der Anwendung, habe nur 1 Seite gemessen),   |

## WhatsApp Verhalten
Die Tests auf die Dateinamen gemapped.

| Filename | Test | Richtung | Notizen | 
| --- | --- | --- | --- |
| 22_01_13_55 | Anruf per Whatsapp. Im WiFi | Extern -> Mich | Kommunikation in einem 10.183.0.0/16 Netz? Ist schon P2P aber warum in einem unterschiedlichen Subnet? |
| 22_01_13_56 | Anruf per Whatsapp. Im WiFi | Ich -> Extern |
| 22_01_13_57 | Anruf per Whatsapp. Im Mobilfunk | Ich -> Extern |
| 22_01_14_17 | Anruf per Whatsapp. Im Mobilfunk | Ich -> Extern |
| out_pxl_25_02_10_57 | Anruf von Pixel per Whatsapp. Handy im Laptop Netz. Beide im Cellular. Wechsel auf selbes WiFi zuhause. Dann wechsel zurück ins Laptop WiFi. | Ich -> Extern | 192.168.12.101 ist im Laptop WiFi. 192.168.178.20 ist WiFi zuhause. Zusätzlich sind beide im Cellular. Pixel bei O2, Extern bei Vodafone |
| out_pxl_25_02_11_10 | Anruf von Pixel per Whatsapp. Pixel im Laptop Netz. Beide haben KEIN Cellular. Wechsel auf selbes WiFi zuhause (nach ca. 30s). Dann wechsel zurück ins Laptop WiFi (nach ca. 30s). | Ich -> Extern | 192.168.12.101 ist im Laptop WiFi. 192.168.178.20 ist WiFi zuhause. |
| out_pxl_25_02_11_15 | Anruf von Pixel per Whatsapp. Pixel im Home WiFi. Nur Pixel zusätzlich Cellular. Idle ca. 2.20min. ohne WiFi zu deaktivieren  | Ich -> Extern | Pixel Cellular ist O2 |
| out_pxl_25_02_11_21 | Anruf von Pixel per Whatsapp. Pixel im Home WiFi. Beide zusätzlich Cellular. Idle ca. 2.20min. ohne WiFi zu deaktivieren  | Ich -> Extern | Pixel Cellular ist O2, Extern ist Vodafone |
| out_pxl_25_02_11_26 | Anruf von Pixel per Whatsapp. Pixel im Home WiFi. Nur Pixel im Cellular. Idle ca. 30s. Dann WiFi deaktivieren 40s. Dann Wechsel zurück. | Ich -> Extern | Pixel Cellular ist O2, Extern ist Vodafone |
| out_pxl_25_02_11_29 | Anruf von Pixel per Whatsapp. Pixel im Home WiFi. Beide im Cellular. Idle ca. 30s. Dann WiFi deaktivieren 40s. Dann Wechsel zurück. | Ich -> Extern | Pixel Cellular ist O2, Extern ist Vodafone |


Das Verhalten in den Tests:

| Verhalten | Protokoll | Endpunkt | Bemerkung |
| --- | --- | --- | --- |
| Verbindungsaufbau | TCP | 157.240.0.61 = whatsapp-chatd-edge... = Facebook Relay | Wahrscheinlich kurzer Verbindungsaufbau um Anruferinfos auszutauschen |
| Direkter Verbindungsaufbau | STUN über IPv4 | 157.240.0.62 = edgeray-shv... | NAT Traversal? |
| Direkter Verbindungsaufbau | STUN über IPv6 | 2a03... = edgeray6-shv... | NAT Traversal? |
| Initiale Verbindung? | UDP über Edgeray | .62 = edgeray | Session Initiation? |
| Binding in lokalem Subnetz | STUN | MWN | Migration auf lokales Netzwerk? |
| Datenaustausch | RTP via UDP | 10.151.13.144 <-> 10.183.33.228 | Datenaustausch im LRZ Netzwerk |
| Datenaustausch im Mobilfunk | RTP via UDP | IPv6 (LRZ) <-> IPv6 (Telefonica) | Datenaustausch läuft ebenfalls P2P direkt von Gerät zu Gerät. Kein Whatsapp Server ist dazwischen |


## Todos:
- IPhone extern per Cellular (evtl)
- NearbyShare 2 Interfaces
- AirDrop in unterschiedlichen Netzwerken mit mehr als 3s
- Untersuchen warum dort TCP verwendet wird
- FaceTime genauer anschauen. 
    - Setup mit Box: anruf, abbruch, migration?
    - IPad WiFi wechseln, was passiert?


## Some testing notes, Mapping ID to device

- Pixel 0095 (adb: 801KPGS1389743) is for outside the box
- Pixel 0093 (adb: 801KPRW1393526) is for inside the box

- iPhone (00008020-001E50A62684002E) is inside the box because of space reasons
- iPad (00008027-000E11421187002E) is outside the box