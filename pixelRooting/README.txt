Die boot.img ist das Android Q bzw. Android 10 Factory Image von Google selber was benutzt wurde um das Handy zu rooten. Um das Handy wieder zurückzusetzen dieses mittels fastboot wieder auf das Gerät booten.

Das geht wie folgt:

Das Handy mittels adb in den bootloader booten:

> adb reboot bootloader

Anschließend die Datei vom PC aus flashen:

> fastboot devices
> fastboot flash boot --slot all boot.img

Das sollte reichen.

Die zweite Datei magisk_patched... ist das gerootete Image. Flashen geht genauso wie mit der anderen Datei. Nur SU ist dann installiert.
