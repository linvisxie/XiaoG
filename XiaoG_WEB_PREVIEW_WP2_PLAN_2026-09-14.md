# XiaoG Web Preview WP-2 Plan — Isolated Runtime / Data / Secret Boundary

**Date:** 2026-09-14  
**Document Type:** Tech Lead Engineering Plan / Preview Track Continuation  
**Applies To:** XiaoG Limited Public Preview v1  
**Current approved state:** WP-0 complete; WP-1 complete and Tech Lead accepted; current Autopilot state `HANDOFF_REQUIRED`

---

## 1. WP-2 Goal

WP-2 establishes the **isolated deployable runtime boundary** required before any real hosting, external secret entry, DNS, public access, or invited-user launch.

WP-2 is still primarily a **local engineering and deployment-contract phase**.

The goal is to ensure that a future Preview deployment can be created from an immutable revision without touching the Product Owner's local runtime, local SQLite, local files, local secrets, or local development process.

---

## 2. Product Boundary

Preview v1 remains:

- invited;
- isolated;
- ephemeral / non-persistent;
- DeepSeek-first;
- Terra conditional and not enabled in Preview until its separate future audit.

WP-2 must not expand XiaoG into persistent multi-user SaaS, open registration, billing, commercialization, Phase 9 Cloud, or general cloud-first architecture.

---

## 3. Required WP-2 Outcomes

### 3.1 Isolated Runtime Contract

Define and implement the minimum release/runtime contract for a future Preview instance:

- explicit Preview runtime mode;
- configurable bind host and port;
- configurable Preview-owned data directory;
- configurable Preview-owned log directory;
- immutable release identity;
- deterministic health/readiness identity;
- startup validation that refuses unsafe local paths or missing Preview requirements.

Local XiaoG defaults must remain unchanged.

### 3.2 Linux / Container Release Contract

Provide a reproducible conventional Linux/container startup path for the DeepSeek Preview runtime.

The contract must define:

- Python/runtime version expectations;
- dependency installation;
- startup command;
- required environment variables;
- writable paths;
- non-root preference where practical;
- process shutdown behavior;
- health check;
- SSE compatibility requirements.

This may include bounded local Docker/container/release files if Main Codex can validate them locally without external services.

### 3.3 Data Isolation Contract

Preview runtime must use only Preview-owned transient state.

It must never:

- initialize or select Product Owner local `data/xiaog.db`;
- read local backups;
- reuse local logs as Preview state;
- import local Conversations / Settings / Memory / files.

Session-isolated transient SQLite created in WP-1 remains the base model unless a safer bounded refinement is required.

### 3.4 Secret Contract

Define a minimal server-side secret interface for Preview.

At minimum:

- Preview Provider secrets come from server-side environment/secret injection;
- secret values must never be rendered to browser clients;
- secret values must never be committed to Git;
- diagnostics/logging must remain redacted;
- `.env.example` / deployment examples must contain placeholders only;
- startup must clearly distinguish “secret missing” from “secret invalid” without printing secret values.

WP-2 may define and locally test the interface.

WP-2 must **not** enter any real secret into an external service.

### 3.5 Reverse Proxy / HTTPS / SSE Contract

Document and test the host requirements for a future edge/proxy:

- HTTPS termination;
- same-origin frontend/API routing;
- SSE pass-through;
- buffering disabled;
- long-lived response compatibility;
- request/idle timeout requirements;
- forwarded headers policy;
- health/readiness route behavior;
- request-body limits;
- no WebSocket requirement unless architecture changes.

WP-2 does not create DNS or a real public proxy.

### 3.6 Release Artifact and Rollback Contract

Define how one immutable XiaoG Preview revision becomes a deployable artifact.

The contract must include:

- commit identity;
- release identity;
- build/release artifact identity;
- startup configuration;
- release gate;
- rollback to previous immutable revision;
- compatibility with ephemeral data semantics.

Do not depend on a specific hosting vendor unless later authorized.

### 3.7 Deployment Smoke Contract

Implement a deterministic local deployment-smoke path using fake/local dependencies only.

The smoke should cover at minimum:

- Preview startup from release contract;
- `GET /`;
- static assets;
- `/health`;
- Preview mode/release identity;
- closed `/docs`, `/redoc`, `/openapi.json`;
- isolated Preview session creation;
- deterministic fake-Provider SSE streaming through the intended local proxy/container path if practical;
- no Product Owner local database access.

No paid or real Provider call is needed.

### 3.8 Security Boundary

WP-2 must identify the exact remaining public-exposure blockers after the isolated runtime contract is complete.

At minimum, it must separate:

- runtime/data/secret readiness (WP-2);
- invited access/auth boundary (WP-3);
- rate/cost/abuse boundary (WP-3);
- real hosting/deployment actions (later explicit authorization);
- Terra server-side readiness (separate gate).

---

## 4. External Authorization Gate

The following are **not authorized by this plan alone** and require Product Owner point-in-time approval before execution:

- GitHub login/authentication;
- GitHub repository creation;
- adding a Git remote;
- pushing code;
- creating a hosting/cloud project;
- creating cloud storage/database resources;
- entering Provider/deployment secrets into any external service;
- creating DNS/domain records;
- enabling external/public/invited access;
- purchasing paid hosting/domain resources;
- any real Provider/API call for deployment verification;
- Terra server-side integration/authentication.

If WP-2 reaches one of these actions, stop and request Product Owner authorization.

---

## 5. Still Forbidden

WP-2 must not:

- begin WP-3 or WP-4;
- start Controlled Dual-Codex;
- start Workers;
- implement DeepSeek Registry maintenance;
- start Phase 5.5 or Phase 6+;
- revive persistent multi-user architecture;
- expose G-BRIDGE / Remote Control;
- alter the accepted default-Edge Known Issue status without new evidence.

---

## 6. Required Handoff

WP-2 completion must produce:

`XiaoG_WEB_PREVIEW_WP2_HANDOFF.md`

The handoff must include:

- start and final Git provenance;
- exact code/config/test changes;
- runtime/container/release contract;
- data isolation contract;
- secret contract;
- proxy/SSE contract;
- deployment smoke evidence;
- release/rollback contract;
- remaining WP-3 blockers;
- any external actions that now require Product Owner authorization;
- recommended next decision, not implementation.

---

## 7. Stop Gate

When WP-2 local scope is complete:

- set `HANDOFF_REQUIRED`;
- output `AUTOPILOT_SCOPE_COMPLETE`;
- output `HANDOFF_TO_TECH_LEAD_REQUIRED`;
- stop.

Do not start external hosting or WP-3 automatically.

---

**END — XiaoG Web Preview WP-2 Plan / 2026-09-14**
