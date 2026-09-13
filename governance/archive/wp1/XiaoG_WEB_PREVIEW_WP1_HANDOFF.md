# XiaoG Web Preview WP-1 Handoff

Date: 2026-09-14 Asia/Shanghai  
Activation: `XIAOG-AUTOPILOT-WEB-PREVIEW-WP1-2026-09-14-V1`  
Autopilot State: `HANDOFF_REQUIRED`

## Window

- Start provenance: `main` at `818376df2a62eb20b8f0d7f0ad72f195543d0a03`; the only initial working-tree differences were the Product Owner / Tech Lead-provided governance documents.
- WP-1 local candidate: `12a3ed352b0af3db1f611babcb1d295fd0982114` (`candidate: add safe ephemeral preview mode`).
- Allowed work: bounded local code/config/test/docs changes for a release baseline and non-persistent Preview mode.
- Stop gate: WP-1 complete; Tech Lead review required before any WP-2 work.

## Delivered

- Runtime configuration now has explicit `local` and `preview` modes, with configurable host, port, data directory/database path, log directory, and release identity. Existing local defaults stay `127.0.0.1:8000` and `data/xiaog.db`.
- Preview requires a non-local `XIAOG_DATA_DIR` and explicit immutable `XIAOG_RELEASE_ID`; it rejects accidental use of the Product Owner's `data/` directory.
- Preview API callers receive a server-issued opaque HttpOnly session cookie. Every live session has an independently initialized SQLite database beneath the Preview-owned directory. The directory is removed at Preview startup, making this boundary non-persistent across process starts.
- Request-scoped database selection keeps Preview Conversation, Settings, Memory, Search, and usage operations inside that session's database. Streaming retains the originating request scope.
- Preview disables FastAPI docs/schema URLs. No backup/import/export or file-byte API exists in the current service.
- Provider policy remains Registry/configuration-driven. WP-1 validates a DeepSeek-only Preview allowlist, so Terra is unavailable without a health check or Codex App Server start. Local mode retains Terra unchanged.
- `/health` now reports commit, runtime mode, and release identity for later deployment verification and immutable-revision rollback.

## Verification

- `./.venv/Scripts/python.exe run_core_tests.py`: 37 passed, 0 failed, 0 errors, 0 skipped.
- Python compilation passed for the changed backend/entrypoint modules.
- `node --check frontend/app.js` and `node --check frontend/i18n.js` passed.
- `git diff --check` passed.
- New deterministic Preview tests cover unchanged local defaults, explicit Preview configuration/release identity, DeepSeek-only provider policy, closed docs policy, separate session SQLite state, cross-session Conversation non-access, and startup cleanup of temporary session databases.
- No real Provider, secret, listener, tunnel, deployment, external service, browser-profile, database copy, or local user-data inspection was used.

## Remaining WP-2 Blockers

- No hosting topology, external secret store, HTTPS edge, invite/access control, rate/cost controls, cloud data volume, CI/CD, remote, DNS, or deployment artifact exists or is authorized.
- Preview cookie/session isolation is a local bounded transient boundary, not an invited-access system. A future external access gate must add authorized invitation handling and edge/app controls.
- Terra remains conditional pending its separate server-side readiness/authentication audit.
- The existing real default-Edge generation-time navigation Known Issue remains unresolved and non-blocking; synthetic tests do not claim to fix it.

## Recommended Next Decision

Tech Lead should review this handoff and, only if Product Owner separately authorizes the necessary external actions, issue a bounded WP-2 Activation for isolated runtime/data/secret boundaries. Do not begin WP-2, hosting, GitHub, DNS, deployment, or Terra work in this window.

`AUTOPILOT_HANDOFF_READY`
