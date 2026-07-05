#!/usr/bin/env python3
"""Tests for Magent orchestration advice."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".agents" / "scripts"))

from advisor import build_advice, format_advice, match_recipe  # noqa: E402


def test_match_recipe_detects_bugfix():
    recipe = match_recipe("login returns 500 after reset", "src/auth tests/auth", "")

    assert recipe is not None
    assert recipe["id"] == "bugfix"


def test_match_recipe_uses_word_boundaries_for_short_keywords():
    recipe = match_recipe("production readiness check", ".", "")

    assert recipe is not None
    assert recipe["id"] == "release-readiness"


def test_advice_keeps_tiny_copy_edit_local():
    advice = build_advice("fix typo", "README.md", "", max_agents=4)

    assert advice["recommendation"] == "keep-local"
    assert advice["recipe"] is None
    assert advice["manual_overhead"]["agent_packets"] == 0
    assert "Handle this directly" in advice["suggested_command"]
    assert "manual orchestration likely costs more" in advice["reasons"][0]


def test_advice_recommends_recipe_for_risky_bug():
    advice = build_advice("login returns 500 after password reset", "src/auth tests/auth", "", max_agents=4)

    assert advice["recommendation"] == "use-recipe"
    assert advice["recipe"] == "bugfix"
    assert advice["manual_overhead"]["agent_packets"] > 0
    assert "start bugfix" in advice["suggested_command"]


def test_advice_clamps_max_agents_to_one():
    advice = build_advice("production readiness check", ".", "", max_agents=0)

    assert advice["recommendation"] == "use-recipe"
    assert advice["manual_overhead"]["agent_packets"] >= 1
    assert advice["manual_overhead"]["requires_sync"] is True
    assert advice["manual_overhead"]["requires_merge"] is True


def test_format_advice_shows_overhead_and_reason():
    advice = build_advice("prepare v1 release", ".", "", max_agents=3)

    output = format_advice(advice)

    assert "Magent advice" in output
    assert "Estimated overhead:" in output
    assert "Suggested next command:" in output
