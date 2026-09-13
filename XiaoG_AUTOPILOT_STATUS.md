# XiaoG Autopilot Status

Protocol Version: v1.4 FINAL
Activation ID: XIAOG-AUTOPILOT-PHASE5-2026-09-12-V1
Roadmap Version: XiaoG Master Roadmap v2 (2026-09-12)
Roadmap Content Hash: 0f971684cae4eee043c113f3195aed461103139c344b3a272d11237d5d1e96f8
Autopilot State: RUNNING
MILESTONE: PHASE_5_STABLE_REACHED
Window Start: 2026-09-12 Asia/Shanghai
Window Stop Gate: Engineering Foundation candidate accepted by the Product Owner
Current Stage: Engineering Foundation Gate / Batch B in progress (10.6 and 10.7 complete)
Current Task: Batch B local Permission Abstraction and Unified Search Service Continuation are complete; File / Artifact Lifecycle (10.8) is the next authorized item.
Current Branch: main
Start Accepted Baseline: v0.4.0 / 7ddab006a618ede56e3d22d55ba2f212d8f47cd0
Last Accepted Stable Baseline: Phase 5 / 78130be33c53d2c2b3c68e378ccc96cce9a144d7
Current Candidate: none; Engineering Foundation Batch B is in progress and is not ready for a Candidate.
Last Checkpoint: 4339f7157f289c5d5c5e954d5f21b372771bec9c - Batch A Reliability Core complete: deterministic core suite, redacted diagnostics, unified error boundary, additive migration history, and unified configuration boundaries.
Working Tree: Candidate implementation is committed; expected clean after this status-only commit.
Runtime Identity: XiaoG backend is healthy on 127.0.0.1:8000 as Python listener PID 24180 launched from D:/XiaoG/.venv/Scripts/python.exe main.py; Batch A code is active after restart.
Tests Completed: Phase 5 Stable matrix retained. Engineering Foundation Batch A: run_core_tests.py deterministic local suite 20/20 passed; covers API contracts, safe DB migration history/idempotence, Conversation lifecycle, Search, Settings, Provider/Model Registry contracts, Auto Router, Phase 5 state regressions, Provider action contracts, diagnostics secret redaction, unified error contract, and configuration secret boundaries. Python compileall, frontend Node syntax, product JSON and diff checks passed. Live local runtime restart passed: /health and /api/provider-status HTTP 200; Terra and DeepSeek status available; live SQLite migration preserved conversation/message/settings counts 9/124/15, schema_version=003_personalization_defaults, integrity_check=ok, foreign_key_check empty; 404/422 responses expose unified credential-free detail.code/message/retryable/retry_action; startup diagnostics emitted database_initialized without secret marker. No paid Provider request was made.
Tests Pending: Batch B 10.8 File / Artifact Lifecycle, 10.9 Provider Health / Fallback / Degradation, 10.10 Backup / Import / Export, then final Engineering Foundation regression and Candidate experience gate.
Known Issues: none found in the affected v0.4.3 scope.
Blockers: none
Backlog / Future Suggestions: none
Product Owner Gate: Phase 5 Accepted Stable Baseline remains 78130be. Batch A is an internal recoverability checkpoint and requires no Product Owner experience because no product-visible regression was introduced. Engineering Foundation final Candidate still requires Product Owner Experience.
Next Allowed Stage: Engineering Foundation Gate / Batch B 10.8 File / Artifact Lifecycle only when context/quota is safe. Phase 5.5, Dual-Codex, Phase 6+, and unauthorized Workers remain prohibited.
Worker Status: No Worker is active in this Autopilot Window.
Roadmap Delta Suggestion: Phase 5 Stable Engineering Addendum accepted by the Product Owner on 2026-09-13: permanent regression coverage for reproducible Product Owner bugs; state-machine-first design for stateful features; Conversation x Manual Model reasoning semantics; combination-path/state-transition regression; Provider action URL/capability/security contracts; quota-efficient local deterministic tests; and staged Local-first, GitHub-on-demand integration.
Protocol Delta Suggestion: none
GitHub Status: no remote is configured and GitHub CLI is not installed; no authentication or repository authorization was inferred. Creating a private repository, authenticating, adding a remote, or pushing requires explicit Product Owner action/authorization and does not block local XiaoG.
Exact Next Action: Begin Engineering Foundation Batch B at 10.6 Permission Abstraction; do not enter later Batch B items until its state ownership, persistence, lifecycle, fallback, and API boundary are explicit.
## Phase 5 Stable Milestone Engineering Addendum

