#!/usr/bin/env bash
# Render the no-secret WP-5B Nginx template. This script does not install,
# reload, or expose anything.
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  render_nginx_preview_gateway.sh --host <preview-domain> --certificate <absolute-cert-path> --key <absolute-key-path> --output <file>

All arguments are paths or a public hostname only. Do not pass invite or Provider credentials.
USAGE
}

host=""
certificate=""
key=""
output=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --host) host=${2:?missing hostname}; shift 2 ;;
    --certificate) certificate=${2:?missing certificate path}; shift 2 ;;
    --key) key=${2:?missing key path}; shift 2 ;;
    --output) output=${2:?missing output path}; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ $host =~ ^[A-Za-z0-9.-]+$ && $host != *..* && $host != .* && $host != *. ]] || { echo "Invalid hostname." >&2; exit 2; }
[[ $certificate == /* && $key == /* && -n $output ]] || { echo "Certificate/key must be absolute paths and output is required." >&2; exit 2; }

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
template="$root/deploy/nginx/xiaog-preview.conf.template"
tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT

sed \
  -e "s|__XIAOG_PUBLIC_HOST__|$host|g" \
  -e "s|__TLS_CERTIFICATE_PATH__|$certificate|g" \
  -e "s|__TLS_PRIVATE_KEY_PATH__|$key|g" \
  "$template" > "$tmp"
if grep -q '__[A-Z_]*__' "$tmp"; then
  echo "Template placeholders remain; refusing to write output." >&2
  exit 1
fi
install -D -m 0644 "$tmp" "$output"
echo "Rendered Nginx configuration: $output"
