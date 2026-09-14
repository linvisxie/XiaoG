# XiaoG Web Preview WP-4 Handoff

Activation: `XIAOG-AUTOPILOT-WEB-PREVIEW-WP4-2026-09-14-V1`  
State: `HANDOFF_REQUIRED`

GitHub source-control authorization: `XIAOG-WP4-GITHUB-SOURCE-CONTROL-GATE-2026-09-14-V1`.

This Handoff also records Product Owner-supplied ECS Preview deployment-verification evidence. It does not authorize a further external action.

## Window

- Start provenance: `main` / `4047fc8d6fe41c09de747720506aa1ec26986673`, clean tree, no remote. The accepted Preview product candidate remains `7bd80be7028e521a5d837bdd8f8a2b3c0adcc88b`.
- Scope completed: local CI/test-gated release and deployment automation readiness, GitHub source-control/CI, and recorded ECS Preview deployment verification evidence.
- Original local stop gate was reached, then the Product Owner granted the bounded GitHub source-control/CI authorization above. That gate is complete. The Product Owner subsequently supplied ECS Preview deployment-verification evidence for the immutable revision below. This documentation update does not authorize public exposure, DNS, HTTPS configuration, external secrets, real Provider, or invited external access.

## Delivered

- `tools/ci/wp4_release_gate.py` implements a deterministic no-network release gate. It requires a full reachable Git revision and, in strict mode, a clean working tree. It checks Git whitespace consistency, scans tracked and non-ignored untracked files for explicit Provider/invite/CI secret assignments, compiles Python, checks every frontend JavaScript file with Node, runs core regression, Preview smoke, and explicit WP-3 access/streaming verification.
- A successful gate emits only a temporary manifest by default. When requested, its deterministic manifest uses `xiaog-preview-<full-git-revision>` as the Preview release ID and records the immutable source revision, runtime mode, provider policy, and ephemeral-session policy.
- `.github/workflows/wp4-release-gate.yml` is a local definition only. Its future CI job runs the gate and a local container build-label assertion; it has no deploy, registry publish, credentials, or external-access job.
- The Dockerfile now rejects a missing/non-full source revision and labels the image with `org.opencontainers.image.revision`. It contains no secret or runtime release ID. `deploy/preview.env.example` and `deploy/WEB_PREVIEW_WP4_RELEASE_CONTRACT.md` define only placeholders and a target-neutral release, health, rollback, and external-authorization contract.
- The release/rollback contract preserves accepted behavior: local mode is unchanged; Preview is explicit, invite-only, ephemeral/session-isolated, DeepSeek-only, Terra-disabled, and has no open registration.

## ECS Preview deployment verification

Product Owner-supplied runtime evidence records the following completed verification:

- Host: Alibaba Cloud ECS Hong Kong.
- Image revision: `7814fc0f57af9cd5db677d121b50d32437f81b73`.
- Runtime health: `status=ok`; `commit=7814fc0f57af9cd5db677d121b50d32437f81b73`; `release_id=xiaog-preview-7814fc0f57af9cd5db677d121b50d32437f81b73`.

The health evidence confirms that the container runtime reported the immutable deployed revision and matching release identity. It contains no secret value. It is not evidence of, and does not authorize, public exposure, DNS, HTTPS configuration, real Provider requests, external secret injection, or invited external access.

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

Docker is unavailable on this workstation (`docker` command not found). No local container build or container smoke was run. GitHub CI supplied the container build-label contract evidence, and the Product Owner supplied the separate ECS runtime health evidence above.

## Candidate and Git

The original local candidate `38455d0cee8c5a572761b5283821dc54f71b6d3e` exposed one CI-only quoting defect in the Docker revision-label inspection command. The release gate and image build themselves succeeded; the final `docker image inspect` Go-template contained unnecessary backslashes.

Replacement candidate: `641f5fb360f0f8e6e0cbaf27fbff3182a79d3550` (`fix: correct WP-4 container label check`). This is a one-line workflow-only correction; no product backend, frontend, schema, runtime semantics, provider behavior, or secret handling changed. The full local release gate passed on this commit, then it was non-force pushed to `main`.

Current ECS-verified Preview revision: `7814fc0f57af9cd5db677d121b50d32437f81b73` (`fix: expose container source revision in health`). This minimal backend change returns a valid 40-character lowercase `XIAOG_SOURCE_REVISION` before retaining the existing Git fallback. Three deterministic tests cover valid, invalid, and absent environment values. The clean-tree local release gate passed with 47/47 core tests, and GitHub Actions run `34836960055` completed successfully on that exact commit.

GitHub identity and CI evidence:

- Repository: `linvisxie/XiaoG`, Private, `https://github.com/linvisxie/XiaoG`.
- Remote: `origin` / `https://github.com/linvisxie/XiaoG.git` (fetch and push); local `main` tracks `origin/main`.
- Initial pushed history reached `7cb2e1ef0a5ede0114057f820505741667b712e2`. Its Actions run `34777920498` failed only at the malformed inspect template; the release gate passed and no artifact was published.
- Replacement commit `641f5fb360f0f8e6e0cbaf27fbff3182a79d3550` was pushed normally. Actions run `34778077074` succeeded: `release-gate` and `Build local container artifact contract` both passed. No container registry publish, deployment, secret injection, or external access occurred.
- Current ECS-verified revision `7814fc0f57af9cd5db677d121b50d32437f81b73` was pushed normally. Actions run `34836960055` succeeded. The ECS runtime verification is recorded above; it does not add authorization for public exposure, DNS, HTTPS configuration, external secrets, real Provider, or invited external access.

## External gate / minimum Product Owner authorization

Local readiness and the recorded ECS Preview runtime verification are complete. Further progress requires a new point-in-time Product Owner decision naming the target and granting only the necessary action, for example:

1. inject real `DEEPSEEK_API_KEY` and `XIAOG_PREVIEW_INVITES` through the target's server-side secret facility;
2. configure DNS and HTTPS or allow invited external access, if separately desired;
3. authorize any real Provider request and provider-side spend/budget action.

Those steps cannot be replaced locally because they mutate third-party accounts, hold real secrets, can incur cost, and can make the Preview externally reachable. Terra remains outside this window and needs its separate server-side readiness/authentication authorization. No such action starts automatically.

`AUTOPILOT_HANDOFF_READY`
