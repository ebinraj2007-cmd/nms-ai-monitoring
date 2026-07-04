[Setup]
AppName=NMS AI Monitoring
AppVersion=1.0
DefaultDirName={autopf}\NMS AI Monitoring
DefaultGroupName=NMS AI Monitoring
OutputDir=output
OutputBaseFilename=NMS-AI-Monitoring-Setup
Compression=lzma
SolidCompression=yes

[Components]
Name: "server"; Description: "Central Server (Prometheus + Grafana)"; Types: full compact custom; Flags: fixed
Name: "agent"; Description: "Monitoring Agent"; Types: full custom
Name: "aiengine"; Description: "AI Prediction Engine"; Types: full custom

[Files]
Source: "..\docker-compose.yml"; DestDir: "{app}"; Components: server
Source: "..\prometheus\*"; DestDir: "{app}\prometheus"; Components: server; Flags: recursesubdirs
Source: "..\ai-engine\*"; DestDir: "{app}\ai-engine"; Components: aiengine; Flags: recursesubdirs
Source: "..\README.md"; DestDir: "{app}"

[Icons]
Name: "{group}\NMS AI Monitoring"; Filename: "{app}\README.md"
Name: "{group}\Uninstall NMS AI Monitoring"; Filename: "{uninstallexe}"

[Run]
Filename: "notepad.exe"; Parameters: "{app}\README.md"; Description: "View setup instructions"; Flags: postinstall nowait skipifsilent
