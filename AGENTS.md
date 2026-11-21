# Windows-Veröffentlichungen

Vor der öffentlichen Bereitstellung neuer Windows-EXE-Downloads für den Gold- und Silberrechner die jeweilige Datei mit Volker Andreas Müllers bestehendem Codesigning-Zertifikat signieren. Das gilt für deutsche und spanische Releases sowie für Website-Downloads. Der freigegebene Zertifikat-Fingerabdruck ist `5F2BD8D34D846C0197AC5A58343B6FDD407DE639` (SHA-1 als Zertifikatkennung). Für die Dateisignatur und den RFC-3161-Zeitstempel SHA-256 verwenden.

Vor dem Austausch Signatur, Zertifikat-Fingerabdruck, Zeitstempel und SHA-256-Prüfsumme prüfen. Nach der Veröffentlichung die Datei erneut vom öffentlichen Link herunterladen, Signatur und Prüfsumme bestätigen und die dokumentierten Prüfsummen aktualisieren. Wenn der Schlüssel nicht verfügbar ist, die EXE für die Signierung vorbereiten und mit der Veröffentlichung warten.

Private Schlüssel, PFX-Dateien und Passwörter bleiben im lokalen Signiervorgang. Wenn eine PFX entsperrt werden muss, das Passwort verdeckt im lokalen Signierdialog eingeben lassen. Es gehört nicht in den Chat, das Repository, Build-Artefakte oder Protokolle.
