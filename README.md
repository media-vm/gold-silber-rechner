# Gold- und Silberrechner

**English** · [Gold and Silver Calculator](README.en.md)

**Español** · [Descargar la calculadora de oro y plata](https://github.com/media-vm/gold-silber-rechner/releases/tag/v2.4) · [Código e instrucciones](README.es.md)

Der **Gold- und Silberrechner** ist eine kostenlose Anwendung zur Berechnung des Materialwerts von Gold und Silber anhand aktueller Edelmetallkurse.

Die Anwendung eignet sich zum Beispiel zur Bewertung von Münzen, Barren, Schmuck und anderen Gegenständen aus Gold oder Silber.

## Version

Aktuelle Quellcode-Version: **2.4**

Version 2.1 wird übersprungen. Version 2.0 bleibt als frühere Quellcode-Version erhalten.

## Download

Die gemeinsamen Downloads für Deutsch, Spanisch und Englisch stehen im [GitHub-Release v2.4](https://github.com/media-vm/gold-silber-rechner/releases/tag/v2.4). Die App wählt die Sprache anhand der Systemeinstellung. Mit `--lang de`, `--lang es` oder `--lang en` kannst du sie direkt wählen.

### Windows

- [Windows 10/11, 64 Bit](https://github.com/media-vm/gold-silber-rechner/releases/download/v2.4/Gold-Silver-Calculator-2.4-Windows-x64.exe)
- [Windows 7, 32 Bit](https://github.com/media-vm/gold-silber-rechner/releases/download/v2.4/Gold-Silver-Calculator-2.4-Windows7-x86.exe)

Beide portablen Dateien wurden mit dem selbstsignierten Zertifikat von Volker Andreas Müller signiert und tragen einen DigiCert-Zeitstempel. Der Fingerabdruck des Zertifikats lautet `5F2BD8D34D846C0197AC5A58343B6FDD407DE639`. Start und Berechnung wurden auf dem Windows-CI-Runner geprüft. Ein Starttest auf einem echten Windows-7-System steht aus.

### Debian / Ubuntu

[DEB-Paket 2.4-1 herunterladen](https://github.com/media-vm/gold-silber-rechner/releases/download/v2.4/gold-silber-rechner_2.4-1_all.deb)

```bash
sudo apt install ./gold-silber-rechner_2.4-1_all.deb
```

[SHA-256-Prüfsummen der drei Pakete](https://github.com/media-vm/gold-silber-rechner/releases/download/v2.4/SHA256SUMS.txt)

### Snap – Version 2.3 (amd64 und ARM64)

Im [Snap Store](https://snapcraft.io/gold-silber-rechner) im Kanal `latest/stable` verfügbar: amd64 Revision 11, ARM64 Revision 10. Bestehende Installation aktualisieren:

```bash
sudo snap refresh gold-silber-rechner
```

[amd64-Snap für lokale Installation herunterladen](https://github.com/media-vm/gold-silber-rechner/releases/download/v2.2/gold-silber-rechner_2.2_amd64.snap)

[ARM64-Snap für lokale Installation herunterladen](https://github.com/media-vm/gold-silber-rechner/releases/download/v2.2/gold-silber-rechner_2.2_arm64.snap)

Der Snap im Store enthält Deutsch und Spanisch auf dem Stand 2.3. Die oben verlinkten Snap-Dateien gehören zum Archiv-Release 2.2.

### Android – weiterhin Version 2.0

Die Android-APK bleibt bei Version 2.0. Der Android-Quellcode und ein Android-Build sind in diesem Repository nicht enthalten.

[Bisherige Android-APK aus Release v2.0](https://github.com/media-vm/gold-silber-rechner/releases/download/v2.0/gold-silver-calculator-v2.apk)

### Weitere Paketvarianten und Archiv

Ein MSIX-Paket wurde im Rahmen dieser Aktualisierung nicht für Version 2.2 erstellt oder veröffentlicht. Für ARM64 sind Build- und Veröffentlichungsworkflows vorhanden. Version 2.0 bleibt im [Release v2.0](https://github.com/media-vm/gold-silber-rechner/releases/tag/v2.0) und in der Git-Historie als Archiv erhalten.

### Projekt-Webseite

Weitere Informationen und Downloads:

https://linuga.org/gsr/

## Funktionen

- Berechnung des Materialwerts von Gold und Silber
- Eingabe des Gewichts
- Auswahl bzw. Eingabe der Feinheit
- Berechnung des enthaltenen Feingewichts
- Verwendung aktueller Gold- und Silberkurse
- übersichtliche grafische Oberfläche
- Unterstützung verschiedener Betriebssysteme

## Unterstützte Plattformen

Der Gold- und Silberrechner ist für mehrere Plattformen verfügbar:

- Windows
- Linux
- Android

Je nach Plattform stehen unterschiedliche Installationspakete zur Verfügung, darunter:

- Windows EXE
- Windows MSIX
- Debian DEB
- Snap
- Android APK

## Screenshot unter Linux

![Gold- und Silberrechner 2.3 auf Deutsch mit geöffnetem Währungsmenü und einer Beispielrechnung in Euro](images/screenshot-linux.png)

## Quellcode

Die Desktop-Version wurde in **Python** entwickelt.

Die grafische Benutzeroberfläche verwendet Tkinter.
Die Datei `gold-silver-value-calculator-german-v2.2.py` ist der gemeinsame Entwicklungsstand für Deutsch, Spanisch und Englisch. Alle drei Sprachen werden auf `main` gepflegt. Die veröffentlichten Pakete können einen älteren Stand enthalten.

Start aus dem Repository mit installiertem Python und Tkinter:

```bash
python -m pip install -r requirements.txt
python gold-silver-value-calculator-german-v2.2.py --lang de
```

## Code signing policy

Free code signing provided by SignPath.io, certificate by SignPath Foundation.

### Project roles

- Author / Committer: Volker Andreas Müller
- Reviewer: Volker Andreas Müller
- Approver: Volker Andreas Müller

### Privacy policy

See [PRIVACY.md](PRIVACY.md).

The application connects to `https://gsr.linuga.org/` to retrieve current gold and silver prices. It does not contain advertising, analytics or user tracking.

## Lizenz

Dieses Projekt steht unter der MIT License.

Siehe die Datei `LICENSE` im Repository.

Die aktuelle Entwicklungsfassung bietet auf Deutsch EUR, CHF und USD sowie Karatangaben und Sterlingsilber. Die zusätzlichen Währungen und Gewichtseinheiten für die spanische Oberfläche beschreibt die [spanische Anleitung](README.es.md).

## Paketbau

DEB reproduzierbar aus dem aktuellen Quellstand bauen:

```bash
python3 packaging/build-deb.py
```

Der Build auf `main` erzeugt das DEB-Paket 2.4-1 unter `dist/`.

Windows-Pakete werden über den GitHub-Actions-Workflow `Windows Build` aus derselben Python-Datei erstellt. Für einen Release werden die Windows-Builds vor der Veröffentlichung wie in [AGENTS.md](AGENTS.md) beschrieben signiert und geprüft. Der Windows-7-Laufzeithook stellt den Import `zoneinfo` über den Backport bereit, ohne den Anwendungscode zu verändern.
