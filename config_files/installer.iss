; Basic Inno Setup Script (myinstaller.iss)
[Setup]
AppName=Macrosoft Support
AppVersion=1.0
AppPublisher=Macrosoft s.r.o
AppPublisherURL=https://online.macrosoft.sk/
AppSupportURL=https://online.macrosoft.sk/
AppUpdatesURL=https://online.macrosoft.sk/
DefaultDirName={autopf}\Macrosoft Support
DisableProgramGroupPage=yes
OutputDir=.\installer_file
OutputBaseFilename=MacrosoftSupportInstaller
SetupIconFile=icon.ico
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest

[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"
Name: "sk"; MessagesFile: "Languages\Slovak.isl"

[Files]
; Slovak version
Source: "MacrosoftSupport\MacrosoftSupport.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "MacrosoftSupport\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs


[Icons]
Name: "{autoprograms}\Macrosoft Support"; Filename: "{app}\MacrosoftSupport.exe"
Name: "{autodesktop}\Macrosoft Support"; Filename: "{app}\MacrosoftSupport.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  InstallerPath: String;
  ConfigPath: String;
begin
  if CurStep = ssPostInstall then begin
    // Get the full path of the installer executable
    InstallerPath := ExpandConstant('{srcexe}');

    // Create path for output file
    ConfigPath := ExpandConstant('{app}\installer_path.txt');

    // Save directly to file with UTF-8 encoding
    SaveStringToFile(
      ConfigPath,
      'Installer Path: ' + InstallerPath + #13#10,
      False
    );
  end;
end;