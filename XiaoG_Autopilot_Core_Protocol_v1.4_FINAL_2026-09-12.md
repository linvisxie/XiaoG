# XiaoG Autopilot Core Protocol v1.4 FINAL
## Plus-Efficient · Recoverable · State-Machine-Gated

**Document Type:** Permanent Autopilot Core Protocol  
**Protocol Version:** v1.4 FINAL  
**Date:** 2026-09-12  
**Applies To:** XiaoG Main Codex  
**Product Owner:** User  
**Tech Lead / Architect / Reviewer:** ChatGPT

---

# 0. Core Definition

Autopilot means:

> **Codex may autonomously complete engineering work inside an explicitly authorized Autopilot Window, but Product Owner approval is mandatory between product stages.**

Autopilot is not unlimited autonomy.

Autopilot is always bounded by:

- Start baseline
- Allowed scope
- Stop gate
- Product Owner gates
- Roadmap
- Git reality
- Safety guards

---

# 1. Authority Model

## 1.1 Master Roadmap

The Master Roadmap is the highest authority for:

- product direction
- phase sequence
- architecture principles
- ADRs
- permanent requirements
- removed routes
- phase boundaries
- long-term hard requirements

Roadmap progress text may become stale after an Autopilot Window begins.

Therefore:

> Roadmap determines **where XiaoG should go**.

---

## 1.2 Git + AUTOPILOT_STATUS

During an active Autopilot Window, live project state is determined by:

1. Git repository evidence
2. current working tree
3. `XiaoG_AUTOPILOT_STATUS.md`
4. Candidate / Accepted Baseline commits

Therefore:

> Git + STATUS determine **where XiaoG actually is now**.

---

## 1.3 Conflict Priority

If live status sources disagree:

1. Git object history / actual files
2. current working tree evidence
3. test evidence
4. AUTOPILOT_STATUS
5. chat memory

If STATUS conflicts with Git:

> **Repair STATUS to match Git. Never mutate Git merely to make STATUS look correct.**

---

# 2. Immutable Governance Documents

Main Codex MUST NOT autonomously modify:

- Master Roadmap
- Autopilot Core Protocol
- Autopilot Activation issued by Tech Lead

If changes appear necessary:

- record `Roadmap Delta Suggestion`
- record `Protocol Delta Suggestion`
- stop only if the conflict blocks safe work

Main Codex MAY maintain:

- `XiaoG_AUTOPILOT_STATUS.md`
- `XiaoG_AUTOPILOT_HANDOFF_YYYY-MM-DD.md`
- code
- tests
- changelog
- engineering docs
- migration docs
- diagnostics docs

---

# 3. Autopilot Activation

The Core Protocol does NOT define the current development window.

Every Autopilot Window must have a separate:

`XiaoG_AUTOPILOT_ACTIVATION_<scope>_<date>.md`

Activation must define:

- Roadmap identity
- Roadmap version/hash
- Start Accepted Baseline commit
- Start stage
- Allowed Scope
- Stop Gate
- Worker policy
- special constraints
- expected first action

If Activation is missing:

> Autopilot must not start.

---

# 4. State Machine

Main Codex must maintain exactly one Autopilot state.

Valid states:

```text
INACTIVE
RUNNING
PAUSED_RECOVERABLE
WAITING_FOR_PRODUCT_OWNER_EXPERIENCE
ACCEPTING_CANDIDATE
HANDOFF_REQUIRED
CLOSED
```

---

## 4.1 INACTIVE

Autopilot is not active.

Do not interpret “继续工作” as Autopilot authorization.

---

## 4.2 RUNNING

Codex is actively implementing the current authorized stage.

“继续工作” while RUNNING means:

> Continue the current unfinished stage.

It does NOT approve a future stage.

---

## 4.3 PAUSED_RECOVERABLE

Work was interrupted by:

- quota
- context limit
- provider outage
- recoverable external blocker
- user pause

“继续工作” while PAUSED_RECOVERABLE means:

> Resume the current stage from STATUS + Git.

It does NOT accept a Candidate.

---

## 4.4 WAITING_FOR_PRODUCT_OWNER_EXPERIENCE

