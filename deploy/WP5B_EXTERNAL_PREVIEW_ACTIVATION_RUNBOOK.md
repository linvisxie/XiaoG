# XiaoG WP-5B External Preview Activation Runbook

**State:** Preparation only. This runbook authorizes nothing by itself.  
**Fixed topology:** `Internet -> HTTPS :443 -> Nginx on ECS -> 127.0.0.1:8000 -> xiaog-preview`.

Run every command below only after the named Product Owner authorization covers
the associated cloud, secret, or external-access action. Never put an invite
credential or Provider key in a command line, shell history, Git checkout,
Nginx configuration, Docker Config.Env, CI output, or evidence bundle.

## 1. Deployment preflight

The operator must record redacted command output only.

1. Confirm the running container and immutable image identity:

   ```text
   bash deploy/scripts/audit_xiaog_preview_gateway.sh xiaog-preview
   ```

   Require container name `xiaog-preview`, loopback-only host publication for
   application port 8000, and a read-only mount to `/app/.env`. The audit prints
   sensitive field names only, never their values.

2. Through the existing private operator path, require `/health` to report:

   ```text
   status=ok
   runtime_mode=preview
   commit=7814fc0f57af9cd5db677d121b50d32437f81b73
   release_id=xiaog-preview-7814fc0f57af9cd5db677d121b50d32437f81b73
   ```

3. Confirm the Preview policy remains invite-only, ephemeral/session-isolated,
   DeepSeek-only, and Terra unavailable/not routed. Confirm `/docs` and
   `/openapi.json` are closed over the private path.

4. Treat the DeepSeek key used during manual troubleshooting as compromised.
   Do not continue to an external activation until a separately authorized
   server-side key rotation has completed and the old key is revoked.

5. Preserve the current container invocation, non-secret mounts, port mapping,
   immutable image reference, and `/health` evidence as the rollback baseline.

## 2. Cloud-resource actions — human authorization required

These are manual cloud actions. Do not infer completion from this repository.

| Action | Required result |
| --- | --- |
| DeepSeek key rotation | New key is written only to the protected host-side `/run/xiaog-preview/app.env`; old key is revoked; value is never recorded. |
| Minimal invite set | Create only Product Owner-approved, revocable invite identities in the same protected file; do not distribute them until acceptance succeeds. |
| Public endpoint | Confirm or allocate the ECS public IP/EIP to be used by the named Preview hostname. |
| DNS | Create the exact record for the approved hostname. No wildcard or unrelated records. |
| TLS certificate | Issue a certificate for that hostname. Prefer DNS validation before installing Nginx; retain key/cert outside the repository. |
| Security group | Allow public TCP 443 only. TCP 80 is optional and only redirects to HTTPS. Deny public TCP 8000. Restrict SSH to named operator source addresses. |

## 3. ECS Nginx installation and configuration

1. Use the ECS operating system's supported package manager to install Nginx.
   This step changes ECS and requires authorization. Confirm the resulting
   binary with `nginx -v`; do not install unrelated web panels or agents.

2. From the approved repository checkout, render a candidate without secrets.
   Invoke scripts with `bash`; executable file permissions are not assumed.

   ```text
   bash deploy/scripts/render_nginx_preview_gateway.sh \
     --host <approved-preview-hostname> \
     --certificate <absolute-certificate-path> \
     --key <absolute-private-key-path> \
     --output /tmp/xiaog-preview.conf
   ```

3. Disable the distribution's conflicting default Nginx site before installing
   the template. The XiaoG template deliberately owns default HTTP/HTTPS
   virtual hosts and rejects unknown Host headers rather than proxying them.

4. Preserve a rollback copy of an existing XiaoG site file, if any. Install the
   rendered configuration at the distribution's approved include path, for
   example `/etc/nginx/conf.d/xiaog-preview.conf`. The target must be readable
   by Nginx but contain no secret value.

5. Validate before reload:

   ```text
   sudo nginx -t
   sudo systemctl reload nginx
   ```

   Abort on either failure. Do not change XiaoG image, database, Provider
   configuration, firewall, or application port to compensate for an Nginx
   error.

6. Confirm host listeners. Public 443 is expected only after the security-group
   authorization; XiaoG application port 8000 remains loopback-only.

## 4. Release verification after authorized activation

Run the credential-free verifier from an external operator-controlled network:

```text
bash deploy/scripts/verify_external_preview_gateway.sh \
  --url https://<approved-preview-hostname> \
  --http-url http://<approved-preview-hostname> \
  --public-ip <approved-ecs-public-ip>
```

Require all of the following:

- HTTPS `/` and `/health` succeed; health reports the expected immutable commit,
  release ID, and `runtime_mode=preview`.
- HTTP returns `308` to the approved HTTPS hostname.
- `/docs` and `/openapi.json` return `404`; unauthenticated
  `/api/conversations` returns `401`.
- A public probe to TCP 8000 fails.

Then, using only authorized browser-based manual verification and no terminal
credential arguments:

1. Test one approved invite login, authenticated session, conversation creation,
   a single bounded DeepSeek streaming response, and logout.
2. Test a second approved invite in a separate browser profile/session; it must
   not list, read, or alter the first invite's conversation data.
3. Confirm the UI/provider status leaves Terra unavailable and no open
   registration path exists.
4. Review redacted Nginx and XiaoG logs for absence of invite values, cookies,
   Authorization headers, and Provider key material.

## 5. Rollback

If any Nginx, HTTPS, authentication, isolation, SSE, or TCP-8000 check fails:

1. Stop invitations immediately; do not retry with broader network access.
2. Restore the saved site configuration:

   ```text
   bash deploy/scripts/rollback_external_preview_gateway.sh \
     --backup <known-good-nginx-conf> \
     --target <active-nginx-conf> --apply
   ```

   If this was the first XiaoG site file, use:

   ```text
   bash deploy/scripts/rollback_external_preview_gateway.sh \
     --remove-target <active-nginx-conf> --apply
   ```

3. Re-run `sudo nginx -t`, reload Nginx, and verify port 8000 remains private.
4. Restore the current private Preview baseline. Do not restore Preview session
   SQLite: it is intentionally ephemeral. Rotate the Provider key and revoke
   affected invite credentials if exposure is suspected.

## 6. Completion evidence

Record only: operator identity, timestamps, hostname, image revision, health
identity, certificate fingerprint/expiry, security-group rule identifiers,
redacted verifier output, session-isolation result, bounded-stream result, and
rollback readiness. Never record secret values, invite credentials, cookies,
raw configuration environments, or request Authorization headers.
