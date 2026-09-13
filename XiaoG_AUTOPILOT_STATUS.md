# XiaoG Autopilot Status

Protocol Version: v1.4 FINAL
Activation ID: XIAOG-AUTOPILOT-PHASE5-2026-09-12-V1
Roadmap Version: XiaoG Master Roadmap v2 (2026-09-12)
Autopilot State: HANDOFF_REQUIRED
MILESTONE: PHASE_5_STABLE_REACHED
MILESTONE: ENGINEERING_FOUNDATION_ACCEPTED_STABLE
Window Start: 2026-09-12 Asia/Shanghai
Window Stop Gate: Engineering Foundation accepted by Product Owner with documented non-blocking Known Issue; Tech Lead handoff required.
Current Stage: Engineering Foundation Accepted Stable / Handoff Required
Current Task: Handoff is prepared; stop autonomous progression and transfer to Tech Lead.
Current Branch: main
Start Accepted Baseline: v0.4.0 / 7ddab006a618ede56e3d22d55ba2f212d8f47cd0
Last Accepted Stable Baseline: Phase 5 / 78130be33c53d2c2b3c68e378ccc96cce9a144d7
Engineering Foundation Accepted Product Code Baseline: ffdfe3de10c87e50afc3d69017b1deaf7e883029
Candidate Provenance: 30bf8078447c962778ee98968b1afe5cd4a2f85c is an ancestor of the accepted Foundation baseline. It was previously presented as a generation-navigation repair candidate, but Product Owner experience did not prove the real default-Edge navigation issue fixed. It is not accepted as a navigation-bug-fix candidate.
Product Owner Decision: Engineering Foundation is accepted with the Known Issue below as a non-blocking risk acceptance. This is not a claim that the issue is fixed or absent.

## Known Issue — Navigation delay during generation in real default Edge runtime

In the Product Owner's real default Edge environment, while Conversation A is processing, thinking, or generating, clicking Conversation B, New Chat, or Settings sometimes does not switch immediately. The clicked destination appears retained and, when A finishes, the UI may jump to the last clicked destination.

- Current workaround: wait for the current response generation to finish before navigating.
- No data loss, Conversation/message cross-write, database corruption, security issue, or erroneous generation cancellation was observed.
- Impact: generation-time navigation experience only; accepted by Product Owner as non-blocking for Engineering Foundation.
- Root cause: currently unknown.

Diagnostic facts, which must not be over-interpreted:

- Isolated real Edge with delayed local mock SSE navigated immediately to B, Settings, and Draft during generation.
- Navigation also worked during the pre-first-delta window and during high-frequency delta rendering.
- Real XiaoG ASGI with a local fake Provider returned normal API requests concurrently during a generation.
- No provable frontend global lock, pending-navigation queue, backend event-loop blocker, or synthetic stale-navigation replay was found.
- The real default Edge profile did not expose CDP: it ignored remote-debugging arguments. The safety restriction was not bypassed, no profile was copied or cleared, and no real Provider call was made during that capture attempt.
- Therefore synthetic passes do not prove the real Product Owner issue does not exist, and they do not resolve it.

Reopen investigation if a trace becomes available in the real runtime, frequency rises materially, data/message pollution appears, a wrong generation is cancelled, SQLite/state damage appears, relevant frontend/runtime architecture changes materially, or Product Owner raises priority.

## Final Verification

- `run_core_tests.py`: 34 passed, 0 failures, 0 errors, 0 skipped; deterministic and no real Provider calls.
- Retained local Edge smoke: passed; isolated dynamic loopback HTTP 200 then DOM click.
- Retained synthetic generation-navigation E2E: passed; local delayed SSE plus fake Provider verified B/Settings/Draft commit before generation completion, no Draft-created empty conversation, no cross-conversation stream pollution, no synthetic stale navigation replay, and ordinary ASGI API concurrency.
- Python harness compilation and `node --check frontend/app.js` / `frontend/i18n.js`: passed.
- SQLite: migration history `001_core_schema` through `004_file_artifact_lifecycle`; `integrity_check=ok`; `foreign_key_check` empty.
- Security boundary: core regression includes credential redaction and configuration-secret boundary checks; retained harnesses make no Provider call and emit no credential values.
- Frontend asset identity was not changed by this closeout: `0.4.3-generation-navigation-r1`.

## Test Harness Classification

- Retained: `tests/e2e_playwright_smoke.py` is a bounded, isolated local Edge and HTTP-readiness smoke; it does not call XiaoG APIs or a Provider.
- Retained: `tests/e2e_generation_navigation.py` is a deterministic local synthetic regression for global generation lock and cross-conversation stream-pollution regressions. Its scope explicitly excludes the unresolved real default-Edge Known Issue.
- Removed: `tests/e2e_trace.py` was one-time trace/debug infrastructure with no long-term regression value.

## Handoff and Scope Guard

- Complete handoff: `XiaoG_ENGINEERING_FOUNDATION_HANDOFF.md`.
- GitHub: no remote is configured and no GitHub authentication, repository creation, or push was performed or authorized.
- Backlog only, not implemented: DeepSeek Registry maintenance from `deepseek-v4-flash` to official `deepseek-flash`, display name `DeepSeek V4.1 Flash`, official capability verification, retired model handling, and safe additive/backward-compatible preservation of existing Settings, Conversations, and per-model reasoning preferences.
- Next allowed state: HANDOFF_REQUIRED only. Do not autonomously begin Phase 5.5, Controlled Dual-Codex, Phase 6+, Workers, DeepSeek Registry maintenance, or GitHub work.
- Exact next action: Tech Lead reviews and accepts the handoff before authorizing any new scope.