Current Candidate is complete and ready for user experience.

Only in this state does:

**继续工作**

mean:

> User accepts the current Candidate.

Then state becomes:

`ACCEPTING_CANDIDATE`

---

## 4.5 ACCEPTING_CANDIDATE

Codex must first verify Candidate Provenance.

If verification passes:

- mark Candidate as Accepted Stable Baseline
- update STATUS
- determine next authorized stage

If Stop Gate reached:

→ `HANDOFF_REQUIRED`

Otherwise:

→ `RUNNING`

---

## 4.6 HANDOFF_REQUIRED

No new product development is allowed.

Codex must:

- create/update Handoff
- stop at safe state

Then:

`CLOSED`

---

## 4.7 CLOSED

Current Autopilot Window is over.

A new Activation is required to enter autonomy again.

---

# 5. Control Commands

## “开启自治模式”

Sent to:

**ChatGPT Tech Lead**

Meaning:

- assess current project state
- create a new Activation
- user sends Activation to Main Codex

---

## “继续工作”

Sent to:

**Main Codex**

Meaning depends ONLY on current state:

| State | Meaning |
|---|---|
| RUNNING | continue current unfinished stage |
| PAUSED_RECOVERABLE | resume current stage |
| WAITING_FOR_PRODUCT_OWNER_EXPERIENCE | accept Candidate and advance |
| HANDOFF_REQUIRED | do not advance; finish handoff |
| CLOSED / INACTIVE | no Autopilot authority |

Codex must never infer meaning from conversational tone when STATUS gives a state.

---

## “恢复旧模式”

Sent to:

**ChatGPT Tech Lead**

ChatGPT will generate a short:

`STOP_AND_HANDOFF`

instruction.

User sends it to Main Codex.

Main Codex then enters:

`HANDOFF_REQUIRED`

and does not continue product development.

---

# 6. Candidate Provenance Check

A Candidate may be accepted only if ALL are true:

1. Candidate commit exists
2. Candidate commit hash matches STATUS
3. Candidate commit is reachable from expected branch
4. runtime-relevant working tree has no unexplained changes after Candidate
5. frontend cache-busting has been applied where required
6. the version the user experienced corresponds to the Candidate
7. required tests associated with that Candidate passed
8. no later uncommitted runtime code silently changed behavior

If any item fails:

> Candidate must NOT be marked Accepted.

Return to current stage repair/verification.

---

# 7. Runtime Identity for User Experience

Before asking Product Owner to experience a Candidate, Codex should expose enough identity to verify what is running.

At minimum, experience report should include:

- Candidate commit
- app version
- current branch
- whether backend was restarted
- whether frontend cache was refreshed/version-busted
- relevant runtime/provider status

If XiaoG already exposes self-version/commit information, use it.

Goal:

> The user must experience the same build that will be accepted.

---

# 8. Git Commit Semantics

## Internal Checkpoint

Purpose:

- quota/context recovery
- safe partial progress

Not Stable.

Suggested commit marker:

`checkpoint:`

---

## Candidate Commit

Created after:

- implementation
- required targeted tests
- one formal self-review
- required corrections
- affected regression
- stage final regression

Candidate is:

> technically ready for user experience

Candidate is NOT yet Stable.

Suggested marker:

`candidate:`

---

## Accepted Stable Baseline

Only after:

- Product Owner actually experiences Candidate
- Product Owner says “继续工作”
- Candidate Provenance Check passes

STATUS records:

`Accepted Stable Baseline = <commit>`

No history rewrite is required.

---

# 9. Working Tree Policy

Before Candidate delivery:

Preferred:

`git status = clean`

If not clean:

Codex must explicitly classify remaining changes as:

- intentional non-runtime metadata
- temporary test artifact
- blocked external change
- unsafe/unrelated unknown change

Runtime code changes after Candidate are not allowed before user experience unless Candidate is replaced.

If Candidate changes:

> create a new Candidate commit and update STATUS.

---

# 10. STATUS File Policy

Maintain:

`XiaoG_AUTOPILOT_STATUS.md`

STATUS is a lightweight recovery file.

It should contain:

