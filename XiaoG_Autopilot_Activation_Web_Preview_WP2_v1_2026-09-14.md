# XiaoG Autopilot Activation — Web Preview WP-2 v1
## Isolated Runtime / Data / Secret Boundary

**Activation ID:** `XIAOG-AUTOPILOT-WEB-PREVIEW-WP2-2026-09-14-V1`  
**Core Protocol Required:** `XiaoG_Autopilot_Core_Protocol_v1.4_FINAL_2026-09-12.md`  
**Roadmap Base:** `XiaoG_Master_Roadmap_v2_2026-09-12`  
**Required Preview Addendum:** `XiaoG_Roadmap_Addendum_Public_Preview_v1_2026-09-13.md`  
**Required Product Decision:** `XiaoG_Public_Preview_Product_Decision_v1_2026-09-14.md`  
**Required WP-2 Plan:** `XiaoG_WEB_PREVIEW_WP2_PLAN_2026-09-14.md`  
**Product Owner:** User  
**Tech Lead / Architect / Reviewer:** ChatGPT  
**Main Codex:** Main XiaoG Codex / Integrator  
**Worker Policy:** No Worker in this window

---

## 1. Purpose

Implement the bounded local **WP-2 isolated runtime/data/secret boundary** needed before any real external deployment.

This Activation authorizes local code/config/test/docs work only.

It does not authorize external account/service mutations or public exposure.

---

## 2. Start Reality

Expected startup facts:

- Branch: `main`
- WP-1 final HEAD expected:
  `31bd46ba8335d3893e6cd7d0ae1f924948a5618e`
- WP-1 candidate:
  `12a3ed352b0af3db1f611babcb1d295fd0982114`
- Working tree: clean
- No Git remote
- STATUS: `HANDOFF_REQUIRED`
- Milestone:
  `WP_1_RELEASE_BASELINE_AND_SAFE_EPHEMERAL_PREVIEW_MODE_COMPLETE`

### Mandatory provenance check

Before modifying anything, inspect:

- current branch;
- current HEAD;
- tracked/untracked working tree;
- latest relevant Git log;
- latest `XiaoG_AUTOPILOT_STATUS.md`;
- `XiaoG_WEB_PREVIEW_WP1_HANDOFF.md`;
- current Preview runtime/config/data/session implementation;
- provider and secret-loading paths.

If Git reality differs materially, do not mutate Git to match this Activation. Stop if safe scope cannot be confirmed.

---

## 3. Allowed WP-2 Implementation Scope

### A. Runtime portability

Allowed to implement:

- Linux/container-compatible Preview startup contract;
- environment-driven bind host/port;
- isolated Preview-owned data/log paths;
- release identity and health identity;
- safe startup validation;
- deterministic shutdown behavior.

### B. Container/release files

Allowed to add bounded local release artifacts such as:

- Dockerfile;
- `.dockerignore`;
- release/runtime environment example;
- local container startup script/config;
- documentation.

Do not publish images or push to any registry.

### C. Secret interface

Allowed to implement/test:

- environment-based server-side secret contract;
- placeholder examples;
- missing-secret validation;
- redaction tests;
- non-exposure to frontend/API.

Do not enter or copy any real secret into test fixtures, Git, logs, or external services.

### D. Data boundary

Allowed to strengthen Preview-owned transient storage/session isolation if needed.

Must preserve:

- no Product Owner local DB reuse;
- no local backup import;
- no destructive migration;
- local mode compatibility.

### E. Reverse proxy/SSE contract

Allowed to add local deterministic proxy/container tests or docs that validate:

- SSE no-buffer behavior;
- long-response compatibility;
- forwarded header expectations;
- health route;
- same-origin contract.

Do not create a real public reverse proxy or DNS record.

### F. Release and rollback

Allowed to define/test:

- immutable revision identity;
- local build artifact contract;
- rollback selection contract;
- release metadata.

### G. Deployment smoke

Allowed to create deterministic local smoke tests using:

