# Macrosoft Support (QML)

Windows desktop support application built with **Python 3.13 + PySide6/QML**.
It combines remote-support setup (Macrosoft Connect), device/browser
permission fixes, OBS installation and lecture recording helpers.

The UI is QML; Python exposes a single `MacrosoftBackend` object to QML and
runs long operations in `QThread` workers.

## Architecture

```
main.py                         Qt bootstrap (loads qml/main.qml)
launcher.py                     UAC elevation launcher
build_project.py                PyInstaller + Inno Setup build automation
qml/                            QML views and reusable controls
support_app/
  app_config.py                 endpoints, paths, Cloudflare headers, lazy identity
  backend.py                    QObject facade exposed to QML
  workers/                      background workers (install, service, OBS, ...)
  tasks.py                      QThread worker lifecycle
  settings.py                   typed persistence + installer access code
  api.py                        HTTP client (timeouts, retries)
  logging_setup.py              rotating file + console logging
  version.py                    single source of the app version
  qt_bindings.py                declarative Qt property helper
  status.py                     Status enum for QML indicators
  macrosoft_connect.py          install paths / service / RustDesk reporting
  macrosoft_api.py              full-name lookup and web links
  obs_control.py                OBS detection, launch, config
  system_info.py                process/service/network/installation checks
  rtmp_url_manager.py           PeerTube live-video provisioning
  registry_permission_manager.py
  browser_permission_manager.py
  rust_service_manager.py
```

See [ROADMAP.md](ROADMAP.md) for the modernization plan and current status.

## Requirements

- Windows 10/11 (x64)
- Python 3.13
- Administrator rights for permission/service operations

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt   # runtime + build + dev tools
```

## Run

```powershell
python main.py
```

## Quality checks

```powershell
python -m ruff check .
python -m pyright
python -m pytest
```

CI runs the same commands on a Windows runner (see `.github/workflows/ci.yml`).

## Build

```powershell
python build_project.py
```

This produces a PyInstaller onedir build in `output/` and prepares the Inno
Setup sources (`config_files/installer.iss`).

## Notes

- Application logs are written to `%APPDATA%\MacrosoftSupport\support_app.log`.
- Persistent settings live in `%APPDATA%\MacrosoftSupport\config.json`.
- The installer access code is read from `installer_path.txt` next to the
  executable, with a legacy filename fallback.