```text
Protocol Version:
Activation ID:
Roadmap Version:
Roadmap Content Hash:

Autopilot State:
Window Start:
Window Stop Gate:

Current Stage:
Current Task:
Current Branch:

Start Accepted Baseline:
Last Accepted Stable Baseline:
Current Candidate:
Last Checkpoint:

Working Tree:
Runtime Identity:
Tests Completed:
Tests Pending:

Known Issues:
Blockers:
Backlog / Future Suggestions:

Product Owner Gate:
Next Allowed Stage:

Worker Status:
Roadmap Delta Suggestion:
Protocol Delta Suggestion:
Exact Next Action:
```

---

# 11. STATUS Storage Rule

STATUS and Handoff are engineering control artifacts.

Preferred behavior:

- store them inside the XiaoG repository under a dedicated control/docs location if the project structure allows
- commit them when appropriate for reproducibility
- do not let STATUS-only edits falsely make a Candidate runtime-dirty

If the existing project has a better control-doc location, use it.

If unsure:

- place under a clearly named project docs/control folder
- do not put secrets inside

---

# 12. Plus-Efficient Context Strategy

## First Activation

Read:

- Roadmap
- Core Protocol
- Activation
- relevant Git state
- current interrupted work

## Normal continuation

Prefer:

- STATUS
- git status
- relevant git log
- current Roadmap section
- directly affected code
- directly relevant ADR/permanent requirements

Do NOT repeatedly:

- reread entire Roadmap
- reread entire Core Protocol
- rescan whole repository
- analyze future phases

---

# 13. Scope Guard

Autonomous work may include only:

- current stage requirements
- real current-stage bugs
- regressions caused by current work
- minimum necessary refactor
- minimum necessary tests

Do NOT “improve while here”:

- unrelated UI polish
- future features
- unrelated performance work
- speculative architecture
- new provider
- nonessential dependency upgrades
- future phase abstractions

Record such ideas under:

`Backlog / Future Suggestions`

---

# 14. Test Strategy

## Level 1 — Targeted

During implementation.

## Level 2 — Affected Regression

After fixes/self-review.

## Level 3 — Stage Final Regression

Only before Candidate delivery.

Do not run Level 3 after every small change.

---

# 15. Self Review Rule

Default:

**one formal Self Review per Candidate cycle**

Check:

- Roadmap omissions
- fake support
- capability lies
- provider hardcoding
- DB/migration risk
- cache-busting
- security
- secrets
- retry/error behavior
- i18n
- settings persistence
- permanent requirement regressions
- removed-route regressions
- unnecessary scope expansion

If issues are found:

- fix
- targeted retest
- affected regression if needed

Do not perform endless “one more review”.

---

# 16. Efficiency Guard

Stop and report if any condition occurs.

## E1
Same root cause failed after 2 repair cycles.

## E2
A third heavy Stage Final Regression would be required.

## E3
External Provider/API repeatedly fails and root cause cannot be distinguished.

## E4
A large architecture rewrite is required but not authorized.

## E5
Remaining quota/context is clearly insufficient to safely finish the next major step.

## E6
Progress requires broad unrelated refactoring outside current scope.

When triggered:

- checkpoint if safe
- update STATUS
- set state `PAUSED_RECOVERABLE`
- output:

`EFFICIENCY_GUARD_STOP`

---

# 17. External Cost Guard

Real Provider tests may consume paid API quota.

Rules:

- prefer smallest valid real test
- avoid repetitive real-provider calls
- reuse local/unit tests when provider behavior is already proven
- do not brute-force provider testing

Default external retry budget:

- same real-provider test: max 2 retries after initial attempt

If still ambiguous:

- stop
- record exact request class/error
- use Efficiency Guard

Never invent support because a paid API test was skipped or failed.

---

# 18. Quota / Context Recovery

If quota/context is nearly exhausted:

1. do not begin a new large modification
2. finish minimum safe boundary
3. create checkpoint if useful
4. update STATUS
5. set state `PAUSED_RECOVERABLE`
6. record exact next action

Later:

**继续工作**

means resume current stage.

---

# 19. Product Owner Gate

Before requesting user experience:

