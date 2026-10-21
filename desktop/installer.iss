; Inno Setup 6 — مثبّت حَكَم لنظام Windows
; البناء:  iscc /DAppVersion=1.0.0 desktop\installer.iss   (بعد تشغيل PyInstaller)
#ifndef AppVersion
  #define AppVersion "1.0.0"
#endif
#define AppName "Hakam"
#define AppPublisher "Hakam Project"
#define AppURL "https://github.com/bahattab/ai-legal-agent-arabic"

[Setup]
AppId={{6E1B7C64-3F2A-4D8E-9B1A-7A5C2F0D4E11}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}/issues
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=..\dist
OutputBaseFilename=Hakam-Setup-{#AppVersion}
SetupIconFile=assets\hakam.ico
UninstallDisplayIcon={app}\Hakam.exe
LicenseFile=..\LICENSE
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\dist\Hakam\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\Hakam.exe"
Name: "{group}\{#AppName} (open in browser)"; Filename: "{app}\Hakam.exe"; Parameters: "--browser"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\Hakam.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Hakam.exe"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent

; ملاحظة: بيانات المستخدم في %APPDATA%\Hakam لا تُحذف عند إلغاء التثبيت (القضايا والإعدادات محفوظة)
