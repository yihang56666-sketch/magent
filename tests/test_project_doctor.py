#!/usr/bin/env python3
"""Regression tests for the project readiness doctor."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from doctor import check_generated_artifacts, check_required_paths, human_size  # noqa: E402


def test_human_size_formats_megabytes():
    assert human_size(5 * 1024 * 1024) == "5.0 MB"


def test_check_required_paths_reports_missing_files(tmp_path: Path):
    checks = check_required_paths(tmp_path)
    missing = {check["name"] for check in checks if not check["ok"]}

    assert "README.md" in missing
    assert "tests" in missing


def test_check_generated_artifacts_warns_for_large_binary(tmp_path: Path):
    artifact = tmp_path / ".agents" / "magent.exe"
    artifact.parent.mkdir()
    artifact.write_bytes(b"x" * 2048)

    checks = check_generated_artifacts(tmp_path, large_threshold=1024)

    assert checks[0]["name"] == ".agents/magent.exe"
    assert not checks[0]["ok"]
