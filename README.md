# Gold- und Silberrechner

Der **Gold- und Silberrechner** ist eine kostenlose Anwendung zur Berechnung des Materialwerts von Gold und Silber anhand aktueller Edelmetallkurse.

Die Anwendung eignet sich zum Beispiel zur Bewertung von Münzen, Barren, Schmuck und anderen Gegenständen aus Gold oder Silber.

## Version

Aktuelle Quellcode-Version: **2.2**

Version 2.1 wird übersprungen. Version 2.0 bleibt als frühere Quellcode-Version erhalten.

## Download

### Debian / Ubuntu – Version 2.2

[DEB-Paket Version 2.2 herunterladen](https://github.com/media-vm/gold-silber-rechner/raw/refs/heads/main/downloads/gold-silber-rechner_2.2-1_all.deb)

```bash
sudo apt install ./gold-silber-rechner_2.2-1_all.deb
```

Das Paket liegt direkt im Repository unter `downloads/`. Ein GitHub-Release für Version 2.2 wurde noch nicht veröffentlicht.

SHA-256: `da8e70a8f9b900c3e3a962b0b06b6ec2672198738e4eadbf589b65f289afb796`

### Frühere Installationspakete (Version 2.0)

Die bisherigen Installationspakete der Version 2.0 stehen über die GitHub-Releases zur Verfügung. Das DEB-Paket für Version 2.2 ist oben direkt verlinkt:

https://github.com/media-vm/gold-silber-rechner/releases

### Windows

Für Windows steht eine ausführbare EXE-Datei bereit:

`Gold-Silber-Rechner-2.0.exe`

Die Anwendung kann direkt gestartet werden.

### Debian / Ubuntu

Für Debian-basierte Linux-Systeme steht ein DEB-Paket zur Verfügung:

`gold-silber-rechner_2.0-1_all.deb`

Installation:

```bash
sudo apt install ./gold-silber-rechner_2.0-1_all.deb
```

### Snap

Für Linux steht außerdem ein Snap-Paket zur Verfügung:

`gold-silber-rechner_2.0_amd64.snap`

Lokale Installation:

```bash
sudo snap install --dangerous ./gold-silber-rechner_2.0_amd64.snap
```

Die Anwendung ist außerdem über den Snap Store erhältlich.

### Android

Für Android steht eine APK-Datei zur Verfügung:

`gold-silber-rechner-2.0.apk`

Bei direkter Installation der APK kann Android eine Bestätigung für die Installation aus einer externen Quelle verlangen.

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

## Screenshots

### Linux

![Gold- und Silberrechner unter Linux](images/screenshot-linux.png)

### Windows

![Gold- und Silberrechner unter Windows](images/screenshot-windows.png)

## Quellcode

Die Desktop-Version wurde in **Python** entwickelt.

Die grafische Benutzeroberfläche verwendet Tkinter.
Die Datei `gold-silver-value-calculator-german-v2.2.py` enthält den aktuellen Quellcode der Desktop-Version 2.2.

Start aus dem Repository mit installiertem Python und Tkinter:

```bash
python -m pip install -r requirements.txt
python gold-silver-value-calculator-german-v2.2.py
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
