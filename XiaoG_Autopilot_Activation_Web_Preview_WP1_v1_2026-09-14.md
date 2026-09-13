# XiaoG Autopilot Activation — Web Preview WP-1 v1
## Release Baseline + Safe Ephemeral Preview Mode

**Activation ID:** `XIAOG-AUTOPILOT-WEB-PREVIEW-WP1-2026-09-14-V1`  
**Core Protocol Required:** `XiaoG_Autopilot_Core_Protocol_v1.4_FINAL_2026-09-12.md`  
**Roadmap Base:** `XiaoG_Master_Roadmap_v2_2026-09-12`  
**Required Preview Addendum:** `XiaoG_Roadmap_Addendum_Public_Preview_v1_2026-09-13.md`  
**Required Product Decision:** `XiaoG_Public_Preview_Product_Decision_v1_2026-09-14.md`  
**Product Owner:** User  
**Tech Lead / Architect / Reviewer:** ChatGPT  
**Main Codex:** Main XiaoG Codex / Integrator  
**Worker Policy:** No Worker in this window

---

## 1. Purpose

Implement a bounded local **WP-1 release baseline and safe ephemeral Preview mode** suitable for later isolated deployment.

This window may modify local product/config/test/docs code only as necessary for WP-1.

This window does **not** authorize GitHub, hosting, external services, public exposure, real Provider calls, Terra server-side integration, or later product phases.

---

## 2. Start Reality

Expected start facts:

- Branch: `main`
- WP-0 final documentation commit / expected HEAD:
  `818376df2a62eb20b8f0d7f0ad72f195543d0a03`
- Working tree: clean
- Engineering Foundation Accepted Stable product-code baseline:
  `ffdfe3de10c87e50afc3d69017b1deaf7e883029`
- STATUS state: `HANDOFF_REQUIRED`
- Milestone: `WP_0_WEB_PREVIEW_READINESS_AUDIT_COMPLETE`

### Mandatory provenance check

Before modifying anything, inspect and report:

- current branch;
- current HEAD;
- tracked and untracked working tree;
- latest relevant git log;
- latest `XiaoG_AUTOPILOT_STATUS.md`;
- `XiaoG_WEB_PREVIEW_READINESS_AUDIT.md`;
- Preview Addendum and Product Decision;
- current runtime/config/provider/data paths.

If Git reality materially differs, do not mutate Git to make it match this Activation. Stop for Tech Lead review if the discrepancy affects safe execution.

---

## 3. WP-1 Required Outcomes

### 3.1 Explicit runtime mode

Introduce an explicit, testable distinction between:

- normal local XiaoG mode;
- Preview mode.

Preview mode must not activate accidentally in the existing local runtime.

### 3.2 Deployment-safe runtime configuration

Make the minimum bounded changes required so a future Preview runtime can configure, without editing source code:

- bind host / port;
- data directory / database location;
- log location;
- Preview runtime identity / release identity where needed.

Do not silently change the defaults used by the Product Owner's existing local XiaoG.

### 3.3 Safe ephemeral Preview semantics

Preview mode must not reuse Product Owner local persistent data.

"Ephemeral" must not be implemented as one globally shared temporary history/database that lets one Preview user list or mutate another user's temporary conversations/settings.

WP-1 must provide a minimal transient isolation boundary sufficient for Preview v1 without building a full persistent identity platform.

At minimum, Preview mode must prevent cross-preview-user access to temporary Conversation state.

History-bearing/destructive surfaces that cannot be safely isolated in WP-1 must be disabled or unavailable in Preview mode rather than exposed unsafely.

### 3.4 Preview data boundary

Preview mode must never reuse:

- Product Owner's existing `data/xiaog.db`;
- local backup contents;
- local user files;
- local development logs as Preview state.

Any temporary Preview state must use an isolated Preview-owned location or in-memory/transient mechanism.

No destructive migration is allowed.

### 3.5 Provider boundary

Preview v1 primary Provider path is DeepSeek.

Terra must remain unavailable in Preview mode until a later Terra Server-side Readiness / Authentication Audit explicitly authorizes it.

Do not delete or degrade Terra in normal local XiaoG.

If filtering is required, implement a generic deployment/provider allowlist or capability boundary rather than permanent Terra-specific UI hardcoding.

### 3.6 Public-surface policy preparation

WP-1 must define and locally test Preview policy for:

- `/docs`
- `/redoc`
- `/openapi.json`
- diagnostics/admin-like surfaces
- backup/import/export
- file/artifact byte operations
- any endpoint exposing shared local state

Unsafe/unneeded surfaces must default closed/unavailable in Preview mode.

