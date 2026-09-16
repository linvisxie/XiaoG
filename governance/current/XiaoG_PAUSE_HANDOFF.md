# XiaoG Pause Handoff

State: `HANDOFF_REQUIRED`  
Maintenance mode: **PAUSED — no external Preview deployment is active**

## Current project stage

WP-5B Engineering is complete. The project is paused immediately before
**WP-5B External Deployment Activation**. This is a maintenance pause to avoid
unnecessary cloud-resource consumption; it is not a cancellation or a change
to the accepted Preview architecture.

## Provenance at pause

- Branch: `main`
- Governance HEAD: `937bf45d81a45b3e8c0f41a760cf64ee22fb1c6d`
- Working tree at pause preparation: clean
- Local WP-5B deployment-activation candidate:
  `0b2314577b767df35ba638fd3eb15b8663161c41`
- Existing manually verified ECS Preview image:
  `7814fc0f57af9cd5db677d121b50d32437f81b73`
- ECS container: `xiaog-preview`; application binding remains
  `127.0.0.1:8000 -> 8000`.

## Completed

- WP-5A private ECS Preview verification was recorded: Preview mode,
  invite/session flow, DeepSeek routing, and one bounded streaming generation
  were manually verified; Terra remained unavailable/not routed.
- The Preview service remains loopback-only; application TCP 8000 has not been
  prepared for direct public exposure.
- WP-5B produced the Nginx HTTPS-to-loopback gateway template, safe logging
  contract, render/audit/verify/rollback scripts, deterministic gateway
  contract tests, activation runbook, and deployment readiness checklist.
- The strict local release gate passed on the WP-5B activation package.

## Not completed

- The DeepSeek key exposed during manual troubleshooting has not yet been
  rotated and must be treated as compromised.
- No Nginx gateway has been installed or reloaded on ECS.
- No public endpoint/EIP confirmation, DNS record, TLS certificate, or
  security-group change has been made for External Preview.
- No external tester invite has been distributed and no external Preview
  acceptance verification has occurred.
- No Preview closeout, Master Roadmap v3 integration, formal GitHub follow-up,
  or Controlled Dual-Codex work has started.

## Pause reason

External Preview deployment is temporarily paused to reduce cloud-resource
consumption. Do not delete files, remove the local environment, alter the
existing deployment, or perform cloud cleanup as part of this pause.

## Recovery entry

Resume through `XiaoG_MAIN_CODEX_ENTRY.md`, then read:

1. `governance/current/XiaoG_AUTOPILOT_STATUS.md`;
2. this pause handoff;
3. `governance/current/XiaoG_WEB_PREVIEW_WP5B_HANDOFF.md`;
4. `governance/current/WP5B_DEPLOYMENT_READINESS_CHECKLIST.md`; and
5. `deploy/WP5B_EXTERNAL_PREVIEW_ACTIVATION_RUNBOOK.md`.

Run provenance before acting: branch, HEAD, tracked/untracked working tree,
relevant log, remote, and the private ECS runtime/health identity. Git and
runtime evidence override this handoff if they differ.

## Recovery point and required order

Recovery point: **WP-5B External Deployment Activation**.

Resume only with the necessary point-in-time Product Owner/Tech Lead external
authorization, in this order:

1. DeepSeek key rotation.
2. ECS recovery and private runtime/health/revision verification.
3. DNS, TLS, and security-group actions.
4. Nginx deployment, configuration validation, and rollback-point retention.
5. External Preview verification.
6. Preview closeout.
7. Master Roadmap v3 integration.
8. Formal GitHub follow-up/integration.
9. 16GB Controlled Dual-Codex.

Until separately authorized, do not modify the backend, frontend, database,
Provider architecture, or deployment architecture. The pause does not grant
permission to push, perform cloud operations, rotate/inject secrets, expose
the service, change DNS/TLS/security groups, distribute invites, or make
Provider calls.

`AUTOPILOT_HANDOFF_READY`
