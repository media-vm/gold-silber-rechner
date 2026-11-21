# Windows-Veröffentlichungen

Vor der öffentlichen Bereitstellung neuer Windows-EXE-Downloads für den Gold- und Silberrechner die jeweilige Datei mit Volker Andreas Müllers bestehendem Codesigning-Zertifikat signieren. Das gilt für deutsche und spanische Releases sowie für Website-Downloads. Der freigegebene Zertifikat-Fingerabdruck ist `5F2BD8D34D846C0197AC5A58343B6FDD407DE639` (SHA-1 als Zertifikatkennung). Für die Dateisignatur und den RFC-3161-Zeitstempel SHA-256 verwenden.

Vor dem Austausch Signatur, Zertifikat-Fingerabdruck, Zeitstempel und SHA-256-Prüfsumme prüfen. Nach der Veröffentlichung die Datei erneut vom öffentlichen Link herunterladen, Signatur und Prüfsumme bestätigen und die dokumentierten Prüfsummen aktualisieren. Wenn der Schlüssel nicht verfügbar ist, die EXE für die Signierung vorbereiten und mit der Veröffentlichung warten.

Private Schlüssel, PFX-Dateien und Passwörter bleiben im lokalen Signiervorgang. Wenn eine PFX entsperrt werden muss, das Passwort verdeckt im lokalen Signierdialog eingeben lassen. Es gehört nicht in den Chat, das Repository, Build-Artefakte oder Protokolle.

Beim nächsten Windows-Build das GSR-Fenstersymbol in die portable PyInstaller-EXE einbetten und beim Start explizit als Tk-Fenstersymbol laden. Für die Windows-10/11- und die Windows-7-EXE jeweils prüfen, dass die Titelleiste auch bei einer alleinstehenden EXE in einem leeren Ordner das GSR-Symbol anstelle der Tk-Feder zeigt. Das im Explorer sichtbare EXE-Symbol allein gilt nicht als Nachweis.

# Gemeinsamer Desktop-Quellcode

Deutsch, Spanisch und Englisch verwenden dieselbe Anwendungsdatei `gold-silver-value-calculator-german-v2.2.py` auf `main`. Änderungen an der Berechnung, der Oberfläche und dem Paketbau dort pflegen. `README.md`, `README.es.md` und `README.en.md` beschreiben die drei Sprachmodi. Der Zweig `es` bleibt als Kompatibilitätsverweis für bestehende Links und ist kein eigener Entwicklungszweig.
