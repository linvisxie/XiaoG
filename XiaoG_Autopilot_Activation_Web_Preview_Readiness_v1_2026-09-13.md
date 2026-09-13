# XiaoG Autopilot Activation — Web Preview Readiness Audit v1

**Activation ID:** `XIAOG-AUTOPILOT-WEB-PREVIEW-READINESS-2026-09-13-V1`  
**Core Protocol Required:** `XiaoG_Autopilot_Core_Protocol_v1.4_FINAL_2026-09-12.md`  
**Roadmap Base:** `XiaoG_Master_Roadmap_v2_2026-09-12`  
**Required Addendum:** `XiaoG_Roadmap_Addendum_Public_Preview_v1_2026-09-13.md`  
**Product Owner:** User  
**Tech Lead / Architect / Reviewer:** ChatGPT  
**Main Codex:** Existing primary XiaoG Codex  
**Worker Policy:** No Worker in this window

---

## 1. Purpose

Perform a bounded **read-only Web Preview Readiness Audit** so Tech Lead can design an isolated invited-user web deployment without guessing from the current local architecture.

This Activation does **not** authorize implementation or deployment.

---

## 2. Start Reality

Last confirmed handoff facts:

- Branch: `main`
- Engineering Foundation Accepted Stable product-code baseline: `ffdfe3de10c87e50afc3d69017b1deaf7e883029`
- Closure / STATUS / Handoff commit and last confirmed HEAD: `effb57b66d084ce76bda9cdd198395ab8041a12b`
- Working tree: clean
- Autopilot previous state: `HANDOFF_REQUIRED`
- Previous scope: `AUTOPILOT_SCOPE_COMPLETE`

These are startup expectations only.

### Mandatory provenance check

Before doing anything else, inspect and report:

- current branch;
- current HEAD;
- working tree, including untracked files;
- latest relevant git log;
- `XiaoG_AUTOPILOT_STATUS.md`;
- `XiaoG_ENGINEERING_FOUNDATION_HANDOFF.md`;
- actual runtime entrypoint/config files.

If Git reality materially differs from the expected start facts, **do not mutate Git to match this Activation**. Record the discrepancy and stop for Tech Lead review if it affects safe audit conclusions.

---

## 3. Allowed Scope

Allowed actions are limited to:

- reading source, configuration, tests, docs, migrations, and runtime scripts;
- inspecting local Git state/history;
- inspecting local dependency manifests;
- running deterministic local tests/checks that do not modify product data;
- inspecting startup behavior on loopback only when safe;
- inspecting how frontend/static assets are served;
- inspecting SQLite paths/schema/migrations without destructive writes;
- inspecting how secrets are referenced, while never printing secret values;
- identifying Windows-specific/local-only assumptions;
- identifying state/session/data ownership relevant to multiple invited preview users;
- producing the audit report described below;
- updating `XiaoG_AUTOPILOT_STATUS.md` only as necessary to reflect this new audit Activation and final handoff state;
- committing audit documentation/status only if the repository governance requires a clean handoff commit.

---

## 4. Strictly Forbidden in This Activation

Do **not**:

- modify product behavior;
- implement deployment code;
- refactor architecture;
- change database schema or migrations;
- rebuild/clear/copy the user's production/local database for preview use;
- expose XiaoG through a tunnel or public port;
- create/login to GitHub;
- create a GitHub repository;
- add a Git remote;
- push anything;
- create any hosting/cloud project;
- create DNS/domain records;
- upload code/data to external services;
- enter secrets into any external service;
- print/copy API keys, tokens, credentials, cookies, or secret values;
- call real Providers/APIs;
- implement DeepSeek Registry maintenance;
- start Controlled Dual-Codex;
- start Phase 5.5 or Phase 6+;
- start any Worker;
- claim the real default-Edge Known Issue is fixed.

---

## 5. Required Audit Questions

Create `XiaoG_WEB_PREVIEW_READINESS_AUDIT.md` and answer, with file/path evidence where possible:

### A. Runtime topology

