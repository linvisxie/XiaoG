# XiaoG Autopilot Activation — Web Preview WP-3 v1
## Invited Access / Rate / Cost / Abuse Boundary

**Activation ID:** `XIAOG-AUTOPILOT-WEB-PREVIEW-WP3-2026-09-14-V1`  
**Core Protocol Required:** `XiaoG_Autopilot_Core_Protocol_v1.4_FINAL_2026-09-12.md`  
**Roadmap Base:** `XiaoG_Master_Roadmap_v2_2026-09-12.md`  
**Preview Addendum:** `XiaoG_Roadmap_Addendum_Public_Preview_v1_2026-09-13.md`  
**Preview Product Decision:** `XiaoG_Public_Preview_Product_Decision_v1_2026-09-14.md`  
**WP-3 Plan:** `XiaoG_WEB_PREVIEW_WP3_PLAN_2026-09-14.md`  
**Product Owner:** User  
**Tech Lead / Architect / Reviewer:** ChatGPT  
**Main Codex:** Main XiaoG Codex / Integrator  
**Worker Policy:** No Worker in this window

---

## 1. Purpose

Implement the bounded local WP-3 boundary required for a small invited Preview:

- invite-only access;
- authenticated Preview sessions;
- rate limits;
- concurrency limits;
- spend-risk controls;
- minimal abuse protection;
- minimal access UI.

This Activation does not authorize external services or external users.

---

## 2. Start Reality

Expected start facts:

- branch: `main`
- expected HEAD:
  `4d7eb3271b86661108a485c22a3ef321210498bf`
- accepted WP-2 product candidate:
  `da5bb6c27ab3c33b7275eac8e686b16c53e057ad`
- working tree: clean
- no remote
- WP-2 accepted by Tech Lead
- current governance state remains a handoff/start-transition point.

These are expectations only. Git and working-tree evidence outrank this document.

### Mandatory provenance check

Before modification, inspect:

- branch;
- HEAD;
- `git status`;
- recent Git log;
- latest `XiaoG_AUTOPILOT_STATUS.md`;
- `XiaoG_WEB_PREVIEW_WP2_HANDOFF.md`;
- Preview runtime/session/data implementation;
- Preview secret-loading implementation;
- Provider call boundary;
- current frontend/API route surface.

If reality materially differs and cannot be safely reconciled inside this Activation, stop and report.

Do not rewrite Git to match expected values.

---

## 3. Required WP-3 Architecture

### 3.1 Invitation model

Implement a bounded per-invite access model.

Requirements:

- separate high-entropy credential per invite/person;
- non-secret invite identity;
- credentials supplied only by server-side configuration/secret input;
- fake credentials only in committed tests/examples;
- no invitation secret logging;
- no invitation secret persistence in session SQLite;
- no open signup;
- no email/password database;
- no OAuth.

Equivalent secure implementation details are allowed if they preserve these semantics.

### 3.2 Authenticated Preview session

After successful invite exchange:

- bind the Preview session to invite identity;
- issue opaque HttpOnly session cookie;
- Preview cookie must be Secure and SameSite-protected;
- finite configurable expiry;
- logout invalidates the session;
- session DB is not created for failed/unauthenticated access;
- existing per-session SQLite isolation remains intact.

Do not alter accepted local-mode behavior.

### 3.3 Protected route policy

In Preview mode, all private/data/provider APIs must require authenticated Preview access.

Unauthenticated availability must be minimized to the frontend shell/static assets, health, and the bounded access exchange required to sign in.

Keep docs/OpenAPI closed.

### 3.4 Rate and concurrency guards

Implement configurable finite limits with safe defaults for Preview:

- per-invite request/generation rate;
- global request/generation rate;
- per-invite active generation concurrency;
- global active generation concurrency;
- access-exchange / failed-auth attempt rate;
- finite request/input size.

The guard must reject before Provider invocation when exhausted.

Return appropriate bounded 401/403/429 responses without secret leakage.

### 3.5 Cost-risk guard

WP-3 must provide a practical spend-risk boundary, not claim billing-grade accounting.

At minimum:

- generation quotas/rates are finite;
- concurrency is finite;
- Preview Provider set remains DeepSeek-only;
- Preview request/input size is finite;
- if safely supported, add a Preview-only finite maximum output-token cap;
- document that in-memory/ephemeral counters reset on process restart;
- never call a real Provider in WP-3.

