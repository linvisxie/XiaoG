# XiaoG Web Preview WP-4 Local Plan

Activation: `XIAOG-AUTOPILOT-WEB-PREVIEW-WP4-2026-09-14-V1`.

1. Define a no-network release gate that verifies a full Git revision, working-tree consistency, tracked-file secret hygiene, Python compilation, frontend syntax, core regression, Preview smoke, and explicit WP-3 access/streaming tests.
2. Generate a deterministic local release manifest only after that gate succeeds. Its Preview identity is `xiaog-preview-<full-git-revision>`.
3. Make the container contract require and label the full source revision, without baking any secret or runtime `XIAOG_RELEASE_ID` into the image.
4. Record future deployment, health verification, and rollback requirements without choosing or creating any external service.
5. Run the complete local simulation and all affected checks. Docker build is conditional on local Docker availability; no substitute result may be claimed when it is unavailable.
6. Deliver a candidate, STATUS, and WP-4 Handoff at `HANDOFF_REQUIRED`.

No external action is part of this plan.
