# XiaoG Web Preview WP-5B Handoff

State: `HANDOFF_REQUIRED`  
Authority record: Product Owner WP-5B External Preview Access engineering task; no separate formal WP-5B Activation ID was supplied.

## Scope completed locally

The accepted topology remains fixed:

```text
Internet -> HTTPS :443 -> Nginx on ECS -> 127.0.0.1:8000 -> xiaog-preview
```

The local gateway-preparation candidate is
`6276ca66be4d51c8e559f437269c8cf2a283fc40`. It contains no XiaoG backend,
frontend, database-schema, Provider-architecture, secret, or deployed-image
change. The current manually verified ECS image remains
`7814fc0f57af9cd5db677d121b50d32437f81b73`.

## Delivered

- `deploy/nginx/xiaog-preview.conf.template` provides TLS termination, known-
  host routing, HTTP-to-HTTPS redirect, loopback-only upstream proxying,
  `X-Forwarded-*` forwarding, stripped incoming Authorization headers,
  rate-limited invite exchange, SSE buffering disabled, long streaming
  timeouts, and a redacted Nginx access-log format.
- `deploy/scripts/render_nginx_preview_gateway.sh` renders the template from a
  hostname and certificate/key paths only; it neither installs nor reloads
  Nginx.
- `deploy/scripts/audit_xiaog_preview_gateway.sh` is a read-only container/
  listener/mount audit that prints sensitive environment *field names* only.
- `deploy/scripts/verify_external_preview_gateway.sh` checks public,
  credential-free HTTPS health, redirect, docs closure, unauthenticated API
  rejection, and optional public TCP 8000 closure. Invite/SSE use remains a
  manual operator check so credentials never enter shell history or CI output.
- `deploy/scripts/rollback_external_preview_gateway.sh` defaults to a dry run
  and can restore an operator-created known-good Nginx configuration only with
  `--apply`.
- `deploy/WEB_PREVIEW_WP5B_EXTERNAL_GATEWAY.md` is the operator contract,
  acceptance checklist, and rollback guide.
- `tests/test_external_preview_gateway_contract.py` adds three deterministic,
  no-network checks for loopback proxying, HTTPS redirect/rate limit, SSE
  buffering/timeouts, log redaction, closed public TCP 8000, and Terra policy.

## XiaoG compatibility conclusion

No application code change was required. XiaoG already uses same-origin API
paths, sends Preview cookies as Secure/HttpOnly/SameSite=Lax with finite expiry,
and produces SSE responses with `X-Accel-Buffering: no`. Nginx owns the public
host boundary and forwards Host plus `X-Forwarded-*` metadata. XiaoG currently
does not make authorization decisions from these forwarded headers.

## Local verification

On clean candidate `6276ca66be4d51c8e559f437269c8cf2a283fc40`:

```text
.\.venv\Scripts\python.exe tools\ci\wp4_release_gate.py --revision HEAD
```

Passed: 50 core tests with no failures/errors/skips, Preview release smoke,
the 7-test WP-3 access/streaming suite, Python compilation, frontend Node
syntax, Git consistency checks, secret scan, and the three WP-5B static gateway
contract tests.

Docker, Nginx, and Bash are unavailable on this workstation. Therefore no local
container check, `nginx -t`, or shell-script syntax execution is claimed. Those
are explicit ECS operator checks before any gateway activation.

## External stop gate and minimum operator actions

No ECS, Nginx runtime, public IP/EIP, security-group, DNS, certificate, secret,
Provider, or tester-invitation action was performed in this window.

Before inviting any external tester, a new point-in-time authorization must
cover only the following minimum actions:

1. rotate the DeepSeek key recorded as compromised before any further Provider
   use;
2. select a named domain, issue/deploy its TLS certificate, and retain the
   certificate paths outside the repository;
3. confirm the ECS public endpoint/EIP and security group allow only public
   TCP 443 (optional TCP 80 redirect), while public TCP 8000 remains denied and
   SSH stays restricted to named operator addresses;
4. install/test/reload the rendered Nginx configuration and retain the
   previous Nginx configuration for rollback;
5. execute the no-secret verifier, then manually validate one revocable invite,
   session isolation, and bounded SSE generation; and
6. distribute only the minimal approved invite set.

No public product release, open registration, Terra integration, or automatic
next phase is authorized.

`AUTOPILOT_HANDOFF_READY`
