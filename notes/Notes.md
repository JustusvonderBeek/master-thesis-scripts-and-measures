# Notizen zur Masterarbeit
Sammelt Todos, Infos, URLs und Ideen

Ein Überblick: https://hedgedoc.rbg.tum.de/s/HtZp88QrD#

## Drafts zur Verwendung / Inspiration
QUIC:
- https://datatracker.ietf.org/doc/draft-seemann-quic-nat-traversal/
- https://datatracker.ietf.org/doc/draft-seemann-quic-address-discovery/
- https://datatracker.ietf.org/doc/html/rfc9000#name-probing-a-new-path
- https://www.rfc-editor.org/rfc/rfc8445.html
- https://datatracker.ietf.org/doc/draft-ietf-quic-multipath/
- https://datatracker.ietf.org/doc/html/rfc7604

NearbyShare:
- https://francozappa.github.io/publication/rearby/paper.pdf

## QUIC Implementierungen und Features
- QUIC-GO: Hat nur qlog und #
- PICOQUIC: Multipath, (zweites Multipath), ...
- QUICHE: ...


## TODOs:
- [ ] Quiche QUIC anschauen -> Setup in Mininet für Migration bauen
- [x] STUN anschauen und ausprobieren
- [x] ICE anschauen und durchlesen
- [ ] Mit QUIC vertraut machen
- [x] QUIC Proposals durchlesen
- [x] AirDrop Mitschnitt Setup überlegen (wie kann man auf Apple die Keys exportieren?)
- [x] Kann Apple Wireshark & sonstiges?
- [x] PCAP anschauen und analysieren
- [x] QUIC Implementierung ausprobieren / erweitern / eigenes

## Fragen (aktuelle)
- Was genau ist das Scope des ganzen Protokolls? Was soll das am Ende können?

## Termin
- Di. 09.01.2024 - WiFi Boxen ausprobieren (Problem), Pixel 1 Box zurückgeben, weiterer Plan besprechen
- Di. 20.12.2023 - Geräte abholen, WiFi Boxen ausprobieren
- Mi. 13.12.2023 - Letzten Traces besprechen und weitere Plan (NearbyShare analysieren)
- Mi. 06.12.2023 - Erste AirDrop Ergebnisse, Jailbrake machen?, Wie weiter?
- Mi. 22.11.2023 - Erstes Treffen (Geräte, Weitere Experimente planen)
- Mi. 29.11.2023 - Besprechung von AirDrop Mitschnitt usw.

## AirDrop
Die wichtigsten Erkenntnisse zu AirDrop zusammengefasst

### Sources
- TODO

## NearbyShare
Die wichtigsten Erkenntnisse zu NearbyShare zusammengefasst

### Source
- TODO

## NAT
https://en.wikipedia.org/wiki/Network_address_translation?useskin=vector

https://github.com/ccding/go-stun


### NAT Typen
- Basic NAT / One-To-One NAT: IP Addresse + Checksum wird geändert
- NAPT (network address and port translation) / IP Masquerading / Many-To-One NAT: Ein Netzwerk auf eine externe IP, IP + Port auf externe IP, Umschreiben in lokale Addresse, Basic Router.
-> Kommunikation kann nur aus dem lokalen Netzwerk heraus anfangen (sonst gibt es kein Mapping)
    - **Full Cone NAT**: 1:1 mapping intern <-> extern; Problem: Es wird nicht überprüft woher die Pakete kommen (jeder kann an intern senden indem er an extern sendet)
    - **Full Cone NAT mit Address Restriction**: Wie Full Cone, diesmal wird aber überprüft ob es schon eine Verbindung von intern -> extern gab. **NUR IP ADDRESSE wird überprüft**
    - **Port Restricted NAT**: Wie Address Restriction aber inklusive dem Port
    - **Symmetric NAT**: Pro interner Addresse + Port gibts ein externes Mapping (jede Verbindung bekommt ein eigenes Mapping). Externe können nur an das externe Mapping senden nachdem sie Pakete empfangen haben
- Mischung aus diesen Typen ist möglich, daher funktioniert das klassische STUN auch nicht mehr
- Source NAT: Verändert die ausgehenden Pakete und matched auf Pakete aus dem genatteten Netzwerk
- Destination NAT: Erlaubt Verbindungen von außerhalb mit (normalerweise) Client Computern. Ändert die Adresse von externen IPs

