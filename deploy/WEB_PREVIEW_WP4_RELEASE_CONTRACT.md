# WP-4 Local Release and Deployment Contract

This document defines readiness only. It does not choose a CI provider, hosting provider, registry, domain, or secret manager, and it authorizes no deployment.

## Test-gated release selection

For a full immutable Git commit `<revision>`, run:

```text
python tools/ci/wp4_release_gate.py --revision <revision> --manifest <local-output>/xiaog-release-manifest.json
```

The gate fails before manifest creation if the checkout is dirty, a Git diff has whitespace errors, a tracked file contains a likely real secret assignment, Python compilation fails, frontend JavaScript syntax fails, `run_core_tests.py` fails, the Preview release smoke fails, or the explicit WP-3 access/streaming tests fail. It uses only local/fake dependencies; it makes no Provider request.

The deterministic manifest derives `release_id` as `xiaog-preview-<full-revision>`. A release target must use precisely that value for `XIAOG_RELEASE_ID`, preserve the full revision as `XIAOG_SOURCE_REVISION`, and reject a mismatch. `XIAOG_RELEASE_ID` stays runtime configuration and is never baked into source control or the container image.

## Container artifact contract

Build only after the release gate succeeds:

```text
docker build --build-arg XIAOG_SOURCE_REVISION=<full-revision> --tag xiaog-preview:<full-revision> .
```

The Dockerfile rejects an absent or non-full SHA-1 revision and labels the image with `org.opencontainers.image.revision`. The image contains no invite or Provider secret. At runtime, inject only named server-side values from `deploy/preview.env.example`: `DEEPSEEK_API_KEY`, `XIAOG_PREVIEW_INVITES`, and the non-secret runtime settings. Do not use browser values, Git, image layers, or logs for those secrets.

## Future deployment and verification

A later, separately authorized deployment must use the same-origin HTTPS/reverse-proxy and SSE rules in `docs/WEB_PREVIEW_WP2_RUNTIME_CONTRACT.md`. Before traffic is enabled, verify `/health` returns `status=ok`, `runtime_mode=preview`, the manifest `release_id`, and the expected source revision when VCS metadata is available. Then run the deterministic Preview smoke against the release configuration with fake/local dependencies before any real Provider request.

Preview remains invite-only, isolated, ephemeral/non-persistent, DeepSeek-only, Terra-disabled, and without open registration. No automatic step may change those policies.

## Rollback

Keep at least one prior release manifest and its corresponding immutable image/revision. On a failed release verification, select that prior artifact, set its matching non-secret release identity and server-side secret/config references, restart only the isolated Preview runtime, and recheck `/health`. Do not copy, migrate, or restore Preview session SQLite: it is intentionally ephemeral. Do not roll back by rebuilding an unrecorded source revision.

## External gate

Executing CI on a remote service, publishing an image, configuring runtime secrets, creating a host, DNS, or enabling external access all require point-in-time Product Owner authorization. This repository contains no target-specific automation for those actions.
