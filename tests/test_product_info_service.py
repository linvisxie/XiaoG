"""Deterministic revision-identity coverage for ProductInfoService."""

from __future__ import annotations

import asyncio
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend import main as api
from backend.services.product_info_service import ProductInfoService, product_info_service


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

    def test_public_info_reads_metadata_file_and_adds_runtime_revision(self) -> None:
        metadata = {
            "name": "XiaoG",
            "version": "test-version",
            "phase": "test-phase",
            "models": ["test-model"],
            "capabilities": ["test-capability"],
            "limitations": ["test-limitation"],
            "changelog": [{"version": "test-version", "title": "test", "items": ["item"]}],
        }
        self.service.path.write_text(json.dumps(metadata), encoding="utf-8")
        with patch.object(self.service, "_git_commit", return_value="c" * 40):
            info = self.service.public_info()

        self.assertEqual({key: info[key] for key in metadata}, metadata)
        self.assertEqual(info["commit"], "c" * 40)

    def test_about_and_health_share_current_product_metadata(self) -> None:
        expected = product_info_service.public_info()
        about = asyncio.run(api.about())
        health = asyncio.run(api.health())

        self.assertEqual(about, expected)
        self.assertEqual(health["version"], expected["version"])
        self.assertEqual(health["phase"], expected["phase"])
        self.assertEqual(health["commit"], expected["commit"])
        self.assertEqual(expected["version"], "0.4.4")
        self.assertEqual(expected["changelog"][0]["version"], expected["version"])
        self.assertIn("WP-5B Engineering Complete", expected["phase"])


if __name__ == "__main__":
    unittest.main()
