"""Deterministic, no-network WP-4 release gate for a committed XiaoG revision."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SHA1 = re.compile(r"^[0-9a-f]{40}$")
SENSITIVE_ENV_ASSIGNMENT = re.compile(
    r"^\s*(?:export\s+)?(?:DEEPSEEK_API_KEY|OPENAI_API_KEY|ANTHROPIC_API_KEY|GITHUB_TOKEN|GH_TOKEN|AWS_SECRET_ACCESS_KEY|AWS_SESSION_TOKEN|XIAOG_PREVIEW_INVITES)\s*=\s*(.*?)\s*$",
    re.IGNORECASE,
)
SENSITIVE_YAML_ASSIGNMENT = re.compile(
    r"^\s*(?:DEEPSEEK_API_KEY|OPENAI_API_KEY|ANTHROPIC_API_KEY|GITHUB_TOKEN|GH_TOKEN|AWS_SECRET_ACCESS_KEY|AWS_SESSION_TOKEN|XIAOG_PREVIEW_INVITES)\s*:\s*(.*?)\s*$",
    re.IGNORECASE,
)
SAFE_VALUE_MARKERS = ("<", "placeholder", "fake", "example", "your_", "replace", "changeme")


def run(*args: str, capture: bool = False) -> str:
    completed = subprocess.run(args, cwd=ROOT, text=True, capture_output=capture)
    if completed.returncode:
        raise RuntimeError(f"command failed ({completed.returncode}): {' '.join(args)}")
    return completed.stdout.strip() if capture else ""


def git(*args: str) -> str:
    return run("git", *args, capture=True)


def revision(value: str) -> str:
    resolved = git("rev-parse", "--verify", f"{value}^{{commit}}")
    if not SHA1.fullmatch(resolved):
        raise RuntimeError("release revision must resolve to a full SHA-1 commit identity")
    return resolved


def scan_tracked_files() -> None:
    tracked = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True).stdout
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", "-z"], cwd=ROOT, capture_output=True, check=True
    ).stdout
    findings: list[str] = []
    for encoded in set(tracked.split(b"\0") + untracked.split(b"\0")):
        if not encoded:
            continue
        relative = Path(encoded.decode("utf-8", "surrogateescape"))
        if relative.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".ico", ".zip", ".pdf"}:
            continue
        try:
            text = (ROOT / relative).read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(text.splitlines(), start=1):
            match = SENSITIVE_ENV_ASSIGNMENT.match(line)
            if relative.suffix.lower() in {".yaml", ".yml"}:
                match = match or SENSITIVE_YAML_ASSIGNMENT.match(line)
            if not match:
                continue
            value = match.group(1).strip().strip("\"'").casefold()
            if not value or any(marker in value for marker in SAFE_VALUE_MARKERS):
                continue
            findings.append(f"{relative}:{number}")
    if findings:
        raise RuntimeError("possible committed secret assignment(s): " + ", ".join(findings))


def write_manifest(revision_id: str, output: Path) -> None:
    payload = {
        "contract_version": 1,
        "source_revision": revision_id,
        "release_id": f"xiaog-preview-{revision_id}",
        "runtime_mode": "preview",
        "provider_policy": "deepseek-only; terra-disabled",
        "persistence": "ephemeral-session-isolated",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", default="HEAD", help="full Git commit or rev-parseable commit (default: HEAD)")
    parser.add_argument("--allow-dirty", action="store_true", help="local verification only; CI must not use this")
    parser.add_argument("--manifest", type=Path, help="write deterministic release manifest after all checks pass")
    args = parser.parse_args()
    try:
        release_revision = revision(args.revision)
        if not args.allow_dirty and git("status", "--porcelain"):
            raise RuntimeError("release gate requires a clean working tree")
        git("diff", "--check")
        git("diff", "--cached", "--check")
        scan_tracked_files()
        run(sys.executable, "-m", "compileall", "-q", "backend", "tests", "main.py", "run_core_tests.py", "tools/ci")
        for script in sorted((ROOT / "frontend").glob("*.js")):
            run("node", "--check", str(script))
        run(sys.executable, "run_core_tests.py")
        run(sys.executable, "tests/preview_release_smoke.py")
        run(sys.executable, "-m", "unittest", "tests.test_preview_access", "tests.test_preview_streaming")
        if args.manifest:
            write_manifest(release_revision, args.manifest.resolve())
        else:
            with tempfile.TemporaryDirectory() as temporary:
                write_manifest(release_revision, Path(temporary) / "release-manifest.json")
        print(f"WP-4 release gate passed: {release_revision} / xiaog-preview-{release_revision}")
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"WP-4 release gate failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
