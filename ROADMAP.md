# Roadmap — Modernization & Hardening

Living plan for making the Macrosoft Support desktop app easier to maintain,
test, ship and support. Status is updated as work lands on `main`.

Legend: ✅ done · 🚧 in progress · ⏳ planned · ⚠️ blocked

## Today — 2026-11-18

Theme: **foundations** (no user-visible behaviour changes).

| # | Item | Status | Commit |
|---|------|--------|--------|
| 1 | Roadmap, README, packaging metadata, CI quality gate, pruned dependencies | ✅ | _filled in below_ |
| 2 | Lazy app identity (remove network I/O at import time) | ⏳ | |
| 3 | Rotating file logging, replace ad-hoc `print` debugging | ⏳ | |
| 4 | HTTP client with timeouts and retries; migrate API calls | ⏳ | |
| 5 | Typed settings/persistence, pytest suite, roadmap update | ⏳ | |

Acceptance for today: `ruff` and `pytest` green in CI, no new runtime
dependencies, console behaviour preserved.

---

## Phase 0 — Security (⚠️ needs credential rotation by owner)

- ⏳ Rotate the Cloudflare service token and PeerTube root credentials that are
  currently stored in source (`app_config.py`, `rtmp_url_manager.py`).
- ⏳ Remove secrets from the repository and git history; inject them at build
  time or move privileged calls behind `online.macrosoft.sk`.
- ⏳ Verify Authenticode signature/hash of downloaded installers before silent
  execution.
- ⏳ Split the elevated helper from the UI so the window does not run as admin
  (Phase 4).

## Phase 1 — Engineering baseline

- ✅ `pyproject.toml` with project metadata, pinned runtime/build/dev deps.
- ✅ Prune unused dependencies (Eel/bottle/gevent/websocket stack).
- ✅ Ruff lint configuration.
- ✅ Pytest test layout and configuration.
- ✅ Pre-commit hook configuration.
- ✅ GitHub Actions CI on Windows (lint + tests).
- ✅ README with architecture, setup, run and build instructions.
- ⏳ Enable Pyright on the modern modules and add it to CI.
- ⏳ `CHANGELOG.md` maintained per release.
- ⏳ Single source of truth for the app version (read by build script).

## Phase 2 — Reliability & observability

- ✅ Remove import-time network calls; resolve identity lazily.
- ✅ Rotating file logging under `%APPDATA%` plus console mirror.
- ✅ HTTP client with explicit timeouts, bounded retries and typed errors.
- ✅ Typed settings/persistence with atomic writes.
- ⏳ Replace remaining broad `except` blocks with narrow handling + logging.
- ⏳ `Status` enum instead of `"enabled"/"disabled"/"checking"` literals.
- ⏳ Fix corrupted UI string (`"NeznA?me meno"`).
- ⏳ Timeouts on installer downloads and OBS WebSocket waits.

## Phase 3 — Architecture

- ⏳ Split `support_app/backend.py` (900+ lines, 25 Qt properties) into cohesive
  controllers behind one QML façade.
- ⏳ Replace repeated `@Property`/setter/notify boilerplate with a helper or
  typed state object.
- ⏳ Typed task runner with cancellation, timeouts and `error` signal.
- ⏳ Split `utils.py` into OBS, process and network modules.
- ⏳ Remove blocking sleeps from the GUI thread (`cleanup`).

## Phase 4 — UI, build & delivery

- ⏳ Extract QML `Theme` singleton/design tokens; split large pages.
- ⏳ Checked-in PyInstaller `.spec`; reproducible builds from lockfile.
- ⏳ Code signing for exe/installer.
- ⏳ Tag-driven release pipeline publishing a signed installer.
- ⏳ Crash reporting and log upload; version check/auto-update.
- ⏳ Least-privilege elevated helper.

## Definition of done

- CI (ruff + pytest) green on every push; Pyright clean on modern modules.
- No import-time network/filesystem I/O.
- Every network call has a timeout; every non-trivial failure is logged.
- Secrets live outside the repository; release artifacts are signed.
- Unit coverage on non-UI logic: config parsing, identity, settings, retries,
  browser profile parsing, status aggregation.
