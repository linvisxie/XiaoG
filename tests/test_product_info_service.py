"""Deterministic revision-identity coverage for ProductInfoService."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.services.product_info_service import ProductInfoService


class ProductInfoServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.service = ProductInfoService(Path(self.temporary.name) / "product_info.json")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_valid_container_source_revision_bypasses_git(self) -> None:
        revision = "a" * 40
        with patch.dict(os.environ, {"XIAOG_SOURCE_REVISION": revision}), patch(
            "backend.services.product_info_service.subprocess.run"
        ) as git_run:
            self.assertEqual(self.service._git_commit(), revision)
        git_run.assert_not_called()

    def test_invalid_container_source_revision_falls_back_to_git(self) -> None:
        with patch.dict(os.environ, {"XIAOG_SOURCE_REVISION": "A" * 40}), patch(
            "backend.services.product_info_service.subprocess.run"
        ) as git_run:
            git_run.return_value.stdout = "b" * 40 + "\n"
            self.assertEqual(self.service._git_commit(), "b" * 40)
        git_run.assert_called_once()

    def test_absent_container_source_revision_keeps_git_failure_behavior(self) -> None:
        with patch.dict(os.environ, {}, clear=True), patch(
            "backend.services.product_info_service.subprocess.run", side_effect=OSError
        ):
            self.assertEqual(self.service._git_commit(), "unavailable")


if __name__ == "__main__":
    unittest.main()