- Candidate exists
- required tests passed
- app is runnable
- runtime identity is clear
- working tree is clean or explained
- STATUS updated

Then state:

`WAITING_FOR_PRODUCT_OWNER_EXPERIENCE`

Codex must STOP.

---

# 20. Experience Report

Keep concise.

Include:

## Stage
## Completed
## Verification
## Self Review & Corrections
## Experience Guide
## Experience Checklist
## Runtime Identity
## Git
## Known Issues
## Next Allowed Stage
## Autopilot State

Do not paste full logs unless needed.

---

# 21. User Reports a Bug

Remain in same stage.

Do:

- reproduce
- diagnose
- fix
- targeted test
- affected regression
- final regression if needed
- create NEW Candidate
- update STATUS
- return to WAITING state

Never accept the old Candidate.

---

# 22. Engineering Foundation Large-Stage Rule

Large internal engineering stages may use internal checkpoint batches.

Checkpoints:

- do not require Product Owner experience unless Activation says so
- are not Stable
- exist for recoverability only

Final Gate still requires:

Candidate → Product Owner Experience → Accepted Stable Baseline.

---

# 23. Handoff

When state becomes:

`HANDOFF_REQUIRED`

generate:

`XiaoG_AUTOPILOT_HANDOFF_YYYY-MM-DD.md`

Include:

## Identity
- Core Protocol version
- Activation ID/version
- Roadmap version/content hash

## Window
- start baseline
- allowed scope
- stop gate
- actual endpoint

## Git
- branch
- git status
- working tree
- checkpoints
- candidates
- accepted baselines
- relevant git log

## Architecture Changes
- services
- registries
- DB/schema/migrations
- provider/router/config changes

## Verification Evidence
For important tests:
- exact command
- pass/fail summary
- scope

## Product Status
- completed stages
- known issues
- blockers
- runtime/start method
- requirement changes

## Next
- next unique correct task
- Worker status
- dual-Codex status
- Tech Lead takeover recommendation

## Governance
- Roadmap modified? expected NO unless explicitly authorized
- Protocol modified? expected NO
- Roadmap Delta Suggestions
- Protocol Delta Suggestions

End with:

`AUTOPILOT_HANDOFF_READY`

---

# 24. Emergency Takeover Fallback

If Main Codex cannot generate Handoff because:

- quota is exhausted
- context is unavailable
- Codex session is inaccessible

Product Owner may give ChatGPT Tech Lead:

- latest `XiaoG_AUTOPILOT_STATUS.md`
- latest `git status`
- latest relevant `git log`
- current branch
- current Candidate/checkpoint hash
- any visible Codex final message

Tech Lead may reconstruct an emergency handoff from Git + STATUS.

Therefore:

> Handoff is preferred, but project governance must never depend on one chat session surviving.

---

# 25. Dual-Codex Rule

After Worker Codex exists, this Core Protocol may still be used, but Activation must explicitly choose:

## Main-Only Window
Worker idle.

or

## Controlled Dual-Codex Window

Tech Lead must define:

- API contract
- schema ownership
- file ownership
- task boundary
- integration owner
- test responsibility
- heavy runtime owner

Two Codex instances must not freely edit main simultaneously.

---

# 26. Safety Invariants

Always preserve Roadmap rules for:

- multi-provider extensibility
- database safety
- conversation/history data
- archive/trash lifecycle
- safe migrations
- secret isolation
- frontend cache-busting
- permanent requirements
- future hard phases
- removed routes

Autopilot cannot override project constitution.

---

# 27. Hard Stop Conditions

Stop and escalate only for:

- destructive data risk
- credential/secret risk
- major Roadmap conflict
- ADR change required
- major product decision
- sensitive/high-risk permission
- unresolved external blocker
- Efficiency Guard
- first Worker setup requiring user action

Ordinary engineering bugs should be handled autonomously.

---

# 28. Final Principle

> Roadmap governs direction.

> Git governs reality.

> STATUS governs recoverability.

> Activation governs the current autonomy boundary.

> Candidate is not Stable.

> Product Owner experience turns Candidate into Accepted Stable Baseline.

> Autopilot is temporary, bounded, recoverable, and reversible.

# END
