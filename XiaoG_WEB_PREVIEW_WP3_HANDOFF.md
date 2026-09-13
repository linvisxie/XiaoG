# XiaoG Web Preview WP-3 Handoff

Activation: `XIAOG-AUTOPILOT-WEB-PREVIEW-WP3-2026-09-14-V1`  
State: `HANDOFF_REQUIRED`

## Delivered

- Preview reads per-invite high-entropy credentials only from `XIAOG_PREVIEW_INVITES`; no credential is committed, logged, returned, or stored in session SQLite.
- Access exchange issues an opaque Secure, HttpOnly, SameSite cookie with finite expiry and binds it to a non-secret invite ID. Failed access creates no session database. Logout invalidates the in-memory session.
- Preview private APIs require an authenticated invite session; only health, static shell, and access exchange remain unauthenticated. Local mode is unchanged.
- Per-invite/global rolling request and generation quotas plus per-invite/global generation concurrency guard run before Provider selection. Input length is bounded. Counters are in-memory risk controls and reset on restart; they are not billing-grade spend caps.
- Added minimal Preview access-code overlay and logout control. Credentials are not persisted in browser storage.

## Verification

- Core regression: 37 passed.
- WP-2 ASGI release smoke: passed using a fake local invite credential and no Provider request.
- Python/Node syntax and `git diff --check`: passed.
- No real Provider, invite distribution, external secret, hosting, remote, DNS, tunnel, or external access occurred. Terra remains disabled in Preview.

## Remaining blockers

WP-4/deployment remains unauthorized. Before real invited access, Product Owner must separately authorize GitHub/remote/push, hosting, DNS, external secret injection, external access, and provider-side budget controls. Terra needs its separate server-side readiness audit.

`AUTOPILOT_HANDOFF_READY`
