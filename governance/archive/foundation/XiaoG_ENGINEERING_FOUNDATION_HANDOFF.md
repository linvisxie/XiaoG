# XiaoG Engineering Foundation Handoff

Date: 2026-09-13 Asia/Shanghai
Autopilot State at handoff: `HANDOFF_REQUIRED`

## Accepted Baselines and Provenance

- Phase 5 Accepted Stable: `78130be33c53d2c2b3c68e378ccc96cce9a144d7`.
- Engineering Foundation Accepted Stable product-code baseline: `ffdfe3de10c87e50afc3d69017b1deaf7e883029` on `main`.
- The baseline includes `30bf8078447c962778ee98968b1afe5cd4a2f85c` as an ancestor. That commit scoped generation ownership to the originating Conversation, but it did **not** prove resolution of the real Product Owner default-Edge navigation problem. Do not describe it as a navigation-bug-fixed candidate.
- Product Owner explicitly accepted Engineering Foundation with the documented Known Issue as a non-blocking risk. This is risk acceptance, not a bug-fix claim.

## Phase 5 and Engineering Foundation Delivered

Phase 5 remains accepted stable. The Foundation added and regression-covered local-first engineering boundaries: deterministic core regression entry point, diagnostics and secret redaction, unified error contracts, additive migration history, unified configuration ownership, local permission abstraction, unified search dispatch, metadata-only File/Artifact lifecycle, provider health/degradation routing, and transactional local backup/import/export.

The Foundation database policy remains additive-only. Current migration history is:

1. `001_core_schema`
2. `002_conversation_lifecycle`
3. `003_personalization_defaults`
4. `004_file_artifact_lifecycle`

No database rebuild, data clearing, or destructive migration is part of this acceptance.

## Known Issue — Navigation delay during generation in real default Edge runtime

### Product Owner observation

In the real default Edge runtime, Conversation A may be processing, thinking, or generating when the user clicks Conversation B, New Chat, or Settings. The UI sometimes does not switch immediately. The intended destination can appear retained, with a delayed jump after A completes.

Temporary workaround: wait for the active response generation to complete before navigating.

### Risk decision

Product Owner accepts this as non-blocking for Engineering Foundation because no data loss, cross-Conversation/message write, database corruption, security issue, or unintended generation cancellation has been observed. Its current impact is navigation experience during generation.

### What was and was not established

The following deterministic diagnostics passed:

- Isolated real Edge with delayed local mock SSE allowed immediate B, Settings, and Draft navigation while A generated.
- The same was true before the first delta and during high-frequency delta rendering.
- Real XiaoG ASGI with a local delayed fake Provider served health, Conversation, defaults, Settings, personalization, and provider-status requests concurrently while A generated.
- No global frontend lock, intentional pending-navigation queue, backend event-loop/API-concurrency blocker, or synthetic stale-navigation replay was proven.

The actual Product Owner default Edge profile could not be traced through CDP: it ignored remote-debugging arguments. That restriction was respected. No browser profile was copied, cleared, or bypassed; user data remained intact; and no real Provider was invoked during the trace attempt.

Conclusion: the root cause is currently unknown. Synthetic passes neither reproduce nor dismiss the real runtime issue. Reopen when a real-runtime trace is available, frequency materially increases, data/message pollution appears, a wrong generation is cancelled, SQLite/state damage appears, relevant frontend/runtime architecture changes, or Product Owner raises priority.

## Regression and Test Governance

Run the concise deterministic local suite first:

```text
.\\.venv\\Scripts\\python.exe run_core_tests.py
```

Final closeout evidence:

- Core regression: 34 passed, 0 failed, 0 errors, 0 skipped.
- Python compile checks for the retained E2E harnesses: passed.
- `node --check frontend/app.js` and `node --check frontend/i18n.js`: passed.
- `tests/e2e_playwright_smoke.py`: passed using an isolated dynamic HTTP server and headless Edge; no XiaoG API or Provider call.
- `tests/e2e_generation_navigation.py`: passed with local delayed mock SSE and fake Provider. It proves the synthetic path remains free of a global generation lock, preserves originating-Conversation stream ownership, permits B/Settings/Draft before completion, avoids an empty Draft Conversation, and finds no synthetic stale-navigation replay.
- SQLite: all four migrations present, `integrity_check=ok`, and no foreign-key violations.
- Security: core tests cover diagnostics redaction and configuration-secret boundaries. The retained E2E harnesses do not use real Provider credentials.

Testing rule: deterministic synthetic E2E is valuable to prevent regression of the already-working synthetic path; it must never be labelled coverage of the unresolved real default-Edge Known Issue. Use real Provider calls only when a specific Product Owner-authorized diagnosis requires them.

## Runtime and Cache Identity

- Product Owner runtime examined: local XiaoG on `http://127.0.0.1:8000`, served by `D:\\XiaoG\\.venv\\Scripts\\python.exe main.py`.
- Frontend asset/cache identity: `i18n.js?v=0.4.3-generation-navigation-r1` and `app.js?v=0.4.3-generation-navigation-r1`.
- This closeout changes documentation and test classification only; it does not change product behavior or cache-busting identity.

## Harness Classification

- Retain `tests/e2e_playwright_smoke.py`: small deterministic local readiness and Edge smoke.
- Retain `tests/e2e_generation_navigation.py`: deterministic local synthetic generation-navigation regression, explicitly scoped away from the Known Issue.
- Remove `tests/e2e_trace.py`: temporary trace/DOM-inspection diagnostic with no durable regression value.

## GitHub and Repository State

No Git remote is configured. GitHub CLI is not installed. No repository creation, login, authentication, remote addition, or push was performed or authorized. Local Git and the working tree remain the source of truth.

## Backlog for a Future Tech Lead Decision

### DeepSeek Model Registry maintenance — do not implement in this handoff

When explicitly scheduled, safely migrate the old `deepseek-v4-flash` registry entry to the official latest stable `deepseek-flash` entry, update the display name to `DeepSeek V4.1 Flash`, and revalidate capabilities against current official announcement/API documentation plus a minimal real API verification. Handle retired V4-Flash and V4-Flash-Vision-Exp entries correctly. Preserve existing Settings, Conversations, and per-model reasoning preferences through safe additive migration and backward compatibility; do not perform a global string replacement.

## Preconditions Before Any New Phase

A Tech Lead must explicitly decide whether and when to start any follow-on work. Do not autonomously begin Phase 5.5, Controlled Dual-Codex, Phase 6+, any Worker, DeepSeek Registry work, or GitHub integration. The known issue above remains part of that decision context.

## Handoff Outcome

`AUTOPILOT_SCOPE_COMPLETE`

`HANDOFF_TO_TECH_LEAD_REQUIRED`