Um auf Linux herauszufinden wie lange eine Verbindung lebt kann man die Kommandos von [hier](https://serverfault.com/questions/481899/how-long-do-nat-mappings-live-for) verwenden:

```
> sysctl -a 2>/dev/null | grep timeout
...
net.netfilter.nf_conntrack_udp_timeout = 30
net.netfilter.nf_conntrack_udp_timeout_stream = 120
net.netfilter.nf_flowtable_udp_timeout = 30
...
```

Der Default Timeout für UDP scheint bei 30 Sekunden zu liegen.

### ICE Writeup
Die Funktionen die für die QUIC Umsetzung vielleicht relevant sein könnten [RFC-QUIC-NAT-TRAVERSAL](https://datatracker.ietf.org/doc/draft-seemann-quic-nat-traversal/).

1. Herausfinden von Adresspaaren (IP, Port). Wichtig: Die QUIC Implementierung muss hier zwischen STUN Paketen und QUIC Paketen unterscheiden können. QUIC Bit Greasing ist also nicht möglich. Idee hierfür könnte [Sektion 5.1.1 / 5.2](https://datatracker.ietf.org/doc/draft-seemann-quic-nat-traversal/) im ICE RFC Draft sein.
2. Die gefundenen Adressen *sollen* sofort nachdem sie gefunden wurden an den anderen Endpunkt gesendet werden (Trickle ICE). Hierfür gibt's einen neuen Pakettypen **ADD_ADDRESS**. Adressen die nicht mehr genutzt werden können / sollen können mit dem neuen Pakettyp **REMOVE_ADDRESS** entfernt werden.
3. Die Tatsache, dass Netzwerk Interfaces unbrauchbar werden können versuchen wir zu verhindern, indem wir mehrere Interfaces / Streams offen halten indem NAT Bindings erneuert werden, auch wenn die Verbindung nicht genutzt wird. Im Fall, dass ein Interface offline geht wechselt die Verbindung per [Connection Migration](https://datatracker.ietf.org/doc/html/rfc9000#name-connection-migration) auf die funktionierenden existierenden Interfaces / Verbindungen. Das sollte bereits nativ in QUIC funktionieren. Hier ist eventuell das Verwenden der Mechaniken in Multipath QUIC [QUIC-MULTIPATH-06](https://datatracker.ietf.org/doc/draft-ietf-quic-multipath/) relevant.
4. Im Fall von P2P Verbindungen zwischen zwei mobilen Geräten wo es keinen wirklichen Server / Client gibt muss QUIC allerdings auch hier erweitert werden. Nativ darf der Server keine [Probing Packets](https://datatracker.ietf.org/doc/html/rfc9000#name-probing-a-new-path) schicken. Um einen migrierten Pfad zu validieren muss das auch vom "Server" funktionieren. Eventuell könnte man sich hier auf einen Mechanismus einigen bei dem der Peer der den Socket für Verbindungen öffnet der Server ist und im Protokoll/Draft weiterhin so funktioniert wie bisher definiert. *Zu klären gilt noch ob die Erreichbarkeit von beiden Enden aus in diesem Fall zustande kommen kann*.
5. Der Matching Algorithmus wird ausgeführt. Unter 4.3 und 4.4 ist beides mal nur der *Client* für die Auswahl und das initiieren der Verbindung zuständig. Um die Komplexität gering zu halten sollten wir wahrscheinlich versuchen dieses Verhalten beizubehalten und nur eine Seite die Aufgabe der Berechnung und Initiierung auszuführen. *Wieder gilt, dass die genaue Funktion darüber entscheidet ob das reicht um de Erreichbarkeit von beiden Seiten aus sicherzustellen*.
6. Die maximale Anzahl an Connection ID limits muss eingehalten werden, was die gleichzeitig die Anzahl an parallelen Verbindungen limitiert. Das dürfte bereits ein Limit im [QUIC-MULTIPATH](https://datatracker.ietf.org/doc/draft-ietf-quic-multipath/) draft sein, den wir zusätzlich anpassen müssen.

Die Implementierung in Form von Paketen (und Logik?) wird zwar unter [QUIC-NAT-DRAFT](https://datatracker.ietf.org/doc/draft-seemann-quic-nat-traversal/) Abschnitt 4.5+ beschrieben aber für Multipath bzw. zwei mobile Peers fehlen wahrscheinlich noch Parameter. Die genauen Pakete kann man sich wahrscheinlich abschauen aber wo nötig nochmal ändern.

### QUIC Basics
- Probing a new Path: Testen der Erreichbarkeit mittels Path Validation Paketen bevor die Verbindung gewechselt wird. Path Validation Pakete sind: **PATH_CHALLENGE**, **PATH_RESPONSE**, **NEW_CONNECTION_ID** und **PADDING**. 

## Ideen
Das finden und sortieren der möglichen Verbindungspaare in **ICE** könnte man wahrscheinlich so in QUIC übernehmen. Zusätzlich ist gerade für das Multipath-Szenario die *valid list* interessant, da hier mehrere **unterschiedliche** Addresspaare enthalten sind. Wenn man diese Verbindungspaare entweder *alle* oder *k-redundanz* öffnet, sollte sich daraus schon eine erhöhte und stabilere Verbindung ergeben. Interessant wird noch das herausfinden ob eine Verbindung über lokales WiFi stattfindet. **Hierzu habe ich bisher wenig gesucht, das wäre sicherlich interessant zu verstehen wie man das feststellen kann. Die Frage bleibt dann wie und ob man diese Information an das Protokoll weiterleitet (braucht das Protokoll die Information um dann z.B. per WiFi im lokalen oder WiFiDirect im direkten Netzwerk nach Peers zu suchen?)**.

**Verwendungen**: Machine to Machine Communication (Talk)

*50045 Security Process for Adopting Machine to Machine Communication for Maintenance in Transportation with a Focus on Key Establishment, Sibylle Fröschle, TU Hamburg, Germany*:
[Talks / Paper](https://www.thinkmind.org/index.php?view=article&articleid=simul_2023_1_90_50045)

Eventuell macht es hier ebenfalls Sinn, sich Machine to Machine Communication anzuschauen.

### Sonstiges
Wenn man in der Chemie Bib den STUN resolver 2 mal laufe lässt kommen 2 unterschiedliche Ergebnisse raus und die Antworten dauern sehr lange.
Daraus lässt sich schließen, dass es sich um ein Symmetrisches NAT (wahrscheinlich) mit dynamischen Bindings handelt, sprich der schwierigsten Art von NAT bindings.

## Testing & Analyse
Zum Analysieren von QUIC und TLS Verbindungen:
https://pkg.go.dev/crypto/tls#example_Config_keyLogWriter

#### Schritte: 
1. In der Software die TLS Session Keys exportieren
2. Als Pre-Shared Master Keys in Wireshark einfügen
3. Decrypt Feld in Wireshark