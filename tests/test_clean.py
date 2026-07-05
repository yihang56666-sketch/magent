#!/usr/bin/env python3
"""Regression tests for generated artifact cleanup."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from clean import existing_targets, remove_target, resolve_inside_root  # noqa: E402


def test_existing_targets_includes_large_local_artifacts(tmp_path: Path):
    artifact = tmp_path / ".agents" / "dist"
    artifact.mkdir(parents=True)

    targets = existing_targets(tmp_path)

    assert artifact.resolve() in targets


def test_existing_targets_preserves_run_keep_files(tmp_path: Path):
    runs = tmp_path / ".agents" / "reports" / "runs"
    runs.mkdir(parents=True)
    keep = runs / ".keep"
    keep.write_text("", encoding="utf-8")
    run = runs / "20260705-000000-1"
    run.mkdir()

    targets = existing_targets(tmp_path, include_runs=True)

    assert run.resolve() in targets
    assert keep.resolve() not in targets


def test_resolve_inside_root_rejects_parent_escape(tmp_path: Path):
    try:
        resolve_inside_root(tmp_path, "../outside")
    except ValueError as exc:
        assert "outside project root" in str(exc)
    else:
        raise AssertionError("Expected ValueError for parent path escape")


def test_remove_target_deletes_files_and_directories(tmp_path: Path):
    file_target = tmp_path / "file.tmp"
    file_target.write_text("x", encoding="utf-8")
    dir_target = tmp_path / "dir"
    dir_target.mkdir()

    remove_target(file_target)
    remove_target(dir_target)

    assert not file_target.exists()
    assert not dir_target.exists()