### 3.6 Frontend access flow

Add only the minimum UI required for invited use:

- invite credential entry;
- invalid/expired/rate-limited feedback;
- authenticated entry into existing XiaoG;
- logout.

Do not store invite credentials in localStorage.

Do not build general account/profile management.

---

## 4. Allowed Work

Allowed:

- bounded backend/frontend/config/test/docs changes;
- local commits;
- fake invitation fixtures;
- local ASGI/TestClient checks;
- fake Provider streaming tests;
- temporary Preview data;
- STATUS and WP-3 handoff updates.

---

## 5. Strictly Forbidden

Do not:

- authenticate to GitHub;
- create GitHub repository;
- add remote;
- push;
- create hosting/cloud project;
- configure DNS/domain;
- inject real external secrets;
- distribute real invite credentials externally;
- enable public/external access;
- create tunnel/public listener;
- call real Provider/API;
- configure provider billing/spend accounts;
- publish container image;
- implement Terra server-side auth/integration;
- start Terra audit without separate Activation;
- start WP-4;
- start Controlled Dual-Codex or Worker;
- implement DeepSeek Registry maintenance;
- start Phase 5.5/6+;
- change the accepted status of the default-Edge Known Issue without new real evidence.

---

## 6. Validation Requirements

Run and record, as applicable:

- existing core regression suite;
- existing WP-2 release smoke;
- Preview auth tests;
- failed access creates no session DB;
- secure cookie/expiry tests;
- invite/session binding tests;
- cross-invite/session isolation negative tests;
- per-invite rate tests;
- global rate tests;
- per-invite concurrency tests;
- global concurrency tests;
- counter release on stream completion/error/cancel;
- access-attempt throttling;
- request/input size guard;
- secret redaction tests;
- logout tests;
- local mode compatibility;
- DeepSeek-only Preview policy;
- Terra-disabled Preview policy;
- docs/OpenAPI closed;
- Python compilation;
- frontend Node syntax;
- `git diff --check`.

Use fake/local dependencies only.

No real Provider or external service.

---

## 7. External Action Stop Rule

If any task requires external service mutation or a real credential:

**STOP.**

Report:

- the exact action required;
- why local substitutes are insufficient;
- secret/data/cost/security impact;
- minimum Product Owner authorization required.

Do not perform the action before explicit approval.

---

## 8. Required Deliverables

At completion:

1. `XiaoG_WEB_PREVIEW_WP3_HANDOFF.md`
2. updated `XiaoG_AUTOPILOT_STATUS.md`
3. branch / start HEAD / final HEAD
4. WP-3 candidate commit
5. working-tree status
6. file-change summary
7. validation summary
8. access/auth model summary
9. rate/concurrency/cost-risk summary
10. explicit statement that:
   - local mode is unchanged;
   - Preview remains opt-in;
   - unauthenticated Preview access is bounded;
   - invite secrets are server-side/unlogged;
   - session state remains isolated;
   - DeepSeek remains the only Preview Provider;
   - Terra remains disabled;
   - no real Provider/external action occurred.
11. remaining blockers before real invited deployment
12. exact Product Owner authorizations needed next
13. recommended next decision, not implementation

---

## 9. Stop Gate

When WP-3 local scope is complete:

- state: `HANDOFF_REQUIRED`
- output:

`AUTOPILOT_SCOPE_COMPLETE`

`HANDOFF_TO_TECH_LEAD_REQUIRED`

Then stop.

Do not continue to WP-4 or deployment.

---

## 10. First Action

Read in order:

1. `XiaoG_Autopilot_Core_Protocol_v1.4_FINAL_2026-09-12.md`
2. `XiaoG_Master_Roadmap_v2_2026-09-12.md`
3. `XiaoG_Roadmap_Addendum_Public_Preview_v1_2026-09-13.md`
4. `XiaoG_Public_Preview_Product_Decision_v1_2026-09-14.md`
5. `XiaoG_WEB_PREVIEW_WP2_HANDOFF.md`
6. latest `XiaoG_AUTOPILOT_STATUS.md`
7. `XiaoG_WEB_PREVIEW_WP3_PLAN_2026-09-14.md`
8. this Activation

Then perform the Mandatory Provenance Check before changing files.

---

**END — XIAOG-AUTOPILOT-WEB-PREVIEW-WP3-2026-09-14-V1**
