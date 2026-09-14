#!/usr/bin/env bash
# Post-deployment WP-5B verifier. It never accepts an invite or Provider key.
# Run only after explicit authorization has enabled the HTTPS gateway.
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  verify_external_preview_gateway.sh --url https://preview.example.com [--http-url http://preview.example.com] [--public-ip 203.0.113.10]

The verifier checks only public, credential-free behavior. Invite login and one
bounded chat/stream are separate manual checks to avoid placing credentials in
shell history or CI output.
USAGE
}

url=""
http_url=""
public_ip=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --url) url=${2:?missing HTTPS URL}; shift 2 ;;
    --http-url) http_url=${2:?missing HTTP URL}; shift 2 ;;
    --public-ip) public_ip=${2:?missing public IP}; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done
[[ $url == https://* ]] || { echo "--url must use https://" >&2; exit 2; }

require_status() {
  local expected=$1 target=$2 actual
  actual=$(curl --silent --show-error --output /dev/null --write-out '%{http_code}' --max-time 20 "$target")
  [[ $actual == "$expected" ]] || { echo "Expected $expected from $target, got $actual" >&2; exit 1; }
  echo "$target -> $actual"
}

health=$(curl --silent --show-error --fail --max-time 20 "$url/health")
python3 -c '
import json, sys
payload = json.load(sys.stdin)
required = ("status", "commit", "release_id", "runtime_mode")
missing = [key for key in required if not payload.get(key)]
if payload.get("status") != "ok" or payload.get("runtime_mode") != "preview" or missing:
    raise SystemExit(f"unexpected health payload fields: {missing}")
print("health: status=ok, runtime_mode=preview, immutable identity present")
' <<<"$health"

require_status 200 "$url/"
require_status 404 "$url/docs"
require_status 404 "$url/openapi.json"
require_status 401 "$url/api/conversations"

if [[ -n $http_url ]]; then
  redirect=$(curl --silent --show-error --output /dev/null --write-out '%{http_code}' --max-time 20 "$http_url")
  [[ $redirect == 308 ]] || { echo "Expected HTTP 308 redirect, got $redirect" >&2; exit 1; }
  echo "$http_url -> 308"
fi

if [[ -n $public_ip ]]; then
  if curl --silent --show-error --connect-timeout 5 --max-time 8 "http://$public_ip:8000/health" >/dev/null; then
    echo "Port 8000 is externally reachable; abort invited Preview." >&2
    exit 1
  fi
  echo "public port 8000: not reachable"
fi

echo "Gateway checks passed. Perform invite/session and one bounded SSE test manually without placing credentials in shell history."
