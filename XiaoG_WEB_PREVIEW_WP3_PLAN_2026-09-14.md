# XiaoG Web Preview WP-3 Plan — Invited Access / Rate / Cost / Abuse Boundary

**Date:** 2026-09-14  
**Document Type:** Tech Lead Engineering Plan  
**Track:** XiaoG Limited Public Preview v1  
**Prerequisite:** WP-2 accepted by Tech Lead  
**Accepted WP-2 product candidate:** `da5bb6c27ab3c33b7275eac8e686b16c53e057ad`  
**WP-2 governance closeout HEAD:** `4d7eb3271b86661108a485c22a3ef321210498bf`

---

## 1. Goal

WP-3 makes the isolated ephemeral Preview safe enough for a **small invited group** before any real public hosting is authorized.

WP-3 covers four boundaries:

1. invited access / authentication;
2. per-invite and global rate limits;
3. concurrency / spend-risk controls;
4. minimal abuse controls.

WP-3 remains a **local engineering window**. It does not create GitHub, hosting, DNS, external secrets, public access, or real Provider traffic.

---

## 2. Preview v1 Access Model

Preview v1 remains:

- invite-only;
- ephemeral / non-persistent;
- DeepSeek-first;
- Terra disabled pending its separate audit;
- no open registration;
- no email/password account system;
- no OAuth / social login;
- no persistent user profile system.

### 2.1 Per-invite credentials

Use **separate high-entropy invite credentials per invited person**, rather than one shared global password.

Each configured invitation must have:

- a non-secret `invite_id` / label;
- a server-side secret credential or safe derived representation;
- an enabled/disabled state if the implementation needs it.

Secret credential values must never be:

- committed to Git;
- written to logs;
- returned by diagnostics;
- stored in the per-session SQLite database;
- exposed to the browser after successful exchange.

Local deterministic tests must use obviously fake credentials only.

### 2.2 Access exchange and session

A successful invite exchange should create an authenticated Preview session.

Requirements:

- the authenticated session is bound to an `invite_id`;
- session cookies are opaque, HttpOnly, SameSite-protected, and Secure for Preview;
- session expiration is finite and configurable;
- logout invalidates the active session;
- removing/invalidating an invitation must have a documented bounded revocation path;
- session SQLite creation must happen only after successful access authentication;
- quotas are aggregated by invite identity, not merely by browser tab/session.

The existing WP-1/WP-2 per-session SQLite isolation remains in force.

### 2.3 Public vs protected surfaces

Before authentication, only the minimum required surfaces may remain available, such as:

- frontend shell/static assets;
- `/health`;
- the bounded Preview access exchange endpoint.

Conversation, settings, memory, search, usage, Provider/model operations, destructive routes, and other private APIs must require an authenticated Preview session.

Local mode must remain unchanged.

---

## 3. Rate / Concurrency / Cost Boundary

WP-3 must implement **finite, configurable, fail-closed Preview limits**.

Equivalent naming/design is allowed, but the behavior must cover:

### 3.1 Per-invite limits

- finite generation/request rate;
- finite rolling-window or interval quota;
- finite concurrent active generations;
- finite request/input size;
- bounded session lifetime.

### 3.2 Global Preview limits

- finite global generation/request rate;
- finite global concurrent Provider generations;
- a global guard that rejects work before any paid Provider invocation when limits are exhausted.

### 3.3 Provider spend-risk rule

The WP-3 controls are **risk controls, not billing-grade accounting**.

Because Preview state is ephemeral, counters may reset on process restart. This must be documented and must not be described as a hard monetary ceiling.

Before real external access, deployment should additionally use provider/account-side budget/spend controls where available; that future external configuration requires Product Owner authorization.

### 3.4 Output/token boundary

If the existing DeepSeek request interface safely supports a Preview-only maximum output-token setting without changing local behavior, add and test a finite Preview cap.

If that cannot be added safely in WP-3, document the limitation clearly; do not fake support.

---

## 4. Abuse Boundary

WP-3 should include a minimal defense suitable for a handful of invited testers:

