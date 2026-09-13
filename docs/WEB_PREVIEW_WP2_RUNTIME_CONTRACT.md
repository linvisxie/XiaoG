# XiaoG Preview Runtime Contract (WP-2)

This is a local release contract, not deployment authorization.

## Required environment

`XIAOG_RUNTIME_MODE=preview`, `XIAOG_DATA_DIR`, and `XIAOG_RELEASE_ID` are mandatory. `DEEPSEEK_API_KEY` must be injected by the eventual host's server-side secret mechanism; it is never a browser value, image layer value, Git value, or log value. Startup fails closed when it is absent. A supplied value is only **configured**, not validated; invalidity can only be established by a later authorized provider request and must remain redacted.

`XIAOG_DATA_DIR` and `XIAOG_LOG_DIR` must be Preview-owned writable locations. Preview refuses the repository's local `data/` directory, creates per-session transient databases below `preview-sessions/`, and removes them on Preview startup. It never imports local backups or user data.

## Linux/container contract

Use Python 3.12 with `requirements.txt`, or build the supplied Dockerfile. Run as a non-root user with writable Preview data/log locations. The process command is `python main.py`; the bind address and port come from `XIAOG_HOST` and `XIAOG_PORT`. The image intentionally has no secret value or release ID baked in.

## Proxy, HTTPS, and SSE contract

A future authorized edge must terminate HTTPS, route frontend and `/api` on one origin, preserve `Cache-Control: no-cache` and `X-Accel-Buffering: no` for SSE, disable response buffering, and allow an upstream response/idle window of at least 180 seconds. It must set a bounded request-body limit and either strip client-supplied forwarded headers or configure the application server to trust them only from the known proxy. WebSockets are not required. `/health` is the non-provider readiness endpoint; it reports commit, runtime mode, and release identity.

## Release and rollback contract

Build only from an immutable Git commit after deterministic regression, syntax checks, Preview release smoke, secret scan/redaction checks, and a future authorized deployment smoke. Set `XIAOG_RELEASE_ID` to that immutable release identity. Roll back by selecting the previous immutable artifact/revision and its matching environment contract; Preview state is intentionally ephemeral, so no database rollback is involved.

## Remaining boundary

WP-2 does not grant hosting, DNS, GitHub, external secret entry, public/invited access, rate/cost controls, or Terra server-side operation. Those remain future authorization gates.
