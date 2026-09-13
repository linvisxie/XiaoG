# XiaoG Autopilot Status

Protocol Version: v1.4 FINAL
Activation ID: XIAOG-AUTOPILOT-WEB-PREVIEW-READINESS-2026-09-13-V1
Roadmap Version: XiaoG Master Roadmap v2 (2026-09-12) + Limited Public Preview Addendum v1 (2026-09-13)
Roadmap Content Hash: 0f971684cae4eee043c113f3195aed461103139c344b3a272d11237d5d1e96f8
Autopilot State: HANDOFF_REQUIRED
MILESTONE: PHASE_5_STABLE_REACHED
MILESTONE: ENGINEERING_FOUNDATION_ACCEPTED_STABLE
MILESTONE: WP_0_WEB_PREVIEW_READINESS_AUDIT_COMPLETE
Window Start: 2026-09-13 Asia/Shanghai
Window Stop Gate: WP-0 read-only Web Preview Readiness Audit delivered; Tech Lead decision and any external-service authorization are required before later Preview work.
Current Stage: WP-0 Web Preview Readiness Audit / Handoff Required
Current Task: Audit is complete. Stop autonomous progression and transfer the documented decision to Tech Lead.
Current Branch: main
Start Accepted Baseline: Phase 5 / 78130be33c53d2c2b3c68e378ccc96cce9a144d7; Engineering Foundation product baseline / ffdfe3de10c87e50afc3d69017b1deaf7e883029
Last Accepted Stable Baseline: Engineering Foundation / ffdfe3de10c87e50afc3d69017b1deaf7e883029
Current Candidate: none
Last Checkpoint: effb57b66d084ce76bda9cdd198395ab8041a12b (prior Engineering Foundation closure/Handoff)
Working Tree: WP-0 audit/status/governance documents are committed in the final audit documentation commit; no product behavior, schema, or deployment code was changed.
Runtime Identity: Current local development entrypoint remains `main.py` / `backend.main:app`, intentionally loopback `127.0.0.1:8000`; frontend asset identity remains `0.4.3-generation-navigation-r1`.
Tests Completed: WP-0 ran deterministic `run_core_tests.py` 34/34 passed, Python compilation, and frontend Node syntax checks. No real Provider/API, deployment, tunnel, public listener, runtime restart, database content read, database mutation, external account, GitHub, remote, or cloud action occurred.
Tests Pending: No further test is authorized in WP-0. A future approved release track must define its own isolated deployment smoke and release gate.

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
- Exact next action: Tech Lead and Product Owner decide whether Preview v1 may be ephemeral or requires persistent per-user data, and separately decide Terra inclusion. Only then may they issue a new bounded Activation and the necessary point-in-time external-service authorization.