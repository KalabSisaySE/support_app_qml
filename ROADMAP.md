# Roadmap — Modernization & Hardening

Living plan for making the Macrosoft Support desktop app easier to maintain,
test, ship and support. Status is updated as work lands on `main`.

Legend: ✅ done · 🚧 in progress · ⏳ planned · ⚠️ blocked

## Today — 2026-11-19

Theme: **architecture & build metadata** (still no user-visible behaviour changes).

Baseline tagged `legacy-v1.0.0` at `e998116` (state before modernization).

| # | Item | Status | Commit |
|---|------|--------|--------|
| 1 | Declarative Qt property helper + `Status` enum | ✅ | `b6514b9` |
| 2 | Explicit `TaskRunner`/`WorkerTask` lifecycle | ✅ | `75d473a` |
| 3 | Log previously swallowed exceptions | ✅ | `78349e6` |
| 4 | Single-source version + rendered build metadata + changelog | ✅ | `67384dd` |
| 5 | Split `utils.py` into OBS/system/API modules + tests | ✅ | _this commit_ |

Acceptance: `ruff`, `pyright` and 59 pytest tests green; QML-facing property
and signal names unchanged.

## 2026-11-18 — foundations

Theme: **foundations** (no user-visible behaviour changes).

| # | Item | Status | Commit |
|---|------|--------|--------|
| 1 | Roadmap, README, packaging metadata, CI quality gate, pruned dependencies | ✅ | `aa42e3d` |
| 2 | Typed settings + lazy app identity (no network I/O at import time) | ✅ | `4cca6fa` |
| 3 | Rotating file logging, replace ad-hoc `print` debugging | ✅ | `75e5808` |
| 4 | HTTP client with timeouts and retries; migrate API calls | ✅ | `22d0e09` |
| 5 | pytest suite for config/settings/api/reporting/status, roadmap update | ✅ | _this commit_ |

Acceptance for today: `ruff` and `pytest` green in CI (30 tests), no new
runtime dependencies, console behaviour preserved.

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
- ✅ Pyright configuration + CI type check for the modern modules.
- ✅ `CHANGELOG.md` maintained per release.
- ✅ Single source of truth for the app version (rendered into build metadata).

## Phase 2 — Reliability & observability

- ✅ Remove import-time network calls; resolve identity lazily.
- ✅ Rotating file logging under `%APPDATA%` plus console mirror.
- ✅ HTTP client with explicit timeouts, bounded retries and typed errors.
- ✅ Typed settings/persistence with atomic writes.
- ✅ Replace silently swallowed exceptions with debug/warning logging.
- ✅ `Status` enum instead of `"enabled"/"disabled"/"checking"` literals.
- ⏳ Timeouts on OBS WebSocket waits (installer download and desktop-auth
  timeouts already added).

## Phase 3 — Architecture

- ⏳ Split `support_app/backend.py` (still ~700 lines) into cohesive
  controllers behind one QML façade.
- ✅ Replace repeated `@Property`/setter/notify boilerplate with a helper.
- ✅ Explicit `TaskRunner`/`WorkerTask` lifecycle (cancellation/timeouts still
  planned).
- ✅ Split `utils.py` into OBS (`obs_control`), system (`system_info`) and API
  (`macrosoft_api`) modules.
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
