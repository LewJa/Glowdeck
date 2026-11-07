; Inno Setup script - builds Glowdeck-Setup.exe from the PyInstaller output in dist\Glowdeck
#define AppName "Glowdeck"
#define AppExe "Glowdeck.exe"
#define AppVer "2.0.0"

[Setup]
AppId={{6D1F3A52-9C47-4E0B-8A1D-2B7E5C93F0A4}
AppName={#AppName}
AppVersion={#AppVer}
DefaultDirName={localappdata}\Programs\Glowdeck
DefaultGroupName={#AppName}
PrivilegesRequired=lowest
OutputDir=installer_out
OutputBaseFilename=Glowdeck-Setup
SetupIconFile=assets\icon.ico
UninstallDisplayIcon={app}\{#AppExe}
Compression=lzma2
SolidCompression=yes
DisableProgramGroupPage=yes
CloseApplications=force

[Tasks]
Name: "autostart"; Description: "Start with Windows"; GroupDescription: "Options:"
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Options:"; Flags: unchecked

[Files]
Source: "dist\Glowdeck\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "Glowdeck"; ValueData: """{app}\{#AppExe}"" --hidden"; Tasks: autostart; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueName: "Glowdeck"; Flags: dontcreatekey uninsdeletevalue

[Run]
Filename: "{app}\{#AppExe}"; Description: "Start Glowdeck"; Flags: nowait postinstall skipifsilent
