# WP-5B Deployment Readiness Checklist

State vocabulary: **READY** = repository/local evidence is complete; **BLOCKED** = must not proceed; **NEEDS HUMAN ACTION** = external operator authorization and evidence are required.

## Immutable release and runtime

| Status | Item | Evidence / required action |
| --- | --- | --- |
| READY | Local gateway-preparation commit | `6276ca66be4d51c8e559f437269c8cf2a283fc40`; strict release gate passed. |
| READY | Deployed XiaoG image identity | Product Owner evidence: `7814fc0f57af9cd5db677d121b50d32437f81b73`, matching health commit/release ID. |
| READY | Preview policy | Invite-only, ephemeral/session-isolated, DeepSeek-only; Terra unavailable/not routed; OpenAPI closed. |
| READY | Gateway preparation | Nginx template, safe logging, render/audit/verify/rollback scripts, activation runbook, and static contract tests exist. |
| NEEDS HUMAN ACTION | ECS runtime recheck | Run the read-only audit and private `/health` check immediately before activation. |

## Security and secrets

| Status | Item | Evidence / required action |
| --- | --- | --- |
| BLOCKED | Compromised DeepSeek key | The manually exposed key must be rotated and revoked before any further Provider use. No value is recorded here. |
| NEEDS HUMAN ACTION | Protected server-side configuration | Confirm only the read-only `/run/xiaog-preview/app.env -> /app/.env` path supplies the new key/invites; Docker Config.Env must not contain either field. |
| NEEDS HUMAN ACTION | Minimal revocable invite set | Create and retain only approved invite identities; distribute nothing until acceptance succeeds. |
| READY | Public port policy in template | Nginx proxies only to `127.0.0.1:8000`; template does not publish application TCP 8000. |

## Cloud gateway

| Status | Item | Evidence / required action |
| --- | --- | --- |
| NEEDS HUMAN ACTION | Public endpoint/EIP | Confirm the exact ECS public address for the approved hostname. |
| NEEDS HUMAN ACTION | DNS | Create the single approved hostname record. |
| NEEDS HUMAN ACTION | TLS certificate | Issue/validate certificate, preferably DNS-validated before Nginx installation. |
| NEEDS HUMAN ACTION | Security group | Public TCP 443 only; optional TCP 80 redirect; deny public TCP 8000; SSH restricted. |
| NEEDS HUMAN ACTION | Nginx installation | Install Nginx, disable conflicting default site, render configuration, run `nginx -t`, then reload. |
| BLOCKED | Nginx syntax/runtime evidence | Nginx and Bash are unavailable on the local workstation; ECS operator must supply `nginx -t` and redacted post-reload evidence. |

## Acceptance verification

| Status | Item | Evidence / required action |
| --- | --- | --- |
| READY | Credential-free verifier | Script checks HTTPS health, HTTP redirect, docs closure, unauthenticated rejection, and optional public TCP 8000 closure. |
| NEEDS HUMAN ACTION | External network verification | Run the verifier from an external operator network after gateway activation. |
| NEEDS HUMAN ACTION | Browser invite/session test | Verify login/logout and two-invite isolation using separate browser sessions. |
| NEEDS HUMAN ACTION | Bounded SSE test | Authorize and verify exactly the approved bounded DeepSeek stream after key rotation. |
| NEEDS HUMAN ACTION | Log review | Confirm Nginx/XiaoG logs and evidence contain no secret, invite, cookie, or Authorization value. |

## Stop condition

Do not invite external testers until every BLOCKED row is resolved and every
NEEDS HUMAN ACTION row has redacted evidence accepted by Tech Lead. This file
does not authorize deployment, secret operations, DNS, certificates, security
groups, public access, additional Provider calls, or Terra.