- What process starts XiaoG?
- Which Python/framework/server components own HTTP and SSE?
- How are frontend assets served?
- Are there background threads/processes or long-lived provider bridges?
- What assumptions exist about `127.0.0.1`, fixed ports, Windows paths, or one local user?

### B. Deployment portability

- Which dependencies are OS-specific?
- Can the current runtime start on a conventional Linux container/VM without redesign?
- If not, list the exact blockers.
- Which filesystem paths need writable persistent storage?

### C. Data ownership

- Where is SQLite located?
- What data is global vs Conversation-scoped vs model-scoped?
- What would happen if two browsers/users used the same deployed backend concurrently?
- Could one user see/modify another user's Conversations/Settings/files under current architecture?
- Is a stateless/ephemeral demo mode safer for Preview v1 than persistent multi-user storage?

### D. Secret/provider boundary

- How are Provider API credentials loaded?
- Which code paths can expose configuration to frontend/API responses/logs?
- What must move to deployment secret storage?
- Confirm secret values were not emitted during the audit.

### E. Streaming/network behavior

- What SSE/streaming/timeouts/concurrency behavior must a host support?
- Are there proxy buffering or long-request requirements?
- Does any provider integration require a local long-lived process that affects hosting choice?

### F. Files/artifacts

- What local filesystem semantics are assumed?
- Which features require persistence beyond SQLite?
- Which current file/artifact capabilities should be disabled or constrained in Preview v1 if isolation is not ready?

### G. Security / abuse / cost

- Minimum access-control boundary for a small invited preview.
- Minimum rate/quota/provider-budget controls.
- Any endpoints unsafe to expose publicly in current form.
- Any debug/admin/local-system surfaces that must remain private.

### H. Release engineering

- What source-control/deployment flow would keep local development isolated from Preview?
- Which existing tests should gate a release?
- What additional deployment smoke test is minimally necessary?
- What rollback mechanism is required?

### I. Architecture options

Propose **2–3 bounded deployment topology options**, ranked by:

- minimum product-code change;
- isolation/safety;
- deployment simplicity;
- persistence suitability;
- streaming compatibility;
- expected maintenance burden;
- suitability for a handful of invited users.

Do not choose or implement a vendor merely from preference. State the runtime requirements so Tech Lead can select the provider after the audit.

---

## 6. Validation Rules

- Prefer deterministic local inspection/tests.
- Do not use real Provider calls.
- Do not modify user data.
- If a check could mutate SQLite or config, use a safe temporary copy only when necessary and explicitly report it; otherwise do not run it.
- Keep logs concise; summarize successful checks and expand failures/evidence only as needed.
- Preserve the Engineering Foundation Known Issue wording: synthetic success does not dismiss the real default-Edge issue.

---

## 7. Required Deliverables

At completion provide:

1. `XiaoG_WEB_PREVIEW_READINESS_AUDIT.md`
2. exact branch / HEAD / working-tree state before and after
3. any audit/status documentation commit hash, if created
4. a concise risk matrix:
   - safe as-is
   - requires configuration only
   - requires small code change
   - requires architectural work
   - must remain unavailable in Preview v1
5. recommended next **decision**, not implementation

---

## 8. Stop Gate

When the audit deliverables are complete:

- set state to `HANDOFF_REQUIRED`;
- output `AUTOPILOT_SCOPE_COMPLETE`;
- output `HANDOFF_TO_TECH_LEAD_REQUIRED`;
- stop.

Do not continue into GitHub, hosting, deployment, code changes, Dual-Codex, DeepSeek maintenance, Phase 5.5, or any later phase.

---

## 9. First Action

Read, in order:

1. `XiaoG_Autopilot_Core_Protocol_v1.4_FINAL_2026-09-12.md`
2. `XiaoG_Master_Roadmap_v2_2026-09-12.md`
3. `XiaoG_Roadmap_Addendum_Public_Preview_v1_2026-09-13.md`
4. `XiaoG_AUTOPILOT_STATUS.md`
5. `XiaoG_ENGINEERING_FOUNDATION_HANDOFF.md`
6. this Activation

Then perform the mandatory provenance check before any audit work.

---

**END — XIAOG-AUTOPILOT-WEB-PREVIEW-READINESS-2026-09-13-V1**
