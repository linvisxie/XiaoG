# XiaoG Web Preview WP-4 Handoff

Activation: `XIAOG-AUTOPILOT-WEB-PREVIEW-WP4-2026-09-14-V1`  
State: `HANDOFF_REQUIRED`

## Window

- Start provenance: `main` / `4047fc8d6fe41c09de747720506aa1ec26986673`, clean tree, no remote. The accepted Preview product candidate remains `7bd80be7028e521a5d837bdd8f8a2b3c0adcc88b`.
- Scope completed: local CI/test-gated release and deployment automation readiness only.
- Stop gate reached: no external CI execution, source-control remote, registry, hosting, DNS, external secret, Provider, or external access was performed or is authorized.

## Delivered

- `tools/ci/wp4_release_gate.py` implements a deterministic no-network release gate. It requires a full reachable Git revision and, in strict mode, a clean working tree. It checks Git whitespace consistency, scans tracked and non-ignored untracked files for explicit Provider/invite/CI secret assignments, compiles Python, checks every frontend JavaScript file with Node, runs core regression, Preview smoke, and explicit WP-3 access/streaming verification.
- A successful gate emits only a temporary manifest by default. When requested, its deterministic manifest uses `xiaog-preview-<full-git-revision>` as the Preview release ID and records the immutable source revision, runtime mode, provider policy, and ephemeral-session policy.
- `.github/workflows/wp4-release-gate.yml` is a local definition only. Its future CI job runs the gate and a local container build-label assertion; it has no deploy, registry publish, credentials, or external-access job.
- The Dockerfile now rejects a missing/non-full source revision and labels the image with `org.opencontainers.image.revision`. It contains no secret or runtime release ID. `deploy/preview.env.example` and `deploy/WEB_PREVIEW_WP4_RELEASE_CONTRACT.md` define only placeholders and a target-neutral release, health, rollback, and external-authorization contract.
- The release/rollback contract preserves accepted behavior: local mode is unchanged; Preview is explicit, invite-only, ephemeral/session-isolated, DeepSeek-only, Terra-disabled, and has no open registration.

## Verification evidence

On clean checkpoint `56748d416a4ae9bbe0f651b3218c15fd22c65147`:

```text
.\.venv\Scripts\python.exe tools\ci\wp4_release_gate.py --revision HEAD
```

Passed:

- `run_core_tests.py`: 44 run, 0 failures, 0 errors, 0 skipped.
- `tests/preview_release_smoke.py`: passed using ASGI and fake/local dependencies only; validates Preview health/release ID, docs closure, secure access cookie, authenticated conversation creation, and logout invalidation.
- `python -m unittest tests.test_preview_access tests.test_preview_streaming`: 7 tests passed; access boundary and fake-stream success/error/cancel counter-release coverage.
- Python `compileall`, frontend Node syntax, Git diff checks, revision/clean-tree checks, and secret scan all passed through the gate.

Docker is unavailable on this workstation (`docker` command not found). No local container build or container smoke was run, and no substitute result is claimed. The Docker build-label assertion remains defined for a future authorized CI environment.

## Candidate and Git

The WP-4 local readiness candidate is created by the accompanying `candidate:` commit. Its exact hash is recorded in STATUS and this Handoff by the following documentation provenance commit after the candidate has passed the strict gate. No product runtime changes occur in that provenance update.

## External gate / minimum Product Owner authorization

Local readiness is complete. Further progress requires a point-in-time Product Owner decision naming the target(s) and granting only the necessary actions, for example:

1. authenticate to and configure a chosen source-control/CI service, including repository/remote/push if desired;
2. choose and create a container registry and/or hosting target, and permit an image publish or deployment there;
3. inject `DEEPSEEK_API_KEY` and `XIAOG_PREVIEW_INVITES` through that target's server-side secret facility;
4. configure domain/DNS/HTTPS or invited external access, if separately desired;
5. authorize any real Provider request and provider-side spend/budget action.

Those steps cannot be replaced locally because they mutate third-party accounts, hold real secrets, can incur cost, and can make the Preview externally reachable. Terra remains outside this window and needs its separate server-side readiness/authentication authorization.

`AUTOPILOT_HANDOFF_READY`