No public listener is authorized in this window.

### 3.7 Release identity and rollback readiness

Establish a local release baseline contract so a future deployment can identify:

- exact Git commit;
- Preview build/release identity;
- runtime mode;
- health/readiness identity.

Document how a future deployment will roll back to the previous immutable revision.

### 3.8 Test/release gate

Gate must include at least:

- existing `run_core_tests.py`;
- Python syntax/compile checks;
- frontend syntax checks;
- Preview mode configuration tests;
- proof normal local defaults remain unchanged;
- proof Preview mode does not reuse Product Owner local DB path;
- cross-preview-session negative tests for transient Conversation state;
- Provider policy test: DeepSeek allowed, Terra unavailable in Preview without breaking local Terra;
- unsafe-surface tests;
- deterministic fake-Provider/SSE smoke where needed.

Do not use a real paid Provider.

The accepted real default-Edge navigation Known Issue remains documented and is not considered fixed by synthetic success.

---

## 4. Allowed Scope

Allowed:

- bounded local source/config/test/docs changes needed for WP-1;
- deterministic local tests;
- test fixtures/fake Providers;
- STATUS updates;
- local Git commits required for clean handoff;
- loopback-only runtime checks using isolated/temp data.

---

## 5. Strictly Forbidden

Do **not**:

- create/login to GitHub;
- create a GitHub repository;
- add a Git remote;
- push;
- create hosting/cloud project;
- create DNS/domain records;
- upload code/data to external services;
- enter Provider/deployment secrets into external services;
- expose XiaoG through tunnel/public port;
- use Product Owner local DB as Preview data;
- copy local user data into Preview fixtures;
- print/copy API keys/tokens/credentials/cookies;
- call real Providers/APIs;
- implement Terra server-side authentication/hosting;
- alter/copy Product Owner browser/profile credentials;
- start Controlled Dual-Codex;
- start a Worker;
- implement DeepSeek Registry maintenance;
- start Phase 5.5 or Phase 6+;
- revive persistent multi-user SaaS architecture;
- claim the default-Edge Known Issue is fixed.

---

## 6. Engineering Constraints

- Safe additive changes only.
- No DB rebuild/destructive migration.
- Existing local behavior is compatibility baseline.
- Preview behavior must be explicitly activated.
- Provider behavior remains Registry/capability/configuration driven.
- No permanent provider-specific UI hardcoding.
- Prefer deterministic local tests.
- Keep logs/secrets redacted.
- Record future deployment concerns rather than broadening WP-1.

---

## 7. Required Deliverables

At completion provide:

1. `XiaoG_WEB_PREVIEW_WP1_HANDOFF.md`
2. updated `XiaoG_AUTOPILOT_STATUS.md`
3. exact branch / HEAD / working-tree before and after
4. all WP-1 commit hashes
5. concise file-change summary
6. deterministic test summary
7. explicit confirmation:
   - local mode preserves accepted semantics;
   - Preview mode is explicit;
   - Preview does not use Product Owner local data;
   - transient Preview users cannot access each other's Conversation state within implemented boundary;
   - DeepSeek is first Preview Provider path;
   - Terra is not enabled for Preview and local Terra was not removed;
   - no external service or real Provider was used.
8. remaining blockers for WP-2
9. recommended next decision, not implementation

---

## 8. Stop Gate

When complete:

- set Autopilot state to `HANDOFF_REQUIRED`;
- stop autonomous progression;
- output:

`AUTOPILOT_SCOPE_COMPLETE`

`HANDOFF_TO_TECH_LEAD_REQUIRED`

Do not continue into WP-2, GitHub, hosting, DNS, external secrets, invited external access, Terra audit/integration, Controlled Dual-Codex, DeepSeek Registry maintenance, Phase 5.5, or Phase 6+.

---

## 9. First Action

Read in order:

1. `XiaoG_Autopilot_Core_Protocol_v1.4_FINAL_2026-09-12.md`
2. `XiaoG_Master_Roadmap_v2_2026-09-12.md`
3. `XiaoG_Roadmap_Addendum_Public_Preview_v1_2026-09-13.md`
4. `XiaoG_Public_Preview_Product_Decision_v1_2026-09-14.md`
5. `XiaoG_WEB_PREVIEW_READINESS_AUDIT.md`
6. latest `XiaoG_AUTOPILOT_STATUS.md`
7. `XiaoG_ENGINEERING_FOUNDATION_HANDOFF.md`
8. this Activation

Then run the mandatory provenance check before modifying any file.

---

**END — XIAOG-AUTOPILOT-WEB-PREVIEW-WP1-2026-09-14-V1**
