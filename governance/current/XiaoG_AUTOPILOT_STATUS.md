# XiaoG Autopilot Status

Protocol Version: v1.4 FINAL
Activation ID: XIAOG-AUTOPILOT-WEB-PREVIEW-WP4-2026-09-14-V1
Roadmap Version: XiaoG Master Roadmap v2 (2026-09-12) + Limited Public Preview Addendum v1 (2026-09-13) + Preview v1 Mode & Terra Gate Product Decision (2026-09-14)
Roadmap Content Hash: 0f971684cae4eee043c113f3195aed461103139c344b3a272d11237d5d1e96f8
Autopilot State: HANDOFF_REQUIRED
MILESTONE: PHASE_5_STABLE_REACHED
MILESTONE: ENGINEERING_FOUNDATION_ACCEPTED_STABLE
MILESTONE: WP_0_WEB_PREVIEW_READINESS_AUDIT_COMPLETE
MILESTONE: WP_1_RELEASE_BASELINE_AND_SAFE_EPHEMERAL_PREVIEW_MODE_COMPLETE
MILESTONE: WP_2_ISOLATED_RUNTIME_DATA_SECRET_BOUNDARY_COMPLETE
MILESTONE: WP_3_INVITED_ACCESS_RATE_COST_ABUSE_BOUNDARY_COMPLETE
MILESTONE: WP_4_LOCAL_CI_RELEASE_DEPLOYMENT_READINESS_COMPLETE
Window Start: 2026-09-14 Asia/Shanghai
Window Stop Gate: WP-4 local CI/release/deployment readiness is complete. Handoff is required before any external CI, deployment, secret, registry, hosting, DNS, or access action.
Current Stage: WP-4 — CI / Test-Gated Automatic Deployment / Handoff Required
Current Task: WP-4 local readiness is complete. WP-3 remains Accepted/Closed; no external WP-4 execution is authorized.
Current Branch: main
Start Accepted Baseline: Phase 5 / 78130be33c53d2c2b3c68e378ccc96cce9a144d7; Engineering Foundation product baseline / ffdfe3de10c87e50afc3d69017b1deaf7e883029
Last Accepted Stable Baseline: WP-3 / 7bd80be7028e521a5d837bdd8f8a2b3c0adcc88b
Current Candidate: WP-4 local readiness / 38455d0cee8c5a572761b5283821dc54f71b6d3e (strict local gate passed; not an external deployment)
Last Checkpoint: 38455d0cee8c5a572761b5283821dc54f71b6d3e (WP-4 local readiness candidate)
Working Tree: clean after final WP-4 governance provenance commit. No external state was changed.
Runtime Identity: Local default remains `main.py` / `backend.main:app` at `127.0.0.1:8000`. Preview is explicitly selected with `XIAOG_RUNTIME_MODE=preview`, an explicit non-local `XIAOG_DATA_DIR`, immutable `XIAOG_RELEASE_ID`, and the DeepSeek-only Preview allowlist. Preview health includes commit, runtime mode, and release identity.
Tests Completed: `./.venv/Scripts/python.exe tools/ci/wp4_release_gate.py --revision HEAD` passed on `38455d0cee8c5a572761b5283821dc54f71b6d3e`: 44/44 core regression, Preview release smoke, explicit 7-test WP-3 access/streaming suite, Python compile, frontend Node syntax, Git diff/revision/clean-tree checks, and secret scan. All use local/fake dependencies; no Provider call occurred.
Tests Pending: local Docker build/container smoke was not run because Docker is unavailable. Any remote CI, registry, deployment, secret injection, real Provider check, or external access remains unauthorized.

## WP-1 Delivery

- Local behavior stays the default and retains the accepted SQLite path, loopback bind, Terra Registry/App Server behavior, and data semantics.
- Preview requires explicit environment configuration and rejects the Product Owner local data directory or an absent release identity.
- Preview creates an opaque HttpOnly session cookie server-side for API callers. Each active Preview session receives its own SQLite file below the configured Preview-owned data directory; no cookie maps to an existing session unless issued by the current process. The session directory is cleared at Preview startup, so state is non-persistent across process starts.
- Request-scoped SQLite routing prevents one Preview session from listing, reading, or mutating another session's Conversation state. Existing local SQLite is not initialized or selected in Preview mode.
- Preview closes `/docs`, `/redoc`, and `/openapi.json`; no backup/import/export or file-byte endpoint exists in the current API.
- Preview Registry policy is generic but WP-1 validates a DeepSeek-only allowlist. Terra is reported unavailable without a Terra health check or App Server startup; normal local Terra behavior remains unchanged.
- Future deployment identity is supplied by `XIAOG_RELEASE_ID`; `/health` reports commit, runtime mode, and release identity. Rollback must select the prior immutable revision and its isolated Preview configuration.

## WP-0 Readiness Conclusion

`XiaoG_WEB_PREVIEW_READINESS_AUDIT.md` records the evidence, risk matrix, bounded topology options, and recommended next decision.

- An isolated one-process FastAPI Preview is portability-feasible in principle, but current runtime is not safe as-is for shared persistent invited users.
- Current SQLite data, Conversations, Settings, Memories, model usage, and artifact metadata lack user/session/tenant ownership; current API has no authentication/authorization or rate/cost-abuse controls.
- An ephemeral/stateless invited Preview is materially safer than persistent shared storage for v1, but still requires an approved future design/release Activation.
- Persistent invited-user Preview is architectural work, not configuration-only deployment.
- Terra requires a separate official server-side Codex App Server operations/authentication decision; it must never reuse Product Owner local browser/profile credentials or local runtime.

## Known Issue — Navigation delay during generation in real default Edge runtime

In the Product Owner's real default Edge environment, while Conversation A is processing, thinking, or generating, navigation to Conversation B, New Chat, or Settings may not switch immediately and may jump after completion.

- Current workaround: wait for the active response generation to finish before navigating.
- No data loss, Conversation/message cross-write, database corruption, security issue, or erroneous generation cancellation was observed.
- Root cause remains unknown. Isolated Edge/mock SSE, pre-first-delta, high-frequency SSE, and local fake-Provider ASGI checks passed, but synthetic success does not dismiss the real issue.

## Governance and Scope Guard

- Public Preview Addendum is approved roadmap scope; full Phase 9 Cloud, commercialization, open registration, desktop/cloud dual runtime, and unrelated product phases remain out of scope.
- No GitHub remote is configured. No GitHub authentication/repository/remote/push, hosting project, DNS, cloud database/storage, external secret, tunnel, or external access was created or authorized.
- DeepSeek Registry maintenance remains backlog only and was not implemented.
- No Worker, Controlled Dual-Codex, Phase 5.5, Phase 6+, or deployment was started.
- Exact next action: Verify the WP-4 candidate provenance, then Tech Lead reviews WP-4 local readiness and decides whether to grant a point-in-time external-action authorization. GitHub authentication/repository/remote/push, hosting, DNS, external secrets, registry publish, invited external access, real Provider, and Terra must not start automatically.