- high-entropy invitation credentials;
- no open registration;
- bounded failed-access attempts / access-exchange rate;
- bounded request body/input size;
- 401/403/429 behavior that does not leak secrets;
- no secret values in logs;
- no trust in arbitrary client-supplied identity headers;
- forwarded-client identity may only be used if the existing trusted-proxy contract makes it safe;
- no file upload / backup / import / export exposure;
- docs/OpenAPI remain closed in Preview.

CAPTCHA, persistent identity databases, billing, complex moderation, and enterprise authorization are not required for Preview v1.

---

## 5. Frontend Experience

Preview users need a minimal usable access flow.

Allowed WP-3 frontend work:

- access-code / invite-credential entry screen;
- clear invalid/expired/rate-limited feedback;
- logout control;
- authenticated transition into the existing XiaoG UI.

Do not redesign XiaoG or create a general account-management product.

Invite credentials must not be persisted in localStorage or rendered back after successful access.

---

## 6. Deterministic Validation

All validation remains local and must use fake/local dependencies only.

Required coverage should include:

- local mode still works without Preview auth;
- Preview unauthenticated API access is rejected;
- invalid invite credential is rejected;
- invalid authentication does not create a session database;
- valid fake invite creates an authenticated session;
- cookie security attributes and finite expiry;
- invite identity is bound to the session;
- invite A cannot access invite B's session state;
- quotas aggregate across multiple sessions belonging to the same invite where applicable;
- per-invite rate limit blocks before Provider call;
- global rate limit blocks before Provider call;
- per-invite concurrency limit;
- global concurrency limit;
- deterministic fake streaming releases counters correctly on success/error/cancel;
- logout invalidates access;
- secret/invite credential redaction;
- docs/OpenAPI remain closed;
- DeepSeek remains the only Preview Provider;
- Terra remains disabled in Preview;
- existing WP-2 release smoke still passes;
- core regression suite;
- Python compilation;
- frontend syntax checks;
- `git diff --check`.

No real Provider/API request is authorized.

---

## 7. External Authorization Gate

WP-3 does **not** authorize:

- GitHub login/authentication;
- creating GitHub repository;
- adding Git remote;
- push;
- hosting/cloud project creation;
- DNS/domain changes;
- external secret injection;
- real invite credential distribution to external users;
- public/invited external access;
- paid Provider verification;
- provider-account budget configuration;
- Terra server-side auth/integration;
- container registry publication.

If any implementation step requires one of these, stop and request Product Owner authorization.

---

## 8. Known Non-Blockers / Deferred Work

The following do not block local WP-3 implementation:

- Docker is not installed on the Product Owner machine; WP-2 image build remains pending for the pre-deployment gate.
- The real default-Edge navigation-delay Known Issue remains unresolved and non-blocking.
- Terra remains a separate conditional Provider gate.

---

## 9. Required Handoff

WP-3 completion must produce:

`XiaoG_WEB_PREVIEW_WP3_HANDOFF.md`

The handoff must contain:

- start/final Git provenance;
- WP-3 candidate commit;
- access/auth design;
- invite secret handling and revocation model;
- protected/public surface matrix;
- per-invite/global rate and concurrency controls;
- cost-risk boundary and its limitations;
- frontend access flow;
- deterministic validation evidence;
- exact remaining pre-deployment blockers;
- external Product Owner authorizations required next;
- recommendation for the next decision only.

---

## 10. Stop Gate

When local WP-3 scope is complete:

- update STATUS;
- set `HANDOFF_REQUIRED`;
- output:

`AUTOPILOT_SCOPE_COMPLETE`

`HANDOFF_TO_TECH_LEAD_REQUIRED`

Then stop.

Do not start WP-4, GitHub, hosting, DNS, secret injection, real invite distribution, public access, Terra, Controlled Dual-Codex, Worker, DeepSeek Registry maintenance, Phase 5.5, or Phase 6+.

---

**END — XiaoG Web Preview WP-3 Plan / 2026-09-14**
