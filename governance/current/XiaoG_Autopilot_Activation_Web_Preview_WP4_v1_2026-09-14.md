# XiaoG Autopilot Activation — Web Preview WP-4 v1
## CI / Test-Gated Automatic Deployment Readiness

**Activation ID:** `XIAOG-AUTOPILOT-WEB-PREVIEW-WP4-2026-09-14-V1`  
**Issued by:** Tech Lead authorization transmitted by the Product Owner on 2026-09-14  
**Core Protocol Required:** `governance/core/XiaoG_Autopilot_Core_Protocol_v1.4_FINAL_2026-09-12.md`  
**Roadmap Base:** `governance/core/XiaoG_Master_Roadmap_v2_2026-09-12.md`  
**Preview authorities:** Public Preview Addendum v1 and Preview v1 Mode & Terra Gate Product Decision, both in `governance/core/`  
**Worker Policy:** Main Codex only; no Worker or Controlled Dual-Codex.

## Start reality and provenance

Expected start: `main`, `4047fc8d6fe41c09de747720506aa1ec26986673`, clean tree, no remote; accepted Preview product candidate `7bd80be7028e521a5d837bdd8f8a2b3c0adcc88b`. These are expectations only. Git history, working tree, tests, STATUS, and authoritative governance files take precedence. Do not rewrite Git to fit this document.

## Allowed local scope

Build the local readiness layer for a future controlled release flow:

- deterministic CI/release gate definition and local simulation;
- core regression, Preview smoke, Preview access/streaming verification, Python compile, frontend syntax, and Git consistency checks;
- tracked-file secret scan;
- immutable revision/release identity and release-manifest contract;
- container build/artifact, rollback, and Preview health verification contracts;
- bounded local config, docs, tests, and commits.

Local mode must retain its accepted behavior. Preview remains opt-in, invite-only, ephemeral/non-persistent, DeepSeek-only, with Terra disabled and no open registration.

## Forbidden actions

No GitHub authentication/repository/remote/push; no hosting, cloud, registry publish, DNS/domain, real external secret, provider billing change, real invite distribution, public/invited external access, tunnel/public listener, real deployment, real Provider/API, Terra server-side integration, Worker/Controlled Dual-Codex, DeepSeek Registry maintenance, Phase 5.5, or Phase 6+.

## External-action stop rule

When the completed local candidate requires an external account, secret, deployment target, or external access to progress, stop and report the exact action, why a local substitute is insufficient, impact on account/secret/data/cost/security, and the minimum Product Owner authorization. Do not choose a provider or carry out the action.

## Stop gate

When all bounded local WP-4 readiness work is complete, produce the current WP-4 Handoff and update STATUS. Set `HANDOFF_REQUIRED`; do not execute deployment or advance further.

**END — XIAOG-AUTOPILOT-WEB-PREVIEW-WP4-2026-09-14-V1**
