#define MyAppName "Gold- und Silberrechner"
#define MyAppVersion "1.0"
#define MyAppPublisher "Volker Müller"
#define MyAppExeName "Gold-Silber-Rechner.exe"

[Setup]
AppId={{6F7297DB-0893-4ACB-8590-F47443AA6209}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

DefaultDirName={autopf}\Gold-Silber-Rechner
DefaultGroupName=Gold- und Silberrechner

OutputDir=installer
OutputBaseFilename=Gold-Silber-Rechner-Setup-1.0

SetupIconFile=gold-silber-icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

Compression=lzma2
SolidCompression=yes

WizardStyle=modern

ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

PrivilegesRequired=admin

[Files]
Source: "dist\Gold-Silber-Rechner.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\gold-silber-icon.png"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Gold- und Silberrechner"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Gold- und Silberrechner deinstallieren"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Gold- und Silberrechner"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Desktop-Verknüpfung erstellen"; GroupDescription: "Zusätzliche Verknüpfungen:"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Gold- und Silberrechner starten"; Flags: nowait postinstall skipifsilent
