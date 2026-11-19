# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/) and the project uses
semantic versioning.

## Unreleased

### Added

- ROADMAP and README with architecture, setup and build instructions.
- CI quality gate (ruff, Pyright on modern modules, pytest) on Windows.
- Rotating file logging under `%APPDATA%\MacrosoftSupport\support_app.log`.
- Typed settings module with atomic writes.
- HTTP client with explicit timeouts and bounded GET retries.
- Declarative Qt property helper, `Status` enum and `TaskRunner` worker
  lifecycle.
- Test suite covering settings, identity, HTTP policy, reporting, browser
  profiles, RTMP names and backend status/property behaviour.

### Changed

- Application identity is resolved lazily; importing the app no longer
  performs network I/O.
- Dependencies are declared in `pyproject.toml`; unused Eel/bottle/gevent
  stack removed.
- Worker threads are cleaned up idempotently, even if a completion slot
  raises.
- Previously swallowed exceptions are logged at debug/warning level.
- Build metadata is rendered from `support_app/version.py`.

## 1.0.0 — legacy baseline

- Original Macrosoft Support application, tagged as `legacy-v1.0.0` before
  the modernization work.
