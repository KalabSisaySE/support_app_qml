# Roadmap — Modernization & Hardening

Living plan for making the Macrosoft Support desktop app easier to maintain,
test, ship and support. Status is updated as work lands on `main`.

Legend: ✅ done · 🚧 in progress · ⏳ planned · ⚠️ blocked

## Today — 2026-11-23

Theme: **backend decomposition & QML tokens**.

| # | Item | Status | Commit |
|---|------|--------|--------|
| 1 | Account authentication flow extracted + tested | ✅ | `1465d45` |
| 2 | Support WebSocket session extracted + tested | ✅ | `b37b4f6` |
| 3 | Progress aggregation extracted + tested | ✅ | `73bd57c` |
| 4 | QML `Theme` singleton and design tokens | ✅ | `24b1456` |
| 5 | CI PyInstaller smoke build + docs | ✅ | _this commit_ |

Acceptance: `ruff`/`pyright` clean, 95 pytest tests green, no QML lint errors,
offscreen control load resolves the Theme singleton.

## 2026-11-20 — runtime hardening & delivery

| # | Item | Status | Commit |
|---|------|--------|--------|
| 1 | Duplicate-task guard + worker failure handling | ✅ | `c1b2179` |
| 2 | One-click flow extracted into a tested controller | ✅ | `a9d4709` |
| 3 | Non-blocking shutdown/OBS startup + bounded handshake | ✅ | `67b4f15` |
| 4 | Checked-in PyInstaller spec + tag-driven release workflow | ✅ | `491481c` |
| 5 | Advisory Authenticode verification for installers | ✅ | _this commit_ |

Acceptance: `ruff`/`pyright` clean, 76 pytest tests green, local build produced
`MacrosoftSupport.exe` with version 1.0.0.0 and installer `AppVersion=1.0.0`.

## 2026-11-19 — architecture & build metadata

Theme: **architecture & build metadata** (no user-visible behaviour changes).

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
- ✅ Advisory Authenticode verification of downloaded installers (logged in the
  support log; enforcement awaits a signed Macrosoft installer).
- ⏳ Remove secrets from the repository and git history; inject them at build
  time or move privileged calls behind `online.macrosoft.sk`.
- ⏳ Split the elevated helper from the UI so the window does not run as admin
  (Phase 4).

## Phase 1 — Engineering baseline

- ✅ `pyproject.toml` with project metadata, pinned runtime/build/dev deps.
- ✅ Prune unused dependencies (Eel/bottle/gevent/websocket stack).
- ✅ Ruff lint configuration.
- ✅ Pytest test layout and configuration.
- ✅ Pre-commit hook configuration.
- ✅ GitHub Actions CI on Windows (lint + tests).
- ✅ CI PyInstaller smoke build on `main`/PRs.
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
- ✅ Bounded waits: installer downloads, desktop-auth polling and the OBS
  websocket handshake all have timeouts; OBS startup is non-blocking.

## Phase 3 — Architecture

- 🚧 Split `support_app/backend.py` into cohesive controllers behind one QML
  façade (one-click, account and support-websocket flows extracted; OBS
  session remains).
- ✅ Replace repeated `@Property`/setter/notify boilerplate with a helper.
- ✅ Explicit `TaskRunner`/`WorkerTask` lifecycle with duplicate guards and
  error reporting (cooperative cancellation still planned).
- ✅ Split `utils.py` into OBS (`obs_control`), system (`system_info`) and API
  (`macrosoft_api`) modules.
- ✅ Remove blocking sleeps from the GUI thread (cleanup now flushes the socket).

## Phase 4 — UI, build & delivery

- 🚧 Extract QML `Theme` singleton/design tokens (done for controls and
  `main.qml`); split large pages next.
- ✅ Checked-in PyInstaller `.spec`; build renders version metadata.
- ⏳ Code signing for exe/installer.
- ✅ Tag-driven release pipeline (builds and publishes; signing awaits a
  certificate).
- ⏳ Crash reporting and log upload; version check/auto-update.
- ⏳ Least-privilege elevated helper.

## Definition of done

- CI (ruff + pytest) green on every push; Pyright clean on modern modules.
- No import-time network/filesystem I/O.
- Every network call has a timeout; every non-trivial failure is logged.
- Secrets live outside the repository; release artifacts are signed.
- Unit coverage on non-UI logic: config parsing, identity, settings, retries,
  browser profile parsing, status aggregation.
