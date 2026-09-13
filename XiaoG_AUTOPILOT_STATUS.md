# XiaoG Autopilot Status

Protocol Version: v1.4 FINAL
Activation ID: XIAOG-AUTOPILOT-PHASE5-2026-09-12-V1
Roadmap Version: XiaoG Master Roadmap v2 (2026-09-12)
Roadmap Content Hash: 0f971684cae4eee043c113f3195aed461103139c344b3a272d11237d5d1e96f8
Autopilot State: WAITING_FOR_PRODUCT_OWNER_EXPERIENCE
Window Start: 2026-09-12 Asia/Shanghai
Window Stop Gate: Engineering Foundation candidate accepted by the Product Owner
Current Stage: Phase 5 / v0.4.2 - Auto Router v1
Current Task: Product Owner experience validation of v0.4.2 Conversation-scoped per-Model Manual reasoning repair.
Current Branch: main
Start Accepted Baseline: v0.4.0 / 7ddab006a618ede56e3d22d55ba2f212d8f47cd0
Last Accepted Stable Baseline: v0.4.1 / b0632f273ddb5310fe59e580bfb06bad067e7026
Current Candidate: v0.4.2 / 36de18f05a5db9a8f3af0fed5df063274881df7a
Last Checkpoint: beacf96 - persisted Manual reasoning as a Conversation plus Model map; legacy scalar compatibility, API resolution, Draft/Header behavior, and regression coverage.
Working Tree: Candidate implementation is committed; expected clean after this status-only commit.
Runtime Identity: XiaoG backend is healthy on 127.0.0.1:8000 as Python listener PID 10380 launched from D:/XiaoG/.venv/Scripts/python.exe main.py; Candidate 36de18f code is active.
Tests Completed: Targeted unittest 10/10 using isolated temporary SQLite, including per-Conversation and per-Model A to B to A restoration, Auto preservation, Conversation isolation, genuine legacy scalar-only row compatibility, and backend chat routing with DeepSeek low while Terra remains high. Python compileall; Node syntax; product JSON; git diff check. Live SQLite safe additive migration loaded without rebuild and PRAGMA integrity_check=ok. Isolated headless Edge regression: Draft Terra low -> DeepSeek max -> DeepSeek low -> Terra high restores each model state with no History row; Settings close/reopen; existing A/B Conversation isolation; Auto hides reasoning and preserves maps; legacy Terra high initializes first DeepSeek to max; hard refresh and XiaoG restart preserve maps. Live provider-status HTTP 200, default-settings HTTP 200, and cache-busted style/app r5 served. Original personalization restored exactly; three exact temporary test Conversations permanently removed through trash then permanent lifecycle; active history returned to 2.
Tests Pending: Product Owner hands-on experience validation only.
Known Issues: none found in the affected v0.4.2 scope.
Blockers: none
Backlog / Future Suggestions: none
Product Owner Gate: Candidate 36de18f is awaiting Product Owner experience validation and is not accepted as Stable. Candidate a31d017 is invalidated by this Product Owner report and remains unaccepted immutable history. Candidate cc6556c is invalidated by the previous Product Owner report and remains unaccepted immutable history. Candidate b6b7178 remains unaccepted immutable history. Do not begin v0.4.3.
Next Allowed Stage: v0.4.2 only
Worker Status: No Worker is active in this Autopilot Window.
Roadmap Delta Suggestion: none
Protocol Delta Suggestion: none
Exact Next Action: Product Owner validates Candidate 36de18f through Draft and existing Conversation Terra/DeepSeek switching, per-model effort restoration, Auto round-trip, legacy Conversation migration behavior, close/reopen, refresh/restart, and Conversation isolation; remain in v0.4.2 until explicit acceptance.