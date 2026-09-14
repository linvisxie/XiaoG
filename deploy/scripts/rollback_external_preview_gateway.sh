#!/usr/bin/env bash
# Restore a saved Nginx configuration after a failed WP-5B gateway check.
# The default is a dry run. This script neither changes XiaoG nor handles
# secrets, DNS, certificates, security groups, or firewall rules.
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  rollback_external_preview_gateway.sh --backup <known-good-nginx-conf> --target <active-nginx-conf> [--apply]

Without --apply, prints the rollback plan only. The backup must be created by
the operator before gateway installation and contain no secret material.
USAGE
}

backup=""
target=""
apply=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --backup) backup=${2:?missing backup}; shift 2 ;;
    --target) target=${2:?missing target}; shift 2 ;;
    --apply) apply=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done
[[ -r $backup && -n $target ]] || { echo "Readable backup and target are required." >&2; exit 2; }

echo "Rollback target: $target"
echo "Known-good backup: $backup"
if [[ $apply != true ]]; then
  echo "Dry run only. Re-run with --apply after operator authorization."
  exit 0
fi
command -v nginx >/dev/null || { echo "nginx is required." >&2; exit 1; }
install -m 0644 "$backup" "$target"
nginx -t
systemctl reload nginx
echo "Nginx configuration restored. Verify external port 8000 remains closed and then recheck private XiaoG health."
