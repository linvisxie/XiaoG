# XiaoG Web Preview Readiness Audit — WP-0

Date: 2026-09-13 Asia/Shanghai
Activation: `XIAOG-AUTOPILOT-WEB-PREVIEW-READINESS-2026-09-13-V1`
Scope: read-only architecture/readiness audit; no product implementation, deployment, external account, secret, or real Provider action.

## Executive conclusion

XiaoG is portable enough to run a **single isolated FastAPI Preview service** on a conventional Linux VM/container when its persistent paths are isolated, but it is **not safe as-is for a shared persistent invited-user deployment**. The current runtime is a local single-user application: it has no authentication, no user/session ownership, and one SQLite database containing global Conversations, Settings, Memories, model usage, and file-artifact metadata.

For Preview v1, an isolated **ephemeral/stateless invited demo** is materially safer than enabling shared persistence. A persistent invited-user Preview requires an explicit identity/ownership boundary and therefore architectural work; it is not a configuration-only deployment.

No hosting vendor is selected. No deployment was started.

## Audit provenance and limits

### Start reality

- Expected branch and HEAD matched: `main` / `effb57b66d084ce76bda9cdd198395ab8041a12b`.
- Expected Engineering Foundation product baseline remains `ffdfe3de10c87e50afc3d69017b1deaf7e883029`.
- The expected clean tree differed only by two untracked Product Owner-provided governance documents: `XiaoG_Roadmap_Addendum_Public_Preview_v1_2026-09-13.md` and `XiaoG_Autopilot_Activation_Web_Preview_Readiness_v1_2026-09-13.md`. There were no uncommitted product-code changes. This did not affect safe audit conclusions.
- The prior STATUS correctly recorded the accepted non-blocking default-Edge generation-time navigation Known Issue. Its root cause remains unknown; synthetic success is not treated as a resolution.

### Audit actions performed

- Read the Core Protocol, complete Master Roadmap v2, Public Preview Addendum, Web Preview Activation, STATUS, and Engineering Foundation Handoff.
- Inspected entrypoints, FastAPI routes, frontend asset serving, providers, App Server manager, SQLite migrations/services, filesystem references, dependency manifest, Windows scripts, and secret boundaries.
- Ran local deterministic checks only: `run_core_tests.py` (34 passed), Python compilation, and frontend `node --check`.

### Explicitly not performed

- No deployment, tunnel, public bind, account creation, GitHub login/remote/push, host selection, DNS, cloud resource, or external secret action.
- No real Provider/API request, real browser Preview exercise, runtime restart, database mutation, database copy, or database content export.
- No product behavior, schema, migration, or configuration change.

## Source evidence index

| Subject | Evidence inspected |
|---|---|
| Local entry and Windows launch | `main.py`, `run_windows.bat`, `setup_windows.bat` |
| FastAPI/static/SSE/API surface | `backend/main.py` (lifespan, `/static`, `/`, `/health`, conversation/settings routes, chat `StreamingResponse`) |
| Runtime paths and secrets | `backend/config.py`, `.env.example`, `.gitignore` |
| SQLite and migrations | `backend/database/db.py`, `backend/database/models.py`, `backend/services/conversation_service.py`, `backend/services/memory_service.py` |
| Providers and Terra process | `backend/providers/deepseek.py`, `backend/providers/terra.py`, `backend/providers/codex_app_server.py`, `backend/services/codex_app_server_manager.py`, `backend/router/model_router.py` |
| Files, backups, permissions, logs | `backend/services/artifact_service.py`, `backend/services/backup_service.py`, `backend/permissions.py`, `backend/diagnostics.py` |
| Browser state and API use | `frontend/index.html`, `frontend/app.js` |
| Dependency/release evidence | `requirements.txt`, `run_core_tests.py`, `product_info.json`, local Git history/status |
## A. Runtime topology

| Area | Current evidence | Preview implication |
|---|---|---|
| Process entry | `main.py` calls Uvicorn with `backend.main:app`, host `127.0.0.1`, port `8000`; `run_windows.bat` launches the same local-only command. | The current launch contract is intentionally loopback/Windows-local. A Preview needs a separate release launcher/topology; do not expose this local launcher. |
| HTTP framework | `backend/main.py` defines one FastAPI app, mounts `frontend/` at `/static`, and serves `frontend/index.html` at `/`. | Static assets and API share one origin; no separate frontend build/deploy pipeline exists. |
| Startup/shutdown | The FastAPI lifespan configures local logging, applies additive SQLite migrations, then attempts to start the Codex App Server; shutdown closes that child process. | Startup needs a writable isolated log/database location. Preview health should not depend on Terra being available because boot catches its `ProviderError`. |
| Streaming | `POST /api/conversations/{id}/chat` returns `StreamingResponse` using SSE, `Cache-Control: no-cache`, and `X-Accel-Buffering: no`. DeepSeek upstream read timeout is 180 seconds. | The host/proxy must support response streaming without buffering and permit long-lived HTTP responses/idle windows. WebSocket support is not required by current code. |
| Frontend | Vanilla HTML/CSS/JavaScript; browser calls same-origin relative `/api/...` URLs. `frontend/index.html` loads static versioned scripts. | No Node build is required at runtime. The preview must preserve asset cache versioning on product static-resource changes. |
| Background/local bridge | `CodexAppServerManager` starts one `codex app-server` child process via stdio. Its one operation lock leases the connection for an entire Terra streamed turn. | Terra is globally serialized per backend process and depends on an installed, authenticated official Codex CLI. It is a material hosting/runtime constraint, not a browser credential path. |

