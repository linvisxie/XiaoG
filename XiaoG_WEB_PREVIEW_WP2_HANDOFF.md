# XiaoG Web Preview WP-2 Handoff

Activation: `XIAOG-AUTOPILOT-WEB-PREVIEW-WP2-2026-09-14-V1`  
State: `HANDOFF_REQUIRED`

## Delivered

- Added a Linux/container release contract: Python 3.12 Dockerfile, non-root runtime user, isolated writable Preview data/log paths, `.dockerignore`, and placeholder-only Preview environment example.
- Preview startup now fails closed when server-side `DEEPSEEK_API_KEY` is missing; it never prints a value. A supplied value is only configured/unverified until a separately authorized real Provider request.
- Documented same-origin HTTPS, forwarded-header, request-size, 180-second SSE/no-buffer, health, immutable release identity, and rollback requirements.
- Added deterministic ASGI Preview release smoke. It runs with a non-real local placeholder, proves root/static/health/release identity/session creation and closed `/docs`, `/redoc`, `/openapi.json`, and makes no Provider request.
- Corrected diagnostics redaction formatting so non-string library log arguments retain their format types.

## Verification

- `python tests/preview_release_smoke.py`: passed.
- `python run_core_tests.py`: 37 passed.
- Python compilation, Node syntax checks, and `git diff --check`: passed.
- Docker is not installed locally, so no image build occurred. No external action occurred.

## Remaining blockers / required next authorization

WP-3 still needs an approved invited-access/auth boundary and rate, concurrency, cost, and abuse controls. External deployment additionally requires point-in-time Product Owner authorization for GitHub/remote/push, hosting, DNS, external secret injection, and external access. Terra remains disabled pending its separate readiness/authentication audit.

`AUTOPILOT_HANDOFF_READY`
