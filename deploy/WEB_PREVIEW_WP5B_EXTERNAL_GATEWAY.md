# WP-5B External Preview Gateway Contract

This is a deployment-preparation contract for a small invited Preview. It is
not authorization to alter ECS, DNS, certificates, secrets, security groups,
or external access.

## Fixed topology

```text
Internet
  -> HTTPS :443 / Nginx on ECS
  -> 127.0.0.1:8000 / xiaog-preview container :8000
```

The XiaoG container must remain bound only through the ECS loopback publish.
Do not publish TCP 8000 to the Internet. Nginx is the sole Internet-facing
component and proxies to `127.0.0.1:8000`.

## Runtime compatibility confirmed in source

- Browser API calls are same-origin relative paths, so no cross-origin policy is
  needed for the fixed topology.
- Preview session cookies are `Secure`, `HttpOnly`, `SameSite=Lax`, finite, and
  server-issued.
- XiaoG chat responses use `text/event-stream` and send
  `X-Accel-Buffering: no`; the Nginx template also disables proxy buffering and
  permits long read/send timeouts.
- The Preview startup policy continues to require the DeepSeek-only allowlist;
  Terra is not started or routed in Preview mode.

## Operator prerequisites requiring explicit external authorization

1. Rotate the DeepSeek key recorded as compromised before any external Provider
   use. Never add its value to this repository, Docker Config.Env, Nginx, shell
   history, evidence, or logs.
2. Select a controlled public hostname and obtain a valid TLS certificate.
3. Confirm an ECS public endpoint/EIP as needed for the selected hostname.
4. Change the ECS security group only to allow inbound TCP 443. TCP 80 is
   optional and may only redirect to HTTPS. TCP 8000 stays closed publicly.
   Restrict SSH to named operator addresses.
5. Preserve the immutable application image revision and release identity;
   record the Nginx configuration backup before activation.

## Prepare, install, validate, and roll back

1. Render `deploy/nginx/xiaog-preview.conf.template` with
   `deploy/scripts/render_nginx_preview_gateway.sh`. The template needs only a
   hostname and certificate/key *paths*, never secret values.
2. Obtain the TLS certificate before installing the TLS site configuration.
   DNS validation is preferred because it does not require an interim public
   HTTP listener. The operator disables the distribution's conflicting default Nginx site,
   reviews the generated file, and runs `nginx -t` before reload. The template
   intentionally owns the default HTTP/HTTPS vhosts so unknown `Host` headers
   are rejected rather than proxied. Install it only after the security group
   and certificate authorization.
3. Run `deploy/scripts/audit_xiaog_preview_gateway.sh` before and after the
   change. It prints mount paths and sensitive field names only, never values.
4. Run `deploy/scripts/verify_external_preview_gateway.sh` after authorization
   to verify HTTPS, health identity, docs closure, unauthenticated rejection,
   redirect behavior, and external TCP 8000 closure. Invite login and bounded
   streaming are deliberately manual to avoid credentials in command output.
5. If verification fails, use
   `deploy/scripts/rollback_external_preview_gateway.sh` with the known-good
   Nginx backup. Restore the prior Nginx configuration before considering any
   XiaoG image change. Preview session data is ephemeral and is never restored.
   If this is the first XiaoG Nginx site and no prior site file exists, use the
   explicit `--remove-target` rollback mode instead.

## Logging and header rules

The template's access log records only remote address, status, HTTP method,
path without query string, response size, and timing. It excludes cookies,
authorization, request bodies, query strings, and referers. Nginx explicitly
sets the upstream host and `X-Forwarded-*` headers, while stripping an incoming
`Authorization` header. The upstream is still private; client-controlled
forwarded headers do not create an application authentication path.

## External Preview acceptance checklist

- HTTPS reaches the expected hostname and presents the expected certificate.
- `/health` reports `status=ok`, `runtime_mode=preview`, matching commit, and
  matching release ID.
- `/`, authenticated invite/session access, conversation creation, and one
  bounded SSE chat response succeed.
- `/docs` and `/openapi.json` remain closed; unauthenticated API calls return
  401.
- A probe to public TCP 8000 fails.
- Terra remains unavailable/not routed; no open registration exists.
- Access/error logs and operational evidence contain no credential, cookie,
  authorization header, or invite value.

## Stop gate

This repository preparation stops before external resource changes. A human
operator with explicit Product Owner authorization must perform ECS, Nginx
installation/reload, certificate, DNS, security-group, secret-rotation, and
tester-invitation actions. Re-run the release gate before selecting a new
immutable release for deployment.