### Loopback, port, and Windows assumptions

- `main.py` and `run_windows.bat` hard-code loopback port 8000; the batch launcher uses Windows `cmd`, PowerShell, `start`, `pause`, and `.venv\\Scripts\\python.exe`.
- `setup_windows.bat` is Windows-only provisioning, not a Linux deployment bootstrap.
- Core Python code uses `pathlib` and standard Python/ASGI dependencies, so it has no demonstrated Windows-only code blocker for a basic DeepSeek-only Linux service.
- There is no container manifest, Linux service definition, release artifact, lockfile, or deployment-specific runtime configuration.

## B. Deployment portability

### Conventional Linux container/VM assessment

A basic FastAPI/SQLite service can plausibly run on Linux by invoking Uvicorn directly: requirements are FastAPI, Uvicorn, HTTPX, and python-dotenv. This is a portability observation only; no Linux runtime was created or tested in WP-0.

Exact blockers or prerequisites:

1. The current RuntimeConfig hard-codes project-relative `data/xiaog.db` and `data/logs`; it has no environment override for an isolated Preview database, data directory, or log directory.
2. Current scripts are Windows launch/install scripts. A Linux/container launch contract and reproducible dependency lock/build definition are absent.
3. Terra requires the `codex` executable on PATH, an officially authenticated server-side CLI context, a writable/compatible runtime environment, and one long-lived child process. It cannot be assumed available or appropriate on a Preview host without a separate authorized architecture decision.
4. SQLite requires one isolated writable persistent volume if persistence is enabled. Horizontal scaling/multiple replicas against one local SQLite file is not a supported topology.
5. The app currently binds loopback. A hosted service can keep backend loopback behind a same-host proxy, or needs a controlled bind configuration; neither behavior is deployment-configurable today.

## C. Data ownership and multi-user safety

### Current persistence

`backend/config.py` resolves the database to `D:\\XiaoG\\data\\xiaog.db` in this local checkout. `backend/database/db.py` opens that one SQLite path and applies four additive migrations:

- `001_core_schema`
- `002_conversation_lifecycle`
- `003_personalization_defaults`
- `004_file_artifact_lifecycle`

Data ownership today is application-global:

| Data | Current owner/scope | Preview consequence |
|---|---|---|
| Conversations, messages, usage | A single SQLite database; Conversation has no user/session/tenant identifier. | Any client able to call the API can list, open, rename, archive, restore, or delete another user's Conversations. |
| Settings and personalization | Global key/value settings. | One user can read/change system prompt, profile, appearance, defaults, and preferences for all users. |
| Memories | Global SQLite records and a global service. | No per-user privacy boundary. |
| Model/reasoning preferences | Conversation-scoped and Conversation x Model-scoped, with global system defaults. | Correct local feature scoping, but not user/tenant isolation. |
| Terra thread IDs/sync markers | Stored on Conversations in the shared database. | Without ownership enforcement, another client can access a Conversation associated with an existing Terra thread. |
| File artifacts | Metadata-only lifecycle records; no upload/download API or file bytes exist. | Metadata has no user owner; true file persistence must remain disabled until identity/storage boundaries are designed. |
| Backups | Local backup service can export/import all XiaoG-owned tables, but it is not exposed as an API route. | Keep unavailable to Preview clients; any future exposure needs strict admin-only control. |

### Concurrent browser behavior

- Browser UI state is per browser tab, but server data is shared globally.
- DeepSeek creates an HTTP client per stream and has no Preview-wide request quota or concurrency limiter.
- Terra serializes complete turns through the one App Server manager lock. This avoids interleaved stdio JSON-RPC, but makes all Preview Terra users contend for one global process.
- SQLite uses a new connection per service operation. It provides local persistence, not tenant isolation or a multi-replica coordination model.

### Preview v1 persistence decision

An ephemeral/stateless demo is materially safer: it can avoid retaining user history, global settings, memory, usage, and artifacts after a session/request window. It still needs an explicit product/runtime mode to prevent writes and disable destructive/history-bearing surfaces; that is a bounded future design task, not an existing switch.

