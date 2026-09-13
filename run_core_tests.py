"""Run XiaoG's deterministic core regression suite from the repository root."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest


def main() -> int:
    root = Path(__file__).resolve().parent
    suite = unittest.defaultTestLoader.discover(str(root / "tests"), pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    print(
        f"XiaoG core regression: {result.testsRun} run, "
        f"{len(result.failures)} failures, {len(result.errors)} errors, "
        f"{len(result.skipped)} skipped."
    )
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())