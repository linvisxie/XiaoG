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
MILESTONE: WP_5A_CONTROLLED_PRIVATE_PREVIEW_VERIFICATION_RECORDED
Window Start: 2026-09-14 Asia/Shanghai
External Authorization: XIAOG-WP4-GITHUB-SOURCE-CONTROL-GATE-2026-09-14-V1 (GitHub private source control and CI only); Product Owner-supplied manual ECS WP-5A private-verification evidence recorded below. No separate WP-5 Activation ID was supplied.
Window Stop Gate: WP-4 readiness and Product Owner-supplied WP-5A controlled private ECS verification are recorded. Handoff is required. The DeepSeek key used during manual troubleshooting must be treated as compromised and rotated before any further Provider use; rotation requires separate authorization.
Current Stage: WP-5A — Controlled Private Preview Verification / Handoff Required
Current Task: Manual ECS Preview verification evidence is recorded for the immutable candidate below. No public exposure, DNS, HTTPS, external invite distribution, or public release occurred. No further activation may start until Tech Lead review and separately authorized key rotation.
Current Branch: main
Start Accepted Baseline: Phase 5 / 78130be33c53d2c2b3c68e378ccc96cce9a144d7; Engineering Foundation product baseline / ffdfe3de10c87e50afc3d69017b1deaf7e883029
Last Accepted Stable Baseline: WP-3 / 7bd80be7028e521a5d837bdd8f8a2b3c0adcc88b
Current Candidate: WP-5A manually private-verified Preview revision / 7814fc0f57af9cd5db677d121b50d32437f81b73.
Last Checkpoint: 7814fc0f57af9cd5db677d121b50d32437f81b73 (container source-revision health fallback; strict local release gate, GitHub CI, and Product Owner-supplied controlled private ECS verification recorded).
Working Tree: clean before this governance-only WP-5A evidence update; no product, runtime, schema, test, deployment configuration, secret, or external action is included here.
Runtime Identity: Local default remains `main.py` / `backend.main:app` at `127.0.0.1:8000`. Preview is explicitly selected with `XIAOG_RUNTIME_MODE=preview`, an explicit non-local `XIAOG_DATA_DIR`, immutable `XIAOG_RELEASE_ID`, and the DeepSeek-only Preview allowlist. Preview health includes commit, runtime mode, and release identity.
Tests Completed: `./.venv/Scripts/python.exe tools/ci/wp4_release_gate.py --revision HEAD` passed on `7814fc0f57af9cd5db677d121b50d32437f81b73`: 47/47 core regression, Preview release smoke, explicit 7-test WP-3 access/streaming suite, Python compile, frontend Node syntax, Git diff/revision/clean-tree checks, and secret scan. GitHub Actions workflow `XiaoG WP-4 release gate` run `34836960055` completed successfully on that exact commit. Product Owner-supplied manual ECS evidence reports localhost-only Preview health, invite/session/conversation verification, DeepSeek routing, and one bounded streaming generation success on the same immutable revision; Terra was not routed.
Tests Pending: no further local source-control/CI test is pending for the verified candidate. Before any further Provider use, the DeepSeek key exposed during manual operator troubleshooting must be treated as compromised and rotated under a separately authorized secret operation. Local Docker remains unavailable; GitHub CI supplied the container build-contract evidence. This governance record does not authorize additional secret operations, Provider calls, public exposure, DNS, HTTPS configuration, or invited external access.

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
- Authorized GitHub source-control/CI actions completed: private repository `linvisxie/XiaoG` at `https://github.com/linvisxie/XiaoG`, remote `origin` at `https://github.com/linvisxie/XiaoG.git`, and non-force `main` pushes. GitHub Actions ran only the repository WP-4 release-gate workflow. Product Owner-supplied evidence records a localhost-only ECS Preview verification in Alibaba Cloud ECS Hong Kong for immutable revision `7814fc0f57af9cd5db677d121b50d32437f81b73`, including one bounded real DeepSeek stream; Terra remained unavailable/not routed. The container uses a read-only bind mount from host `/run/xiaog-preview/app.env` to `/app/.env`; Docker Config.Env no longer contains the Provider key or Preview invite fields. The manual evidence is retained on ECS under `/root/xiaog-evidence/` and must remain access restricted. This record does not authorize further secret operations, Provider calls, public exposure, DNS, HTTPS configuration, or invited external access. No registry publish, cloud database/storage, tunnel, or Terra integration is recorded here.
- DeepSeek Registry maintenance remains backlog only and was not implemented.
- No Worker, Controlled Dual-Codex, Phase 5.5, Phase 6+, public exposure, DNS, HTTPS configuration, external invite distribution, public release, or Terra integration was started by this governance update. One bounded DeepSeek generation is recorded solely as Product Owner-supplied manual verification evidence.
- Exact next action: Tech Lead reviews the WP-5A manual ECS verification and authorizes the minimum necessary compromised-DeepSeek-key rotation, if continued Preview operation is desired. Public exposure, DNS, HTTPS configuration, external invite distribution, additional Provider use, and Terra must not start automatically.
