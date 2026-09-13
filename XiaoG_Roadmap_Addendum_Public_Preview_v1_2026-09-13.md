# XiaoG Roadmap Addendum — Limited Public Preview v1

**Date:** 2026-09-13  
**Document Type:** Tech Lead Roadmap Addendum / Product Owner Decision Record  
**Applies To:** `XiaoG_Master_Roadmap_v2_2026-09-12`  
**Roadmap SHA-256:** `0f971684cae4eee043c113f3195aed461103139c344b3a272d11237d5d1e96f8`  
**Current accepted product-code baseline:** `ffdfe3de10c87e50afc3d69017b1deaf7e883029`  
**Current closure / STATUS / Handoff commit:** `effb57b66d084ce76bda9cdd198395ab8041a12b`

---

## 1. Product Owner Decision

Product Owner has explicitly re-opened a **limited Web Preview / invited-user deployment** goal.

The approved product intent is:

> Allow other users to open a web URL and experience/use the currently accepted XiaoG product, while their usage does not interfere with the Product Owner's local development environment; future approved releases should be able to propagate to the preview website through a controlled automated deployment path.

This decision supersedes the Roadmap v2 statement that Web publishing should remain entirely removed **only to the extent required for this limited Preview track**.

It does **not** restore the previously removed full `Public Cloud Web / Phase 9 Cloud / Multi-user / Commercialization / Dual Runtime` route.

---

## 2. Status Classification

This item is now an **APPROVED ROADMAP REQUIREMENT**.

It is not a candidate idea and must not be dropped from future handoffs or the next consolidated Master Roadmap revision.

Working name:

**XiaoG Limited Public Preview / Web Preview v1**

---

## 3. Scope Boundary

### In scope

- A separately deployed XiaoG Preview reachable through a web URL.
- Preview runtime isolated from the Product Owner's local development runtime.
- Preview data isolated from the Product Owner's local development database and files.
- Provider credentials kept server-side and never exposed to browser clients.
- A controlled release path from source control to Preview.
- Automated deployment after an explicitly releasable revision passes the required tests/gates.
- Small-scale invited-user access suitable for product experience feedback.
- Basic abuse/cost controls appropriate to a preview environment.
- A staging/preview-to-production promotion path if the selected hosting topology supports it without disproportionate complexity.

### Not automatically in scope

- Open public registration.
- Full account system / mature identity platform.
- Commercialization, subscriptions, billing, payment, monetization.
- Production-grade multi-tenant SaaS architecture.
- Phase 9 Cloud revival.
- Cloud-first replacement of XiaoG's local-first product architecture.
- Desktop packaging / EXE.
- Remote Control or G-BRIDGE cloud exposure.
- Any unrelated Phase 5.5 / Phase 6+ feature work.

Any of the above requires a later explicit Product Owner + Tech Lead decision.

---

## 4. Permanent Preview Requirements

The Preview design must satisfy all of the following unless Product Owner explicitly changes them later:

1. **Development isolation**  
   Preview users must not operate against the Product Owner's local development process, local working tree, development database, or local runtime state.

2. **Release isolation**  
   Local edits must not instantly leak into the user-facing Preview. Only an explicitly releasable revision may deploy.

3. **Controlled automatic updates**  
   After the release gate is satisfied, deployment may be automated so the web Preview updates without manual file copying.

4. **Data isolation**  
   The Preview must not reuse the Product Owner's existing local XiaoG SQLite/database contents. User/session data isolation must be designed before invited-user persistence is enabled.

5. **Secret isolation**  
   Provider API keys/tokens must remain in server-side secret/configuration storage and must never be shipped in frontend assets, repository history, logs, or client-visible responses.

6. **Cost / abuse boundary**  
   Preview access requires a bounded usage policy such as invite control, rate limiting, request quotas, provider-budget limits, or equivalent controls appropriate to the chosen topology.

7. **No direct-local-tunnel as the durable architecture**  
   A tunnel to the Product Owner's development machine may be used only for an explicitly authorized short diagnostic/demo, never as the durable Preview deployment model.

8. **Regression gate before release**  
   The deterministic local test suite remains the first release gate. Synthetic tests must not be mislabeled as coverage of the unresolved real-default-Edge Known Issue.