- fake Provider;
- local loopback;
- local container/proxy if available;
- temporary Preview data only.

No real Provider/API call.

---

## 4. Strictly Forbidden

Do not:

- login/authenticate to GitHub;
- create GitHub repo;
- add Git remote;
- push;
- create hosting/cloud resources;
- create cloud database/storage;
- create DNS/domain;
- enter real external secrets;
- expose XiaoG publicly;
- create tunnel/public listener;
- call real Provider/API;
- deploy to any external host;
- publish container images;
- implement Terra server-side authentication/hosting;
- start Terra audit unless separately activated;
- start WP-3/WP-4;
- start Controlled Dual-Codex/Worker;
- implement DeepSeek Registry maintenance;
- start Phase 5.5/6+;
- claim the default-Edge Known Issue is fixed.

---

## 5. Validation

Required local validation should include, as applicable:

- `run_core_tests.py`;
- Python compile checks;
- frontend syntax checks;
- `git diff --check`;
- local defaults unchanged;
- explicit Preview config remains opt-in;
- Preview-owned data/log paths;
- no Product Owner DB reuse;
- session isolation regression;
- secret redaction/non-exposure;
- missing-secret behavior;
- DeepSeek Preview policy unchanged;
- Terra Preview policy unchanged;
- docs/OpenAPI remain closed in Preview;
- container/release startup validation;
- deterministic local deployment smoke;
- health/release identity;
- rollback metadata contract.

Keep logs concise and never print secret values.

---

## 6. External Action Stop Rule

If successful completion of a WP-2 task would require any external action such as GitHub, hosting, DNS, cloud storage, secret entry, public exposure, or paid Provider call:

**STOP.**

Report exactly:

- what external action is required;
- why it is required;
- what data/secret/cost/security impact it has;
- whether a local substitute has already been exhausted;
- the minimal Product Owner authorization needed.

Do not perform the action until explicitly authorized.

---

## 7. Required Deliverables

At completion provide:

1. `XiaoG_WEB_PREVIEW_WP2_HANDOFF.md`
2. updated `XiaoG_AUTOPILOT_STATUS.md`
3. start/final branch, HEAD, working tree
4. WP-2 commit hashes
5. file-change summary
6. validation summary
7. explicit confirmation:
   - local XiaoG remains compatible;
   - Preview remains explicit opt-in;
   - Preview runtime/data/log paths are isolated;
   - Preview secret values remain server-side and unexposed;
   - deployment/release contract is reproducible locally;
   - no external action occurred;
   - no real Provider was called;
   - Terra remains conditional and disabled in Preview.
8. remaining blockers for WP-3/external deployment
9. exact Product Owner authorizations required next
10. recommended next decision, not implementation

---

## 8. Stop Gate

When WP-2 local scope is complete:

- set state to `HANDOFF_REQUIRED`;
- output:

`AUTOPILOT_SCOPE_COMPLETE`

`HANDOFF_TO_TECH_LEAD_REQUIRED`

Stop.

Do not continue into WP-3, WP-4, hosting, GitHub, DNS, secrets, public access, Terra, Dual-Codex, DeepSeek Registry maintenance, Phase 5.5, or Phase 6+.

---

## 9. First Action

Read in order:

1. `XiaoG_Autopilot_Core_Protocol_v1.4_FINAL_2026-09-12.md`
2. `XiaoG_Master_Roadmap_v2_2026-09-12.md`
3. `XiaoG_Roadmap_Addendum_Public_Preview_v1_2026-09-13.md`
4. `XiaoG_Public_Preview_Product_Decision_v1_2026-09-14.md`
5. `XiaoG_WEB_PREVIEW_WP1_HANDOFF.md`
6. latest `XiaoG_AUTOPILOT_STATUS.md`
7. `XiaoG_WEB_PREVIEW_WP2_PLAN_2026-09-14.md`
8. this Activation

Then run the Mandatory Provenance Check before modifying anything.

---

**END — XIAOG-AUTOPILOT-WEB-PREVIEW-WP2-2026-09-14-V1**