- Product Owner Bug -> Permanent Regression Test: every reproducible Product Owner bug should retain a deterministic regression that fails before and passes after the fix; Product Owner effort should focus on product semantics and experience.
- Stateful Feature = State-Machine-First: define ownership, source of truth, persistence, lifecycle, initialization/hydration, override priority, fallback, cross-scope isolation, and migration/backward compatibility before implementation.
- Conversation x Manual Model Reasoning: preference ownership is Conversation x Manual Model; initialize from that pair, then the model's system default, then Registry-valid fallback. Never copy the current effort from another model. Auto preserves all Manual preferences and reports dynamic routing only in message metadata.
- Combination-path Regression: cover state transitions such as A -> B -> A, Manual -> Auto -> Manual, Model A -> Model B -> Model A, History/New Chat both directions, refresh/restart, archive restore, and Settings changes against existing/new Conversations.
- Provider Action Regression: every displayed usage/billing/recharge/console action must have a non-empty valid official URL, match action_capabilities, remain provider-isolated, hide unsupported actions, use an official billing flow when no stable recharge URL exists, and expose no key/token/Authorization secret.
- Quota Efficiency: prefer deterministic Python/JS/API/DB/state tests; summarize successful suites and expand failures only; keep real Provider/model/external API tests to the minimum necessary set.
- Phase 5 Bug Coverage Inventory: retain existing coverage for History -> New Chat isolation, Draft no-empty-history, Auto/Manual reasoning lifecycle, Conversation and Conversation x Model isolation, per-model Settings defaults, Registry reasoning capabilities, persistence, Provider action correctness, and cold-start Provider card rerender. Any suitable remaining gaps belong in Engineering Foundation Automated Test Suite without unrelated refactoring.
- GitHub Staging: local D:/XiaoG runtime, Git, working tree, and STATUS remain primary truth. Stage 1 permits a private remote and secret scan only with explicit authentication/repository authorization; Stage 2 CI follows Automated Tests; Stage 3 branch/PR/worktree/ownership rules follows Engineering Foundation before any Controlled Dual-Codex setup.
- Future Handoff Requirement: carry this milestone, regression policy, state semantics, quota-efficiency policy, Provider action contract, GitHub staging, and scope guards into the Engineering Foundation handoff.
- Scope Guard: no Phase 5.5, 16GB Controlled Dual-Codex, Phase 6+, unauthorized Worker, restored EXE/Installer, Public Cloud, Phase 9 commercialization, or dual desktop/cloud runtime.
## Engineering Foundation Batch A Checkpoint

- Checkpoint: 4339f7157f289c5d5c5e954d5f21b372771bec9c.
- 10.1 Automated Test Suite: `run_core_tests.py` provides the concise local deterministic command; 20 tests cover required API, safe migrations, Conversation lifecycle, Search, Settings, Provider/Model Registry, Router, and retained Phase 5 regressions without real Provider calls.
- 10.2 Logging / Diagnostics: redacted file/console logs and bounded local recent diagnostics exist; API and Router emit low-cardinality events; Authorization/API key/token patterns are redacted by regression test.
- 10.3 Unified Error Model / Boundary: credential-free `detail` contracts provide code/message/retryable/retry_action across HTTP validation, HTTPException, Provider SSE errors, and unexpected API exceptions while preserving frontend `detail.message` compatibility.
- 10.4 Database Migration History: `schema_migrations` tracks 001 core schema, 002 Conversation lifecycle/model state, and 003 personalization defaults. The live database upgraded additively with unchanged user row counts and passing integrity checks.
- 10.5 Unified Configuration: explicit RuntimeConfig, ProviderConfig, ProviderSecrets and safe configuration summary distinguish local .env secrets, SQLite user settings, product_info metadata, and in-memory runtime state; legacy settings properties remain compatible.

## Engineering Foundation Batch B Progress

- 10.6 Permission Abstraction: complete in `acd3ba1`. `backend.permissions` supplies a local-only, deterministic action boundary: local read/write allow; delete/external action require confirmation; sensitive/non-local deny. It is exposed through the future Tool registry contract only; no Phase 5 route, user data, account model, RBAC, public-cloud behavior, or UI confirmation flow changed. Four targeted regressions passed.
- 10.7 Unified Search Service Continuation: complete in `6ee8743`. Current Conversation Search is explicitly the only enabled domain and is dispatched by the shared `SearchService`; future File/Knowledge/Memory/Project domains must join it rather than create competing search paths. Two targeted regressions passed.
- Batch B affected regression after 10.7: `run_core_tests.py` 26/26 passed locally. No external Provider calls were made.
- Exact next action: inspect and define 10.8 File / Artifact Lifecycle ownership, persistence, deletion, and scope using safe additive changes only; do not enter 10.9 before that boundary is explicit.