# XiaoG Web Preview WP-5A Handoff

State: `HANDOFF_REQUIRED`  
Authority record: Product Owner-supplied manual ECS Preview verification evidence; no separate WP-5 Activation ID was supplied.

## Scope and immutable identity

- ECS host location: Alibaba Cloud ECS Hong Kong.
- Container: `xiaog-preview`.
- Image revision: `7814fc0f57af9cd5db677d121b50d32437f81b73`.
- Runtime mode: `preview`.
- Listener: localhost only, `127.0.0.1:8000 -> 8000`.
- Health evidence: `status=ok`, with matching `commit=7814fc0f57af9cd5db677d121b50d32437f81b73` and `release_id=xiaog-preview-7814fc0f57af9cd5db677d121b50d32437f81b73`.

## Manual verification evidence

The Product Owner reports that the following completed successfully on the immutable revision above:

- OpenAPI remained closed.
- Invite authentication, authenticated session access, and conversation creation succeeded.
- DeepSeek routing and one bounded streaming generation succeeded.
- Terra remained unavailable and was not routed.
- No public exposure, DNS, HTTPS, external invite distribution, or public release was performed.

Manual evidence remains on ECS under `/root/xiaog-evidence/`. This document does not copy that evidence or any secret value.

## Secret-loading boundary

- Secret loading was migrated from Docker environment variables to a read-only bind mount: host `/run/xiaog-preview/app.env` to container `/app/.env`.
- Docker Config.Env no longer contains `DEEPSEEK_API_KEY` or `XIAOG_PREVIEW_INVITES`.
- `/app/.env` is readable by the `xiaog` runtime user.

## Security closeout

A real DeepSeek API key was exposed during manual operator troubleshooting. Its value is not recorded here. Treat the key as compromised and rotate it before any further Provider use. Rotation is a separate secret operation and requires explicit authorization.

## Guardrails and next decision

This evidence does not authorize a further deployment, secret operation, Provider call, public exposure, DNS, HTTPS configuration, external invite distribution, or Terra integration. Tech Lead must review the WP-5A evidence and decide whether to authorize the minimum key-rotation operation. No subsequent phase starts automatically.

`AUTOPILOT_HANDOFF_READY`