Persistent invited-user Preview is **architectural work**: identity/session issuance, API authorization, ownership columns/queries for all user data, migration/backward compatibility, per-user settings/memory semantics, and isolated artifact storage need an approved design. A shared database plus an invite URL is not an acceptable substitute.

## D. Secret and provider boundary

- DeepSeek secret loading is server-side only: `.env` is loaded by `backend/config.py`; `DEEPSEEK_API_KEY` is read into `ProviderSecrets`; `DeepSeekProvider` constructs its Authorization header inside the backend.
- `.env`, virtual environments, local SQLite, logs, and local backups are ignored by Git. `.env.example` contains placeholders only.
- Public configuration summaries and Registry/provider endpoints are designed to expose credential type/configuration summary, not secret values. Core regression covers configuration-summary and log redaction behavior.
- The frontend has no API-key loading path and uses relative API requests only.
- Terra delegates authentication to the local official Codex CLI/App Server. XiaoG does not read/store its authentication material; the Preview must not attempt to copy browser profiles, cookies, or user credentials.

Required future deployment boundary:

- Put only provider secrets needed by the selected Preview provider(s) into the selected host's server-side secret store at the separately authorized external-service gate.
- Keep secrets out of build artifacts, browser assets, API responses, diagnostic traces, repository history, and application logs.
- Treat Terra hosting/authentication as a separate provider-readiness decision. It is not approved by WP-0.

No secret value was printed, copied, or exported during this audit.

## E. Streaming, network, and concurrency requirements

A selected host topology must provide:

1. Same-origin HTTPS termination and reverse-proxy routing for FastAPI/static assets.
2. SSE pass-through with buffering disabled, chunk flushing preserved, and response/request timeout limits compatible with a 180-second upstream read window.
3. A single durable process when Terra is enabled, or a deliberately different officially supported Terra architecture. One shared stdio App Server is not horizontally scalable as written.
4. Per-invite/request rate limits, maximum concurrent generations, request-body limits, timeout/cancellation behavior, and provider budget controls before external access.
5. Health/readiness checks that do not invoke a paid Provider. Current `/health` is suitable as a basic non-provider process check.

Current code has no WebSocket dependency, no browser-provider direct connection, no general server-side job queue, and no externally managed background worker.

## F. Files, artifacts, and local filesystem

- Writable local filesystem paths are `data/xiaog.db` and `data/logs/xiaog.log`; `data/backups/` is ignored and reserved for local backups.
- Artifact lifecycle currently persists metadata only. There is no upload endpoint, file-byte storage, object-store integration, project implementation, or file download route.
- Avatar values can be stored as bounded data URLs in global personalization settings; this is not a user-isolated media design.
- Preview v1 should leave file upload, backup/import/export, artifact byte storage, project assets, and diagnostic/admin data unavailable until corresponding isolation and authorization designs exist.

## G. Security, abuse, and cost

### Current public-exposure blockers

The FastAPI API has no authentication/authorization middleware. Routes directly expose shared data and destructive state transitions, including Conversation list/read/write/delete, global settings reads/writes, archive/trash operations, search, provider status, and chat. FastAPI is constructed without disabling its standard schema/docs defaults, so `/docs`, `/redoc`, and `/openapi.json` also need a Preview policy (disable or protect).

No current code provides invite control, rate limiting, request quotas, concurrent-generation budget, provider-spend budget, CAPTCHA/abuse control, audit identity, or per-user deletion/retention policy.

### Minimum boundary before invited use

- Authenticated invite access at the edge or application boundary, covering every API and static route that exposes product state.
- A server-derived user/session identity passed to data authorization logic; never accept user identity only from untrusted client payload.
- Strict per-invite rate/concurrency quotas and an operator-set provider spending cap/alert threshold.
- Protected or disabled API docs, diagnostics, backup/import/export, and any future administrative endpoints.
- HTTPS, secret-store isolation, log redaction, bounded request/stream timeouts, and a removal/expiry procedure for invitations.

## H. Release engineering and rollback

### Current state

Local Git is the only source-control mechanism. No remote is configured, GitHub CLI is absent, and no CI/deployment workflow exists. The deterministic release gate is `run_core_tests.py`; current closeout evidence is 34 passed. Frontend cache-busting is implemented through versioned static query strings and must remain a release rule.

### Required controlled release flow

1. A Tech Lead-approved, explicitly releasable commit is selected from source control.
2. Deterministic core regression, Python/frontend syntax checks, secret scan, and a future deployment smoke pass are recorded against that immutable revision.
3. A build artifact/image is created from that revision and deployed only into an isolated Preview environment; local edits never deploy directly.
4. The Preview exposes version/commit identity and a non-provider `/health` readiness endpoint.
5. Rollback selects the prior immutable artifact/revision. If persistent data is enabled later, backup/restore and forward-only migration compatibility must be designed before first release; current migrations have no formal downgrade mechanism.

