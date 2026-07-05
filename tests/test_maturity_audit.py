#!/usr/bin/env python3
"""Regression tests for the maturity audit helpers."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import maturity_audit  # noqa: E402
from maturity_audit import check_file, check_forbidden_legacy_paths, maturity_level, run_captured  # noqa: E402


def test_check_file_reports_existing_required_file(tmp_path: Path):
    readme = tmp_path / "README.md"
    readme.write_text("# Project\n", encoding="utf-8")

    check = check_file(tmp_path, "README.md", "project overview")

    assert check["ok"]
    assert check["severity"] == "ok"


def test_check_file_reports_missing_file_as_blocker(tmp_path: Path):
    check = check_file(tmp_path, "README.md", "project overview")

    assert not check["ok"]
    assert check["severity"] == "blocker"


def test_maturity_level_accounts_for_warnings():
    assert maturity_level(blockers=1, warnings=0) == "not-ready"
    assert maturity_level(blockers=0, warnings=1) == "publishable-with-local-warnings"
    assert maturity_level(blockers=0, warnings=0) == "publishable"


def test_run_captured_forces_utf8_decoding(monkeypatch, tmp_path: Path):
    captured = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured.update(kwargs)
        return maturity_audit.subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(maturity_audit.subprocess, "run", fake_run)

    run_captured(tmp_path, ["git", "status"])

    assert captured["encoding"] == "utf-8"
    assert captured["errors"] == "replace"
    assert captured["text"] is True


def test_forbidden_legacy_paths_are_blockers(tmp_path: Path):
    legacy = tmp_path / ".agents" / "setup-openai-api.bat"
    legacy.parent.mkdir()
    legacy.write_text("@echo off\n", encoding="utf-8")

    check = check_forbidden_legacy_paths(tmp_path)

    assert not check["ok"]
    assert check["severity"] == "blocker"