9. **Known Issue continuity**  
   The accepted non-blocking generation-time navigation delay in the real default Edge runtime remains documented until evidence justifies changing its status.

10. **Local-first product direction remains intact**  
    The Preview is a distribution/experience track, not an automatic conversion of XiaoG into a cloud-only product.

---

## 5. Placement in the Roadmap

Current completed state:

```text
Phase 5 Accepted Stable
        ↓
Engineering Foundation Accepted Stable
        ↓
HANDOFF_TO_TECH_LEAD_REQUIRED / Autopilot scope complete
```

New approved transition track:

```text
Tech Lead takeover
        ↓
WP-0  Web Preview Readiness Audit (read-only / no product-code change)
        ↓
Tech Lead architecture decision + Product Owner external-service authorization gate
        ↓
WP-1  Source-control / release baseline suitable for deployment
        ↓
WP-2  Isolated Preview runtime + data/secret boundary
        ↓
WP-3  Invited-user access + cost/abuse boundary
        ↓
WP-4  CI/test-gated automatic deployment
        ↓
Product Owner Preview Experience Gate
```

This Preview track is inserted **before the project proceeds into new product-feature phases that would otherwise make deployment divergence harder to control**.

The existing requirement to design the controlled GitHub collaboration model and 16GB Controlled Dual-Codex setup remains valid. Their exact sequencing relative to WP-1/WP-2 is a Tech Lead decision after WP-0 evidence is reviewed.

Phase 5.5 and Phase 6+ remain unauthorized until a later explicit Activation.

---

## 6. WP-0 — Mandatory First Step

Before choosing a hosting provider or changing product code, Main Codex must perform a bounded, read-only **Web Preview Readiness Audit**.

The audit must determine at minimum:

- actual server/framework/entrypoint topology;
- frontend asset serving model;
- SSE/streaming requirements;
- SQLite/database paths, migrations, persistence assumptions;
- local filesystem dependencies;
- Windows-specific assumptions;
- hard-coded loopback/port/path assumptions;
- Provider credential ownership and secret-loading path;
- Conversation/session/state ownership relevant to multiple preview users;
- background process/thread dependencies;
- runtime startup/shutdown expectations;
- static/media/file lifecycle requirements;
- whether a stateless/ephemeral demo mode is materially safer than persistent multi-user preview for v1;
- minimum code/config changes required for isolated deployment;
- hosting capability requirements;
- security, privacy, cost, concurrency, and rollback risks;
- recommended deployment topology options with trade-offs.

WP-0 may inspect and run local deterministic checks but must not deploy, create external accounts/repos, add a Git remote, expose secrets, call real Providers, or modify product behavior.

---

## 7. External-Service Authorization Gate

The following remain consequential external actions and require explicit Product Owner authorization at the point they are needed:

- GitHub login/authentication;
- private repository creation;
- adding/pushing a remote;
- creating a hosting/deployment project;
- adding a domain/DNS record;
- creating cloud database/storage resources;
- entering Provider or deployment secrets into an external service;
- enabling public/invited external access.

Approval of this Addendum authorizes the **planning and audit track**, not blanket authorization for every external account mutation.

---

## 8. Relationship to Removed Roadmap Routes

Roadmap v2 removed Public Cloud Web and Phase 9 because Product Owner did not want those routes at that time and explicitly required a fresh architecture assessment if they were ever re-proposed.

That re-proposal has now occurred, but the decision is intentionally narrow:

- **Restored:** Limited Public Preview / invited-user Web deployment track.
- **Still removed:** full Cloud Runtime route, Phase 9 multi-user/commercialization, general SaaS conversion, desktop/cloud dual-runtime architecture.

Future consolidated Master Roadmap versions must preserve this distinction.

---

## 9. Handoff / Memory Requirement

Future XiaoG handoffs must include this as an **approved, not-yet-fully-implemented requirement** until the Preview track is completed or Product Owner explicitly cancels it.

Minimum handoff wording:

> `XiaoG Limited Public Preview` is approved. Goal: isolated web-accessible invited-user experience with test-gated automatic deployment, without coupling preview users to the Product Owner's local development runtime. Full Phase 9 Cloud / commercialization remains out of scope.

---

**END — XiaoG Roadmap Addendum: Limited Public Preview v1 / 2026-09-13**
