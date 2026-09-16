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
MILESTONE: WP_5B_EXTERNAL_PREVIEW_GATEWAY_LOCAL_PREPARATION_COMPLETE
MILESTONE: WP_5B_DEPLOYMENT_ACTIVATION_DOCUMENTATION_COMPLETE
Window Start: 2026-09-14 Asia/Shanghai
External Authorization: XIAOG-WP4-GITHUB-SOURCE-CONTROL-GATE-2026-09-14-V1 (GitHub private source control and CI only); Product Owner WP-5B External Preview Access engineering task (local code/config/test/docs preparation only). No separate WP-5B Activation ID was supplied.
Window Stop Gate: WP-5B local external-gateway preparation and deployment-activation execution package are complete. Handoff is required before any ECS change, Nginx installation/reload, public IP/EIP, security-group change, DNS, certificate, secret rotation, Provider use, external invite distribution, or public access.
Current Stage: WP-5B — External Preview Gateway Preparation / Handoff Required
Current Task: The loopback-preserving Nginx HTTPS gateway template, no-secret deployment automation, rollback plan, deterministic contract tests, final operator runbook, and READY/BLOCKED/NEEDS HUMAN ACTION checklist are complete. No external gateway was installed or exposed. The DeepSeek key used during manual troubleshooting remains compromised and must be rotated before any further Provider use.
Current Branch: main
Start Accepted Baseline: Phase 5 / 78130be33c53d2c2b3c68e378ccc96cce9a144d7; Engineering Foundation product baseline / ffdfe3de10c87e50afc3d69017b1deaf7e883029
Last Accepted Stable Baseline: WP-3 / 7bd80be7028e521a5d837bdd8f8a2b3c0adcc88b
Current Candidate: WP-5B deployment-activation package / 0b2314577b767df35ba638fd3eb15b8663161c41; the already deployed immutable XiaoG image remains 7814fc0f57af9cd5db677d121b50d32437f81b73.
Last Checkpoint: 0b2314577b767df35ba638fd3eb15b8663161c41 (final ECS activation runbook, first-site rollback path, and gateway-contract test update; strict local release gate passed).
Working Tree: clean before this governance-only WP-5B deployment-activation documentation update; no ECS, Nginx runtime, DNS, certificate, security-group, secret, or external action is included here.
Runtime Identity: Local default remains `main.py` / `backend.main:app` at `127.0.0.1:8000`. Preview is explicitly selected with `XIAOG_RUNTIME_MODE=preview`, an explicit non-local `XIAOG_DATA_DIR`, immutable `XIAOG_RELEASE_ID`, and the DeepSeek-only Preview allowlist. Preview health includes commit, runtime mode, and release identity.
Tests Completed: `./.venv/Scripts/python.exe tools/ci/wp4_release_gate.py --revision HEAD` passed on `0b2314577b767df35ba638fd3eb15b8663161c41`: 50/50 core regression, Preview release smoke, explicit 7-test WP-3 access/streaming suite, Python compile, frontend Node syntax, Git diff/revision/clean-tree checks, secret scan, and three WP-5B static gateway-contract tests. Product Owner-supplied manual ECS evidence reports localhost-only Preview health, invite/session/conversation verification, DeepSeek routing, and one bounded streaming generation success on deployed revision `7814fc0f57af9cd5db677d121b50d32437f81b73`; Terra was not routed.
Tests Pending: the Nginx template was not run through `nginx -t` because Nginx is unavailable locally; shell-script syntax was not executed because a Bash runtime is unavailable locally. Both are explicit ECS operator gates. Before any further Provider use, the DeepSeek key exposed during manual operator troubleshooting must be rotated under a separately authorized secret operation. This governance record does not authorize ECS changes, secret operations, Provider calls, public exposure, DNS, HTTPS configuration, or external invites.

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
- Authorized GitHub source-control/CI actions completed: private repository `linvisxie/XiaoG` at `https://github.com/linvisxie/XiaoG`, remote `origin` at `https://github.com/linvisxie/XiaoG.git`, and non-force `main` pushes. GitHub Actions ran only the repository WP-4 release-gate workflow. Product Owner-supplied evidence records a localhost-only ECS Preview verification in Alibaba Cloud ECS Hong Kong for immutable revision `7814fc0f57af9cd5db677d121b50d32437f81b73`, including one bounded real DeepSeek stream; Terra remained unavailable/not routed. The container uses a read-only bind mount from host `/run/xiaog-preview/app.env` to `/app/.env`; Docker Config.Env no longer contains the Provider key or Preview invite fields. The manual evidence is retained on ECS under `/root/xiaog-evidence/` and must remain access restricted. WP-5B local preparation adds a loopback-only Nginx HTTPS gateway template and no-secret automation, but no gateway was installed and no network, DNS, certificate, security-group, secret, or external-access change occurred. No registry publish, cloud database/storage, tunnel, or Terra integration is recorded here.
- DeepSeek Registry maintenance remains backlog only and was not implemented.
- No Worker, Controlled Dual-Codex, Phase 5.5, Phase 6+, public exposure, DNS, HTTPS configuration, external invite distribution, public release, or Terra integration was started by this governance update. One bounded DeepSeek generation is recorded solely as Product Owner-supplied manual verification evidence.
- Exact next action: Tech Lead reviews the WP-5B Handoff and, if external Preview is desired, issues the minimum point-in-time authorization for compromised-key rotation, named ECS/Nginx operator actions, controlled domain/certificate, security-group rules, and a minimal revocable invite set. Public access, DNS, HTTPS configuration, external invites, additional Provider use, and Terra must not start automatically.
