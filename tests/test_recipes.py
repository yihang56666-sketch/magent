#!/usr/bin/env python3
"""Tests for practical workflow recipes."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".agents" / "scripts"))

from recipes import (  # noqa: E402
    RecipeError,
    format_recipe_detail,
    format_recipe_list,
    get_recipe,
    load_recipes,
    render_recipe_context,
    render_recipe_task,
)


def test_load_recipes_finds_practical_workflows():
    recipes = load_recipes()
    ids = {recipe["id"] for recipe in recipes}

    assert {"bugfix", "code-review", "release-readiness", "docs-polish", "test-plan"} <= ids


def test_render_recipe_task_includes_user_task_and_scope():
    recipe = get_recipe("bugfix")

    task = render_recipe_task(recipe, "login returns 500", "src/auth tests/auth")

    assert "login returns 500" in task
    assert "src/auth tests/auth" in task
    assert "root cause" in task.lower()


def test_render_recipe_context_includes_outcome_and_user_context():
    recipe = get_recipe("release-readiness")

    context = render_recipe_context(recipe, "shipping v1.0")

    assert recipe["outcome"] in context
    assert "shipping v1.0" in context


def test_format_recipe_list_shows_start_command():
    output = format_recipe_list([get_recipe("docs-polish")])

    assert "docs-polish" in output
    assert "python .agents\\magent.py start docs-polish" in output


def test_format_recipe_detail_shows_next_steps():
    output = format_recipe_detail(get_recipe("test-plan"))

    assert "Test Plan" in output
    assert "Next steps:" in output


def test_get_recipe_reports_available_ids_for_unknown_recipe():
    try:
        get_recipe("unknown")
    except RecipeError as exc:
        assert "Available recipes" in str(exc)
        assert "bugfix" in str(exc)
    else:
        raise AssertionError("Expected RecipeError")


def test_malformed_recipe_is_rejected(tmp_path: Path):
    (tmp_path / "broken.json").write_text(json.dumps({"id": "broken"}), encoding="utf-8")

    try:
        load_recipes(tmp_path)
    except RecipeError as exc:
        assert "missing fields" in str(exc)
    else:
        raise AssertionError("Expected RecipeError")
