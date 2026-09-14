#!/usr/bin/env bash
# Read-only operator audit for WP-5B. It intentionally never prints values
# from Docker Config.Env, mounted files, cookies, or Provider configuration.
set -euo pipefail

container=${1:-xiaog-preview}
command -v docker >/dev/null || { echo "docker is required." >&2; exit 1; }

echo "== container =="
docker inspect --format 'name={{.Name}} image={{.Config.Image}} running={{.State.Running}}' "$container"

echo "== published ports =="
docker inspect --format '{{range $port, $bindings := .NetworkSettings.Ports}}{{printf "%s -> " $port}}{{range $bindings}}{{printf "%s:%s " .HostIp .HostPort}}{{end}}{{println}}{{end}}' "$container"

echo "== mount destinations (paths only) =="
docker inspect --format '{{range .Mounts}}{{printf "%s -> %s rw=%t\n" .Source .Destination .RW}}{{end}}' "$container"

echo "== sensitive environment field names only =="
docker inspect "$container" | python3 -c '
import json, sys
items = json.load(sys.stdin)[0].get("Config", {}).get("Env", [])
names = {item.partition("=")[0] for item in items}
for name in ("DEEPSEEK_API_KEY", "XIAOG_PREVIEW_INVITES"):
    print(f"{name}=present" if name in names else f"{name}=absent")
'

echo "== host listeners requiring operator review =="
if command -v ss >/dev/null; then ss -ltn; else netstat -ltn; fi

echo "Audit complete. Compare health and release identity through the private operator path; do not print secret-bearing configuration."
