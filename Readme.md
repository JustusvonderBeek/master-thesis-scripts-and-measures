# Progress Masterarbeit
Diese Datei enthält Notizen, Information und sonstiges zum Fortschritt der jeweiligen Woche.

## Apple Geräte Infos
Ein paar Infos die das Leben vielleicht einfacher machen

### iPhone
- Version 17.1.1
- Wlan-MAC E0:33:8E:78:41:80
- Bluetooth-MAC E0:33:8E:73:9C:50

#### Änderungen
Die folgenden Operationen habe ich bisher auf dem Gerät durchgeführt:
- Installation eines Zertifikates von mitmproxy um Traffic zu sniffen (hat nicht funktioniert)
- iCloud mit meinem Konto verbunden
- HHG und Eduroam Internet eingestellt

### iPad
- Version 17.1.1
- WLAN-MAC EC:2C:E2:DD:CA:72
- Bluetooth-MAC EC:2C:E2:DD:A3:51
- Andere Apple ID erstellt für den Test des Protokolls (tum.mtappleid@gmail.com)

#### Änderungen
Die folgenden Operationen habe ich bisher auf dem Gerät durchgeführt:
- iCloud mit meinem Konto verbunden
- HHG Internet eingestellt

### Mac
- Gesetztes Passwort damit ich im Terminal Sachen installieren kann. Passwort ist: "Masterarbeit"

## 13.12.2023
- NearbyShare näher zusammengefasst
    - Feature exists since in this form since 2020: https://blog.google/products/android/nearby-share/
    - Seems to be a Google Play Service: https://developers.google.com/android/guides/releases#june_2017_-_version_110
    - Windows Support seit 2023: https://blog.google/products/android/nearby-share-windows-android/
    - Offizielle Dokumentation: https://developer.android.com/develop/connectivity/wifi/wifi-direct

### WiFi Shield Boxes
- USB-A Durchlass (funktioniert für WLAN Antenne & ADB & RVICTL)
- Ethernet Durchlass (funktioniert für Internet per USB-C auf den Geräten)


### Pixel Root
Eine kleine Dokumentation darüber, wie man das Pixel rooten kann. Das funktioniert leider nicht universell für alle Geräte, sondern hängt vom Hersteller und dem genauen Gerät ab. Ein gutes Video dazu: https://www.youtube.com/watch?v=qxdxP09zSeQ&ab_channel=PhonlabTech

1. Den Bootloader unlocken. Ist nicht schwer. OEM unlocken. Dazu Developeroptions > OEM Unlock. Sollte das ausgegraut sein dann Factory Reset (und mit WiFi) neu einrichten. Rebooten in bootloader und per PC fastboot tool unlocken. 2 Commands `adb reboot bootloader; fastboot devices; fastboot flashing unlock; fastboot reboot`. Hier: https://android.gadgethacks.com/how-to/unlock-bootloader-your-google-pixel-pixel-xl-0174627/
2. Das orginale Factory Image beziehen. Für die Pixel ist das: https://developers.google.com/android/images#sailfish . Evtl. Acknowledgement bestätigen. Herunterladen und sowohl den äußeren als auch den inneren Ordner extrahieren. Die Datei boot.img aus dem inneren der beiden Ordner auf das Gerät schieben.
3. Magisk auf dem Handy installieren: https://github.com/topjohnwu/Magisk
4. Stable Version downloaded. Dann das boot.img aus dem Download Ordner auswählen. Das Boot Image wird damit gepatched, damit wir es später installieren können. Es sollte im selben Ordner wie das orginal Image liegen.
5. Diese Image dann vom Handy auf den PC ziehen. Sei es mit "adb pull" oder per GUI
6. Das Handy in den unlocked bootloader rebooted. `adb reboot bootloader`
7. Check ob fastboot läuft: `fastboot devices`
8. Das gepatchede Image laden: `fastboot flash boot --slot all image.img`. Das sorgt dafür das beide Slots (für OTA updates, damit das Handy immer läuft und ein Image theoretisch kaputt gehen kann) überschrieben werden.
9. Rebooten: `fastboot reboot`
10. Falls man den orginalen Zustand wieder herstellen möchte geht das indem in der selben Reihenfolge das orginale Google Image aufgespielt wird.

