; Cripto-Bot Setup Script for Inno Setup
; Creates a professional installer for Windows

#define MyAppName "Cripto-Bot"
#define MyAppVersion "1.0"
#define MyAppPublisher "Michael Camacho"
#define MyAppURL "mailto:91pixelsusa@gmail.com"
#define MyAppExeName "Cripto-Bot.exe"

[Setup]
; App Information
AppId={{8F3A4E2D-9B1C-4A7E-8D2F-1E5C9A4B6D3E}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion} Beta
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE.txt
InfoBeforeFile=INSTALL_INFO.txt
OutputDir=installer_output
OutputBaseFilename=Cripto-Bot-Setup-v1.0
SetupIconFile=assets\Cripto-Bot.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main Executable
Source: "dist\Cripto-Bot.exe"; DestDir: "{app}"; Flags: ignoreversion

; Assets folder
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

; Configuration files
Source: ".env.example"; DestDir: "{app}"; Flags: ignoreversion
Source: "coinbase_ecdsa_key.txt"; DestDir: "{app}"; Flags: ignoreversion; AfterInstall: PromptForAPIConfig

; Documentation
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme
Source: "MANUAL_TEST_CASES_ES.md"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "EXECUTABLE_README.md"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "EXECUTABLE_FIX.md"; DestDir: "{app}\docs"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:ProgramOnTheWeb,{#MyAppName}}"; Filename: "{#MyAppURL}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
Filename: "notepad.exe"; Parameters: """{app}\.env.example"""; Description: "Configure API Keys (Important!)"; Flags: nowait postinstall

[Code]
var
  ConfigPage: TInputQueryWizardPage;
  
procedure InitializeWizard;
begin
  ConfigPage := CreateInputQueryPage(wpSelectTasks,
    'API Configuration', 
    'Coinbase API Keys Setup',
    'You will need to configure your Coinbase API keys after installation. ' +
    'The installer will open .env.example file for you to edit.');
end;

procedure PromptForAPIConfig;
begin
  // This runs after file copy
  MsgBox('IMPORTANT: You need to configure your API keys!' + #13#10 + #13#10 +
         '1. Open the .env.example file in the installation folder' + #13#10 +
         '2. Add your Coinbase API credentials' + #13#10 +
         '3. Save the file as .env (remove .example)' + #13#10 + #13#10 +
         'Installation folder: ' + ExpandConstant('{app}'), 
         mbInformation, MB_OK);
end;

[UninstallDelete]
Type: files; Name: "{app}\trading_bot.db"
Type: files; Name: "{app}\.env"
Type: dirifempty; Name: "{app}\assets"
Type: dirifempty; Name: "{app}\docs"
Type: dirifempty; Name: "{app}"