Minimum future deployment smoke: verify HTTPS/same-origin `GET /`, static asset delivery, `/health`, authentication gate, and a deterministic fake-Provider SSE path through the production proxy. Do not use a paid Provider merely to prove deployment streaming.

## I. Bounded topology options (no vendor selected)

| Rank | Option | Product-code change | Isolation and persistence | Streaming / provider fit | Maintenance | Assessment |
|---|---|---|---|---|---|---|
| 1 | One isolated Preview service behind an invite-aware edge/gateway, with ephemeral application data and server-side provider secret(s). | Small-to-moderate: explicit Preview/demo persistence policy and disabling unavailable/destructive surfaces; release/runtime configuration. | Strong separation from local development; no shared user history retained. | SSE-compatible host/proxy required. DeepSeek can be server-side. Terra remains an explicit separate decision. | Lowest of safe options. | Best first decision for a handful of feedback users if ephemeral behavior is acceptable. |
| 2 | One isolated Preview service with a dedicated persistent volume/database and an invite/auth boundary. | Architectural: identity, ownership checks, per-user Settings/Memory/Conversation semantics, migrations, retention, and authorization coverage. | Isolated from local development, but only safe after multi-user data design. | SSE-compatible; one replica/serialized write model unless storage architecture changes. | Moderate and ongoing. | Appropriate only if invited persistence is a product requirement. Not WP-1 configuration work. |
| 3 | Per-invite isolated ephemeral runtime/database behind a central authenticated gateway. | Significant provisioning/session-routing work; may avoid shared-table tenancy. | Strongest data separation and simple deletion of each sandbox. | Each runtime needs SSE support; Terra operational complexity multiplies. | Highest. | Useful only if strong per-user isolation is required before a shared-data model is designed. |

## Risk matrix

| Classification | WP-0 finding | Required disposition |
|---|---|---|
| Safe as-is | FastAPI serves same-origin static assets and API; DeepSeek credentials stay backend-side; additive migration history, redacted diagnostics, deterministic core regression, and `/health` exist. | Reuse only within a separately isolated Preview environment. |
| Requires configuration only | Server-side secret injection for a selected provider, isolated working directory/volume, log destination, HTTPS/proxy SSE settings, immutable release revision, and a bounded one-process runtime. | Decide after external-service authorization; do not use the local `.env`, database, or process. |
| Requires small code/release-engineering change | Environment-configurable runtime data paths/bind settings; Linux/container launcher/build definition; Preview/demo persistence policy; deployment smoke; public docs policy; release identity/rollback metadata. | Scope as a future WP-1 Activation after Tech Lead decision. |
| Requires architectural work | Persistent multi-user invited Preview: authentication, user/session identity, data ownership/authorization, per-user Settings/Memory/Conversation policy, storage/retention, audit and abuse controls. | Do not enable persistent multi-user data until designed and approved. |
| Must remain unavailable in Preview v1 | Direct local-machine tunnel, local development database/files/process, unauthenticated shared API, user-visible backup/import/export, real file upload/storage, Remote Control/G-BRIDGE exposure, cloud secret copying, and unapproved Terra hosting/authentication. | Keep absent/blocked. |

## Recommended next decision — not implementation

Tech Lead and Product Owner should decide one product question before any external authorization:

> Is an ephemeral invited feedback Preview acceptable for v1, or is persistent per-invited-user Conversation/Settings/Memory a requirement?

If ephemeral Preview is acceptable, authorize a narrow future WP-1 Activation to define an immutable source-control/release baseline, Preview runtime configuration, and a safe non-persistent mode. If persistence is required, first authorize a dedicated architecture/design window for identity and data ownership; do not begin deployment work.

A second explicit decision is whether Preview v1 must include Terra. If yes, Tech Lead must first approve an officially supported server-side Codex App Server authentication/operations model. It must not reuse Product Owner browser/profile credentials or the local development App Server.

## Required continuity

The non-blocking Known Issue remains:

> Generation-time navigation may delay in the Product Owner's real default Edge runtime; root cause is unknown and synthetic passes do not dismiss it.

This audit does not change that issue's status.

## WP-0 stop gate

WP-0 deliverable is complete. This audit recommends a decision only; it does not authorize WP-1, GitHub, hosting, deployment, provider calls, Dual-Codex, DeepSeek Registry maintenance, Phase 5.5, Phase 6+, or Workers.

`AUTOPILOT_SCOPE_COMPLETE`

`HANDOFF_TO_TECH_LEAD_REQUIRED`