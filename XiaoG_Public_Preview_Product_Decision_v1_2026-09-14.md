# XiaoG Product Decision Record — Preview v1 Mode & Terra Gate

**Date:** 2026-09-14  
**Document Type:** Product Owner Decision / Tech Lead Roadmap Supplement  
**Applies To:** `XiaoG_Roadmap_Addendum_Public_Preview_v1_2026-09-13.md`  
**Current project state at decision:** WP-0 Web Preview Readiness Audit complete / `HANDOFF_REQUIRED`

---

## 1. Product Owner Decision

Preview v1 will proceed as an:

> **invited, isolated, ephemeral / non-persistent web preview**

Preview v1 will use:

> **DeepSeek as the first supported Preview Provider path.**

Terra is **not removed** from XiaoG and is **not permanently excluded** from Preview v1.

Terra is classified as a:

> **Conditional Preview Provider**

Terra may be added only after a separate bounded **Terra Server-side Readiness / Authentication Audit** confirms an officially supported, secure, operable server-side model for:

- Codex CLI / Codex App Server installation and lifecycle;
- authentication and credential ownership;
- hosting/runtime compatibility;
- long-lived process management;
- concurrency and serialization behavior;
- rate/cost controls;
- safe isolation from Product Owner local browser/profile/runtime credentials;
- operational recovery and observability.

Failure or deferral of the Terra audit **must not block the DeepSeek Preview track**.

---

## 2. Architectural Boundary

Preview v1 remains a distribution / feedback environment. It does not authorize:

- full SaaS conversion;
- open public registration;
- mature account/billing/subscription systems;
- Phase 9 Cloud revival;
- persistent multi-tenant cloud data by default;
- copying the Product Owner's local SQLite database or files to Preview;
- durable tunneling of the Product Owner's local machine;
- G-BRIDGE / Remote Control exposure;
- replacement of the existing local-first runtime.

---

## 3. Ephemeral Safety Requirement

"Ephemeral" does **not** mean one globally shared temporary database that all invited users can inspect.

Before invited external access, one Preview user's transient state must not be readable, listable, mutable, or deletable by another Preview user.

A bounded transient session boundary, isolated temp state, in-memory state, or another Tech Lead-approved mechanism may be used without building a full persistent identity platform.

When Preview mode is off, existing local XiaoG behavior and accepted local data semantics must remain unchanged.

---

## 4. Provider Selection Requirement

Preview Provider availability must remain capability/configuration driven.

Do not permanently hard-code provider-specific UI branches merely to hide Terra.

If a Preview allowlist/capability filter is needed, it must be generic enough that:

- Preview v1 can initially allow DeepSeek;
- Terra can be enabled later after its separate gate;
- future Providers can be added without rewriting permanent UI logic;
- local XiaoG Provider availability remains governed by the normal Registry/capability model.

---

## 5. Sequencing

```text
WP-0 Web Preview Readiness Audit ✅
        ↓
Product Owner Decision:
Ephemeral Preview + DeepSeek-first + Terra conditional ✅
        ↓
WP-1 Release Baseline + Safe Ephemeral Preview Mode
        ↓
Tech Lead Review
        ↓
WP-2 Isolated Runtime / Data / Secret Boundary
        ↓
WP-3 Invited Access + Cost / Abuse Controls
        ↓
WP-4 Test-gated Automatic Deployment
        ↓
Product Owner Preview Experience Gate
```

Terra side gate:

```text
Terra Server-side Readiness / Authentication Audit
        ↓
Tech Lead + Product Owner decision
        ↓
If approved: Terra may join Preview v1
If deferred/not approved: DeepSeek Preview continues
```

---

## 6. Authorization Effect

This decision authorizes issuance of a bounded **WP-1 Activation**.

It does not authorize:

- GitHub login/repository creation/remote/push;
- hosting/cloud project creation;
- DNS/domain changes;
- external secret entry;
- public/invited external exposure;
- real Provider calls;
- Terra server-side integration;
- Controlled Dual-Codex;
- Phase 5.5 or Phase 6+.

---

## 7. Continuity Requirement

Future XiaoG handoffs and the next consolidated Master Roadmap revision must preserve:

> XiaoG Limited Public Preview v1 is approved as an invited, isolated, ephemeral/non-persistent experience track. DeepSeek is the first Preview Provider path. Terra is a conditional Preview Provider and may be added only after a separate server-side readiness/authentication audit. Terra deferral must not block the DeepSeek Preview.

---

**END — Preview v1 Mode & Terra Gate Product Decision / 2026-09-14**
