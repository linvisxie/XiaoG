# XiaoG Web Preview WP-3 Handoff

Activation: `XIAOG-AUTOPILOT-WEB-PREVIEW-WP3-2026-09-14-V1`  
State: `HANDOFF_REQUIRED`

WP-3 replacement candidate: `d3210a5e510ce060e4ffe55ca7b53087419467df` (verification patch; replaces `163921c75032da4867cae75935033fd1049e0c3e`).

## Delivered

- Preview reads per-invite high-entropy credentials only from `XIAOG_PREVIEW_INVITES`; no credential is committed, logged, returned, or stored in session SQLite.
- Access exchange issues an opaque Secure, HttpOnly, SameSite cookie with finite expiry and binds it to a non-secret invite ID. Failed access creates no session database. Logout invalidates the in-memory session.
- Preview private APIs require an authenticated invite session; only health, static shell, and access exchange remain unauthenticated. Local mode is unchanged.
- Per-invite/global rolling request and generation quotas plus per-invite/global generation concurrency guard run before Provider selection. Input length is bounded. Counters are in-memory risk controls and reset on restart; they are not billing-grade spend caps.
- Added minimal Preview access-code overlay and logout control. Credentials are not persisted in browser storage.

## Verification

- `./.venv/Scripts/python.exe run_core_tests.py`: 41 passed, 0 failures/errors. New `tests/test_preview_access.py` verifies invalid invite rejection with no session DB, invite/session identity binding, cross-invite SQLite non-access, no invite credential in SQLite/redacted text, per-invite/global request quota, per-invite/global generation concurrency, guard rejection before a generation is admitted, direct release of active counters, and logout invalidation.
- `./.venv/Scripts/python.exe tests/preview_release_smoke.py`: passed. It verifies a valid fake invite exchange, invite ID response binding, Secure/HttpOnly/SameSite/Max-Age cookie attributes, authenticated Conversation creation, then logout and original-cookie 401; no Provider request.
- Python/Node syntax and `git diff --check`: passed.
- No independent fake-stream test yet proves counter release through all actual streaming success/error/cancel paths; direct admission/release coverage exists. Do not present that specific stream-outcome coverage as complete.
- No real Provider, invite distribution, external secret, hosting, remote, DNS, tunnel, or external access occurred. Terra remains disabled in Preview.

## Remaining blockers

WP-4/deployment remains unauthorized. Before real invited access, Product Owner must separately authorize GitHub/remote/push, hosting, DNS, external secret injection, external access, and provider-side budget controls. Terra needs its separate server-side readiness audit.

`AUTOPILOT_HANDOFF_READY`