### TCPDUMP auf Android
Um tcpdump [auf Android installieren](https://andreafortuna.org/2018/05/28/how-to-install-and-run-tcpdump-on-android-devices/) zu können braucht es ein gerootedes Handy. Siehe oben. Anschließend die aktuelle Version von tcpdump auf der Seite mit extra für ARM kompilierten Versionen runterladen: https://www.androidtcpdump.com/android-tcpdump/downloads

Um tcpdump per adb auf das Gerät schieben zu können braucht es adbd im root Modus. Dazu der Anleitung auf der offiziellen Github Seite folgen: https://github.com/evdenis/adb_root. TLDR: Latest Release auf das Handy runterladen, in Magisk unter Modules öffnen und installieren, reboot.

Anschließend das Program in einen Ordner schieben wo man später mit der Shell drankommt. Offiziell sollte das `/system/xbin` sein (Programme auf die das OS verzichten kann). Weil das Pixel aber diesen Ordner nur als read-only FS mounted und es ziemlich umständlich ist das zu ändern (zumindest mit dem Gerät was ich habe) reicht auch `/sbin` als Ordner. Der ist bereits im PATH und der Befehl tcpdump wird danach direkt gefunden und ausgeführt.

Lässt man tcpdump die Interfaces auflisten finden sich viele verschiedene. Wir werden wahrscheinlich *any* benutzen, das auf allen Interfaces mitschneidet. Das funktioniert dann wie folgt:

    $ adb shell tcpdump -D # Listet Interfaces auf
    $ adb shell tcpdump -vv -i any -w /sdcard/file.pcap
    $ adb pull /sdcard/file.pcap output.pcap  

Damit das funktioniert muss ADB im root Modus aktiviert sein. Also entweder das Modul aktivieren oder statt:

    $ adb shell <command>
    $ adb shell su -c <command>

### Extract SSL Secrets on Android (nicht notwendig?)
TODO: 

Aus IRGENDEINEM Grund ist die Verbindung über WiFi Direct **NICHT** verschlüsselt! Ich kann die Daten zumindest von der PDF einfach so aus dem mitgeschnittenen Stream lesen! Entfernt man zumindest ein bisschen von den überschüssigen Daten kommt zumindest eine Datei mit der richtigen Seitenzahl raus. Man müsste wahrscheinlich also noch weitere Kontrollstrukturen entfernen, aber dann sollte die Datei stimmen.

Überträgt man die Daten hingegen über einen AP ist der anfängliche Austausch ebenfalls **NICHT** verschlüsselt, d.h. man sieht die Klarnamen von dem Gerät was senden möchte. Die Daten sind allerdings verschlüsselt über eine normale TCP Verbindung übertragen. D.h. hier kommt man nicht mehr einfach so an die Daten heran.


## 06.12.2023
- Siebter Test (iPad zu iPhone, aktivierter MAC und IP Adressen Schutz)
    - Idee ist es hier ein mögliches Unterschiedliches Verhalten gerade aus Sicht der IP Migration anzuschauen
- iPhone Jailbrake suchen um zu schauen ob man damit an die Zertifikate kommt -> Spoiler: Es gibt bisher keinen funktionierenden Jailbreak für iOS 17.1+. Tatsächlich gibt es ab dem Xs keine funktionierenden Jailbreaks mehr. Es ist daher unwahrscheinlich, dass in der Kürze der Zeit ein neuer Jailbreak kommt. Die Zeit und der Aufwand sind das Ergebnis allerdings nicht wert. Das einzige was man versuchen *könnte* wäre ein Proxy, wobei auch das mittlerweile erfolglos scheint.

- Siebter Test (iPad zu iPhone, Privacy Mode aus, kein Internet)
    - Beide Geräte mit dem selben AP verbunden
    - **Kein** Zugang zum Internet
    - Übertragung mittels AWDL gestartet
    - Verbindung migriert ohne Probleme auf WiFi obwohl kein Zugang zum Internet besteht
    - Allerdings: Es wird erst eine QUIC Verbindung über das AWDL Interface aufgebaut. Im Laufe der Verbindung wird eine neue DCID geschaffen, diese wird dann bereits auf das WiFi Interface migriert. Es existiert also die selbe selbe DCID kurzzeitig auf beiden Interfaces (Einzelfall)
    - Das passiert bereits bevor die AWDL Verbindung abbricht
    - Die neue Verbindung migriert aber, keine Initial Pakete oder Extended Headers, alles Short Header
    - Dabei sendet das iPad (Sender) zuerst auf dem WiFi Channel, nicht das iPhone (Empfänger)
    - Die Destination Connection ID bleibt identisch zu einer der beiden auf dem AWDL Interface
    - QUIC verwendet hier einen Short Header, also keine neue Verbindung, und die selben Schlüssel (Parameter) etc.
    - Auf dem AWDL Interface werden noch genau 3 Pakete gesendet (2 empfangen, 1 gesendet). Danach ist die alte Verbindung tot. Dabei wird die selbe DCID wie auf dem neuen Interface genutzt. Das ist aber eher ein Artefakt davon, dass das AWDL Interface noch in Reichweite war. Es müssen nicht beide Verbindungen parallel existieren. Und es wird auch immer nur 1 Interface primär genutzt
    - Die Verbindung läuft ohne Probleme zu Ende

- Achter Test (iPad zu iPhone, Privacy Mode aus, Weg- und wieder hingehen, kein Internet)
    - Migriert die Verbindung auch wieder auf das AWDL Interface, nachdem sie schon auf das lokale WiFi Interface ohne Internet migriert ist?
    - Dazu erst wegbewegen, warten und dann wieder hinbewegen
    - Selbes Verhalten wie davor. Beim wegbewegen migriert die Verbindung gut, sobald die Verbindung über das WiFi Interface aber steht, wird nichts mehr geändert
    - Neue QUIC Verbindung wird bereits davor aufgebaut, wieder mit Short Header und bereits genutzter ID
    - Keine Migration zurück auf das AWDL Interface, obwohl die Geräte direkt nebeneinander liegen
- Neunter Test (iPad zu iPhone, Privacy Mode auf dem iPad an)
    - Kein Unterschied zum achten Test
    - Kein anderes Verhalten während des mDNS Advertisements bzw. Announcements
    - Verbindung geht an die selbe Adresse die auch für mDNS verwendet wird
    - Migration funktioniert ebenfalls wie davor (problemlos)
    - Allerdings, diesmal keine gleichzeitige Verbindung von AWDL und WiFi
    - Scheinbar funktioniert die Migration also auch ohne gleichzeitige Verbindung

- Neunter Test (iPad zu iPhone, lokales Netzwerk mit Internet, kein Privacy Mode)
    - Nochmal, was genau passiert im Standardfall?
    - Ohne Wechsel des AP
    - Im Unterschied zu davor wird jetzt zwischen dem Wechsel auf QUIC ICMPv6 gesprochen (Solicitation (iPad, Sender), Advertisement (iPhone, Receiver)). (Mal passiert das genau zwischen dem Verbindungsabbruch, mal aber auch nicht; es scheint periodisch die Nachfrage zu geben, bzw. dann wenn es gebraucht wird weil die Information vielleicht noch nicht vorhanden ist). Es wird **IMMER** gefragt wo die *_asquic._udp.local* Adresse ist, sollte die Information aber noch im Cache sein verbindet sich der Sender sofort per QUIC zum Empfänger an die bekannte Adresse. Funktioniert sowohl mit als auch ohne Internet
    - Zudem entsteht jetzt eine 4s Pause zwischen dem Wechsel. Das liegt daran, dass keine gleichzeitige Verbindung auf dem zweiten Interface aufgebaut wird
    - Zweimal wird die Verbindung zudem erst nach dem Abbruch aufgebaut. Es existieren also nie gleichzeitig 2 Verbindung in diesem Fall (wir wissen dass nie beide Verbindungen gleichzeitig existieren müssen; die Tatsache, dass nur 1 von beiden Verbindungen zur selben Zeit aktiviert ist, konnte ich aber nicht verlässlich reproduzieren; zweimal wird die WiFi Verbindung erst bei Problemen aufgebaut, zweimal aber bereits direkt am Anfang der Übertragung wenn die Verbindung noch gut funktioniert.) Sollten die Geräte aber keinen Zugang zum Internet haben dann bauen sie mit 1-2s Verzögerung eine zweite Verbindung über das WiFi Interface auf
    - Das Verhalten mit dem Übernehmen der alten DCID ist allerdings weiterhin das selbe. Erst in der AWDL Verbindung erstellt, dann in der WiFi Verbindung übernommen
    - Diesen Test habe ich 3 weiter Male wiederholt um über die Charakteristik sicherzugehen

- Zehnter Test (iPad zu iPhone, Lokales Netz, Internet, AP Wechsel)
    - Kann ich die Ergebnisse vom zweiten Test wiederholen? Oder war das ein Wohnheims-internes Problem
    - Diesen Test habe ich 3 mal ausgeführt
    - Es scheint, dass die Messung im Wohnheim wohl ein Einzelfall gewesen ist. Die Verbindung bricht nach dem Wechsel des AP nicht ab und AirDrop scheint im lokalen Netzwerk weiterhin normal zu funktionieren. Dafür sorgen wahrscheinlich auch die IPv6 Adressen, die ein Netzwerkübergreifenden Endpunkt bieten
    - Es scheint so, dass ein Setup mit zwei unterschiedlichen Netzen, die nicht miteinander kommunizieren können notwendig wäre um zu bestätigen, dass Apple auch mit WiFi über das Internet geht (bzw. siehe Cellular Tests)
    - Das wiederum heißt, dass die Verbindung relativ stabil ist, solange man im selben WiFi Netzwerk bleibt


### Erster Test mit NearbyShare
- Verbindung zwischen Handy und Windows Laptop
- Eine Verbindung zwischen dem unangemeldeten Laptop und Handy ist gar nicht zustande gekommen
- Manchmal ist die Verbindung super langsam, teilweise wenige KiB
- Teilweise ist die Verbindung schneller, dann über das WiFi Interface und mittels TCP
- QUIC habe ich bisher nicht ausmachen können
- Es gibt zumindest auf dem Handy die Option, auch mobile Daten zu verwenden um kleinere Dateien zu übertragen
- Ob das aber dazu führt, dass QUIC verwendet wird und die Verbindung migriert ist unwahrscheinlich. Getestet habe ich das aber auch nicht. Wahrscheinlich wäre aber auch hier eine Verbindung über irgendein Relay von Google im Internet, was den Transfer erlaubt.


### Versuche mit SSLKillSwitch
- Das Program kann vom [GitHub Repo](https://github.com/nabla-c0d3/ssl-kill-switch2) heruntergeladen werden
- Beim ersten mal bauen schlägt das Build mit dem Fehler: "libarclite-macosx not found" fehl. Das passiert, weil bei default die Build Version auf 10.x eingestellt ist
- Klickt man in XCode oben auf das Project kann man unter **General** > **Deployment Info** die Version einstellen. Für das eigentliche Program und die Tests auf 14 gesetzt funktioniert der Build
- Allerdings kann man nicht einfach so an Systemapps attachen. Ich habe das bisher nicht zum laufen bekommen. Außerdem muss man dann anschließend noch die Bibliothek laden und ein MitM Proxy einrichten um den Transfer zu erlauben. 
- Das ist sehr aufwändig und funktioniert auch immer noch nicht für AirDrop selber. Denn hier funktioniert ein Proxy natürlich nicht


## 22.11.2023
### TL;DR
- Ältere Geräte verwenden TLS/TCP und seit 17.1 wird sowohl QUIC als auch TCP/TLS für den eigentlichen Datenaustausch verwendet
    - 17.1: Abhängig vom Modus wird TCP/TLS oder QUIC für den Austausch über das lokale Netzwerk verwendet
    - Wenn man an eine Person teilt (einen Kontakt) dann wird QUIC verwendet. Macht Sinn, da dann auch das iCloud Konte bekannt ist. Wenn man hingegen an ein Gerät teilt wird TCP/TLS verwendet. Ich vermute, dass das daher kommt weil in dem Fall das Gerät eventuell nicht mit iCloud verbunden sein kann und Apple daher auf Nummer sicher gehen will
    - Mit TCP/TLS findet keine Connection Migration oder ähnliches statt, die Verbindung bricht bei Problemen ab
    - Es können keine Verbindungen nur über WiFi und nicht AWDL zustande kommen. Das Geräte/die Person wird gefunden, aber es kommt keine Benachrichtgung fürs das Annehmen oder Ablehnen. Dafür müssen beide Geräte in Bluetooth oder AWDL Kontakt und Reichweite sein
    - Im Fall dass beide im selben AP sind geht die Übertragung ohne Probleme vom AWDL zum WiFi Interface und läuft weiter. Es kommt evtl. zu einer kurzen Unterbrechung (wenige Sekunden; 1 mal seamless, 1 mal nicht seamless: ~2s Pause)
    - Wechselt man zusätzlich auch noch den AP bricht die Verbindung vorerst ganz ab (länger als ~1-2s)
    - TODO: Confirm
    - Bei wechseln des AP wird über iCloud *Relays* (keine Ahnung wie die offiziell heißen) versucht wieder eine Verbindung herzustellen
    - Dieser Prozess ist **nicht** seamless und dauert bis zu 60 Sekunden

### Long Version
- Start der Analyse mit den neuen Apple Geräten
- Registrierung von iPad und iPhone mit meiner Apple ID (WICHTIG: Diese am Ende wieder entfernen, genauso wie alle Dateien auf den Geräten die mir gehören)
- Folge den Tipps [dieser Webseite](https://developer.apple.com/documentation/network/recording_a_packet_trace) um das iPhone fertig für den Mitschnitt zu machen und einen Trace anzufertigen
- Trace zeigt mehrere Interfaces auf die für AirDrop genutzt werden: utun4 (System Interfaces; 0-1 ist VPN, darüber ...) / awdl0 (WiFi Direct, Apple Wireless Direct Link) / anpi0 (Bluetooth?)
- Installation von [Opendrop](https://github.com/seemoo-lab/opendrop) sowie [AWDL Re-Implementation](https://github.com/seemoo-lab/owl) um zu testen ob das mit dem aktuellen iPhone kompatibel ist. Nein, ist es nicht (mehr)
- Einloggen in alle Geräte um mit dem MAC airdrop zu testen

- Erste Tests (iPhone zu MAC):
    - Das Macbook empfängt bzw. überträgt die Daten nur per TCP/TLS auf dem AWDL Interface (llw0 nicht genutzt)
    - Das iPhone sendet an die multicast IPv6 Adresse ff02::fb einen MDNS **Response** mit der Ankündigung, dass es eine Authority für die Domain ist an der IPv6 von der der Request gesendet wurde. Diese Ankündigung ist 2 Minuten valid. Der Port ist 8770, Protokoll *hier* TCP.
    - Das Cache-Flush flag von MDNS ist gesetzt womit alte Records überschrieben werden sollen
    - Damit wird die Information bezüglich des AWDL Servers bzw. AP von demjenigen übermittelt, der teilen möchte (die Verbindung anfängt)
    - Dann verbindet sich der MAC (Empfänger) mit dem neu mitgeteilten AP
    - Es kommt eine TCP/TLS1.2 Verbindung zustande, in der laut Paper Authentifikationsdaten ausgetauscht werden (TODO: Was wird ausgetauscht) (27 Pakete)
    - ICMPv6 (bzw. MLDv2) wird benutzt um die ff02::fb Adresse zu excluden (nicht mehr zu listen?)
    - Die Multicast Question (QM) vom MAC (Empfänger) im lokalen Netzwerk (AWDL) wird gesendet um nach *_airdrop._tcp.local* zu fragen. Das iPhone (Sender) antwortet mit dem Port 8770 und der selben IPv6 wie vorher (Warum? Keine Ahnung)
    - Danach beginnt ein neuer Handshake mit dem Sender und per TCP / TLS1.2 werden die Daten übertragen
    - Das wars
    - Periodisch wird das Spiel mit mDNS Request / Response von oben wiederholt und der Cache geflusht.
- Versuche mit einem *mitmproxy* sowohl iCloud als auch AirDrop zu sniffen waren nicht erfolgreich. iOS traut dem eingeschleusten Zertifikat nicht und lädt zumindest von iCloud nichts herunter. Das wird sicherlich auch eine Rolle spielen wenn wir AirDrop über das iCloud Relay untersuchen. Es scheint, Apple betreibt hier Zertifikat Pinning und lässt ungültige Zertifikate nicht zu.
- Als nächstes versuche ich **Frida** zum laufen zu kriegen um damit die SSL Keys loggen zu können um dann den Traffic decrypten zu können
- Frida braucht leider ein DeveloperDiskImage um den Spaß debuggen zu können. Da Apple mit iOS 17 dieses Image geändert hat funktionieren die bisherigen Tools und Protokolle auf einmal aber nicht mehr. Um weiterarbeiten zu können braucht es also erstmal einen Workaround hier.
- Mittels dem Mounter von pymobiledevice3 kann man eine Debugging Verbindung mit dem iPhone herstellen. Problem dabei ist, dass frida bisher noch nicht an das neue Image angepasst wurde und daher nicht mit dem neuen DebuggingImage arbeiten kann. Ein entschlüsseln damit wird also eher nicht möglich
- Um zumindest auf dem MAC den Trace decrypten zu können versuche ich die OpenCore Bootargumente auszunutzen. Das sollte gehen, da das **csrutil** Tool im Recovery Mode nicht unterstützt wird.
- Das entfernen von Beschränkungen des NVRAM ist erforderlich und kann einfach in den OpenCore Settings deaktiviert werden indem ein Flag in den Security Settings geändert wird. Danach muss OpenCore erneut in den Settings installiert und rebooted werden. Das führt dazu, dass der Kernel mit den entsprechenden Flags geladen wird.
- Sobald der NVRAM freigeschaltet ist kann man im normalen Terminal mit dem Command *nvram boot-args "amfi_get_out_of_my_way=1"* und Root Rechten das AMFI Feature deaktivieren und die Keys auslesen.
- Nachdem die Keys ausgelesen wurden konnte ich leider immer noch nicht den Traffic entcrypten. Zudem funktioniert die OpenDrop Implementierung mit den gelesenen Keys auch nicht korrekt.

TODO: Setup für das iphone finden um damit TLS und QUIC traffic (von AirDrop) entschlüsseln zu können.

- Versuche mit einem *mitmproxy* sowohl iCloud als auch AirDrop zu sniffen waren nicht erfolgreich. iOS traut dem eingeschleusten Zertifikat nicht und lädt zumindest von iCloud nichts herunter. Das wird sicherlich auch eine Rolle spielen wenn wir AirDrop über das iCloud Relay untersuchen. Es scheint, Apple betreibt hier Zertifikat Pinning und lässt ungültige Zertifikate nicht zu. Confirmed, App Store pinnt Zertifikate, daher bräuchte man hier sicherlich ein jailbrake Phone
- Als nächstes versuche ich Frida zum laufen zu kriegen um damit die SSL Keys loggen zu können um dann den Traffic decrypten zu können. Laut Paper [TLS Session Key Extraction](https://rp.os3.nl/2015-2016/p52/report.pdf) geht das aber ebenfalls nur mit einem iPhone was einmal ge-jailbraked wurde damit man die App extrahieren, laden und signen kann

- Zweiter Test (iPhone zu iPad): *Wechsel des AP*:
    - Das iPhone sendet wieder, das iPad empfängt
    - Der grundsätzliche Aufbau ist der selbe wie im ersten Test (mDNS um IP zu suchen, kurzer Austausch **über TCP/TLS1.2** wahrscheinlich identisch zu dem vom ersten Test)
    - Nach dem ersten Austausch switchen die Geräte aber auf QUIC um und übertragen die Daten mittels QUIC, nicht mit TCP/TLS
    - Die Übertragung dauert (subjektiv) länger
    - Auch ein kurzzeitiger Verbindungsabbruch führt nicht dazu, dass die Daten online über die iCloud übertragen werden. Stattdessen kann die Verbindung in QUIC recovered werden
    - Ich habe es geschafft einmal die Verbindung abzubrechen, wonach die Datei mit einer iCloud Wolke Icon angezeigt wurde. Da aber alle meine Geräte die selbe Apple ID besitzen kann ich nicht sagen ob das auch sonst der nächste Schritt wäre oder ob das daher kommt, dass die Datei eh in meiner iCloud liegt
    - *Daher erstellen einer zweiten Apple ID und auf dem iPad anmelden mit der neuen Apple ID*
    - Sobald man den Versuch etwas weiter weg startet (**falsch**: sobald man statt der Apple ID Person das spezielle Gerät als Ziel auswählt), benutzen auch iPad und iPhone mit 17.1 TCP/TLS und übertragen die Daten über das AWDL Interface mit diesem Protokoll. Daher stürzt die Übertragung auch beim wegbewegen einfach ab und wird nicht weiter fortgesetzt. Sobald man sich näher zum Gerät bewegt kann es passieren (ich habe nicht genau herausgefunden wann), dass die restlichen Daten dann über eine neue Verbindung doch noch ausgetauscht werden.
    - Mit 16 Sekunden Pause kann die Verbindung wieder aufgenommen werden (start und ende close, dazwischen keine Verbindung)
    - Hypothese: Solange beide Geräte die Übertragung in der UI nicht abbrechen wird die Verbindung beim näher kommen wieder aufgenommen. Hier allerdings wieder TCP/TLS und eine gänzlich neue Verbindung, keine Connection Migration oder das Fortsetzen einer bestehenden Verbindung
    - Mit dem durchgehen der Türe wird die Verbindung für *kurze Zeit unterbrochen* und dann sofort *über das WLAN Interface* **en0** fortgesetzt. Da sich beide Geräte zur gleichen Zeit im gleichen WLAN+selben AP befinden funktioniert das. Die IPv6 **ändern sich** genauso wie die **Destination Connection ID von QUIC** (nicht immer. 1 mal gewechselt, beim selben AP bleibt die DCID gleich!). Beim Aufbau der Verbindung werden 2 Destination Connection IDs ausgemacht, eine scheint aber primär zu sein und die andere wird nur vereinzelt benutzt (genauso ohne encrypt nicht sicher). Nach dem switch wird eine komplett gedroped (TODO: confirm)
    - Der Transfer geht weiter und würde wahrscheinlich auch ohne Probleme zueende laufen
    - Ich bewege mich aber weiter weg und das iPhone (Sender) **wird den AP wechseln**. Ab dem Moment bricht die Verbindung ab. Ab hier: TODO: confirm Das iPad sucht per Neighbor Solicitation nach der Link-Lokal Addresse vom iPhone.
    - Das iPhone wechselt den AP und führt 802.x aus
    - Danach kommt keine Verbindung zwischen dem iPad und dem iPhone mehr zustande
    - Es dauert gut 25 Sekunden bis das erste Mal eine Verbindung per IPv4 an die **17.188.171.155** hergestellt wird. Das ist eine iCloud bzw. Apple Adresse
    - Der Austausch ist allerdings relativ kurz und reicht nicht um die verbleibenden Daten senden zu können. Was genau ausgetauscht wird ist erst nach dem Decrypt klar. Ich vermute zwar es hat etwas mit AirDrop zu tun, es könnte aber auch irgendein anderer Service sein
    - Es kommt einiges an Datenaustausch dazu, mehrmals wird die Verbindung zu Apple aufgebaut und kurz mehrere Daten ausgetauscht. Das ist aber alles hochwahrscheinlich nicht relevant für AirDrop sondern andere Daten bzgl. z.B. Fotos oder anderen Daten. Sicher kann ich bisher aber nicht sein
    - Am Ende kann im lokalen Netzwerk der Austausch wieder aufgenommen werden mittels der davor bereits verwendeten Addressen.
    - iCloud wird (in diesem Fall) **nicht** zum Übertragen als Relay genutzt

- Dritter Test (iPad zu iPhone, iPhone bewegt sich weg) *AWDL bricht ab, kein AP wechsel*:
    - Idee ist, nur weit genug wegzugehen, dass die Verbindung im lokalen Netz bestehen bleibt, aber AWDL nicht mehr funktioniert
    - *Eigene Notiz*: Gerade so durch die Tür durch scheint die WiFi Direct Verbindung abzubrechen aber im selben AP zu bleiben
    - Wechsel der Verbindung funktioniert und findet statt, allerdings mit mehreren Sekunden Pause (~2s bis ICMPv6 Neighbor Solicitation stattfindet, 4s bis QUIC Migration stattfindet) und ohne Transfer dazwischen. Auch hier wieder **nicht wirklich** seamless, bzw. spürbarer Abbruch
    - Allerdings, die Datei wird im lokalen Netzwerk

- Vierter Test (iPad zu iPhone, iPhone bewegt sich weg, iPhone nur Cellular & AWDL)
    - Dieser Test beinhaltet Cellular
    - Idee ist den Austausch über das Internet zu erzwingen, da diesmal keine lokale Verbindung zustande kommen kann
    - Ähnliches Verhalten wie beim dritten Test
    - Verbindung über AWDL bricht ab / wird zu schwach
    - iPhone empfängt und sendet Daten über ein anderes Interface (unbekannt in welchem Zusammenhang, **aber** während des bisherigen Transfers nicht benutzt! -> scheint wohl für AirDrop relevant). Es wirkt so als versuche das iPhone über alle lokalen Interfaces eine Verbindung zum iPad aufzubauen
    - Schlägt fehl, da nicht im selben Netzwerk und WiFi (außer AWDL) nicht verbunden
    - Circa 5s in denen *irgendein* recovery Versuch im lokalen Netz versucht wird. Schlägt fehl
    - Danach 2 neue QUIC Verbindungen (Initial) nach Kalifornien zu Apple. Eine IPv6 (2620:149:f9:1026::7), eine IPv4 (17.188.179.5). Beide 0-RTT. Beide neue DCIDs
    - Beide laufen über das Cellular Interface
    - AirDrop (entscheidet) sich für IPv4. Wahrscheinlich weil ich eigentlich keine IPv6 vom Netzbetreiber bekomme? TODO: confirm
    - IPv6 bleibt offen, wird aber nicht genutzt (Backup?). Zur selben Addresse werden zusätzlich noch eine HTTPS und HTTP Verbindung (Port 443, 80) aufgebaut? Beide kommen nie Zustande (Retransmission der SYNs)
    - Es wird noch genau 1 Paket auf der AWDL Verbindung gesendet. Vom iPhone (Empfänger) zum iPad (Sender). Danach ist die alte QUIC Verbindung tot
    - Auf der neuen werden Daten übertragen bis die Datei beim Empfänger vollständig angekommen ist
    - Dann scheint Apple die Verbindung zu beenden (das heißt Apple kennt den Inhalt / Aufbau?) und ICMP Port Unreachable Pakete werden versendet. Die Cellular QUIC Verbindung ist damit auch tot

- Fünfter Test (iPad zu iPhone, iPhone bewegt sich weg und wieder hin, iPhone nur Cellular & AWDL)
    - Idee: kann die Verbindung auch wieder auf AWDL migrieren?
    - Nein, zumindest von Cellular nicht mehr wieder auf AWDL
    - Die Verbindung über AWDL bricht ab
    - Die Verbindung über Cellular wird fortgesetzt (2 neue Verbindungen, 17.188.178.251, 2620:149:f9:1025::1d)
    - Selbst als das iPhone wieder direkt neben das iPad gelegt wird, migriert die Verbindung nicht mehr wieder zurück auf das AWDL Interface
    - In der GUI wird angezeigt, dass mobile Daten verwendet werden
    - Am Ende der Verbindung sieht man wieder die bekannten ICMP Port Unreachable Pakete

- Sechster Test (iPad iOS 16.x zu iPhone):
    - Es lässt sich in der Auswahl nur das Gerät, nicht die Person auswählen
    - Damit kommt auch keine QUIC sondern nur eine TCP/TLS Verbindung zustande
    - Der Rest funktioniert wie davor auch schon

- Entweder es liegt an Apple und ich bin mit dem Interface nicht vertraut, oder das Feature funktioniert leider nicht so wie angepriesen. Das heißt die Verbindung bricht ab, es dauert super lange bis der Upload wieder aufgenommen wird oder es funktioniert teilweise garnicht obwohl im Interface steht, dass der Upload/Download fertig ist. Das ist aber vor allem der Fall wenn man zwischen seinen eigenen Geräten teilt und die selbe Apple ID auf beiden Geräten verwendet.

Ein paar Notizen zu den Transportparameter:
- Der Parameter mit dem Wert 0xFF080808 bzw. 0xC0000000FF080808 existiert nicht. Sowohl in der offiziellen Dokumentation als auch sonst findet man im Internet dazu nichts
- Im offiziellen RFC findet sich ein Hinweis auf reservierte Transportparameter. Für Integerwerte von N gilt, dass Parameter=31 * N + 27 reserviert werden sollen. Allerdings ergibt sich für beide Werte (mit C0 bzw. FF) keine Kombination bei der der Parameter ignoriert wird, denn die Zahlen sind nicht kompatibel bzw. durch 31 teilbar. Hier bin ich mir nicht sicher, ob die Paramter dieser Form ignoriert werden sollen oder alle die nicht dieser Form folgen.
- Die neuen Verbindungen benutzen alle einen QUIC Short Header. Unabhängig davon ob die Verbindung gleichzeitig besteht oder erst nach dem Verbindungsabbruch aufgebaut wird.
- 

## 09.01.2024
Probleme:
- Die WiFi Boxen sind abgeschlossen, eine Box fehlt und Leander im Urlaub
- Tests mit den Boxen also vorerst ausgesetzt
- Daher, weitermachen mit Setup für die NAT Traversal + Connection Migration Tests

Ideen dazu:
- Setup mit 2 Subnets in Mininet bauen
- QUIC Quiche zum laufen bekommen und die Verbindung migrieren (hin und zurück)

Bisheriges:
- Setup in Mininet gebaut, 2 Pfade über 2 Router. Jeder Pfad brauch davor einen Switch um zu funktionieren
- Möglichkeit gefunden um mehrere Clients in Mininet zu steuern und zu kontrollieren
- Ideen für Automatisierung der Commands
- Normalen QUIC Transfer mit den vorhanden Beispielen aus QUIC-Quiche ausgeführt
- Ausprobieren von quicperf um die Funktionalität zu testen
- Ausprobieren von quicperf multipath um die Funktionaliät zu testen
    - Festgestellt, dass quicheperf-multipath scheinbar nur am Anfang beide Pfade probed und danach mehr oder weniger nur noch einen benutzt. Hier müsste man eventuell mal mit einem anderen Scheduler ausprobieren
    - Zudem funktioniert die Verbindung aktuell auch mit beiden Pfaden (zum testen). Daher ist das NAT bisher noch nicht wirklich relevant

## 24.01.2024
Bisheriges:
- Aufsetzen von automatischem Mininet
- Aufsetzen von WebRTC und ausprobieren der Beispiele
- Ausprobieren des WebRTC P2P Beispiels
    - Setup: Beide Hosts brauchen Zugang zum Internet
    - Starte CLI mit --nat oder Netzwerk mit addNAT()
    - Setze den DNS Resolver auf 8.8.8.8 oder ähnliches, damit beide Hosts DNS auflösen können
    - In die Answer-Address bzw. Offer-Address gehören die jeweiligen Partner IPs rein
- Der Test funktioniert mit in folgender Topologie: mn --topo single,2 --nat --mac; h1 answer --offer-address 10.0.0.2:50000; h2 offer --answer-address 10.0.0.1:60000
- WebRTC funktioniert mit Zugang zum Internet bzw. Google STUN Server

Testsetup: Was wollen wir mit dem WebRTC Setup erreichen?
- Vergleichsbasis für unsere Weiterentwicklung
- Was würde WebRTC machen?
    - NAT traversal Verhalten?
    - Verbindungsabbruch auf einem Pfad, finden wir den zweiten?
    - Wie schwierig ist das Setup?
    - Idee: Benutzen das Pion-To-Pion Beispiel; Wir brauchen eine direkte Verbindung aus Mininet raus ins Internet; die wird für den STUN Server genutzt und sorgt hoffentlich dafür, dass unsere beiden Peers miteinander reden können; Mininet muss außerdem Verbindungsabbrüche simulieren können
- Wir wissen was AirDrop machen würde
    - Können wir die Verbindungsabbrüche verbessern

Todo:
- Datei unter webrtc > util > vnet > nat anschauen. Dort drin sind viele Dinge enthalten, die wir so in unsere Idee wahrscheinlich mit übernehmen können. Wie genau die Einzelteile funktionieren gilt es noch herauszufinden