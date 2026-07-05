#!/usr/bin/env python3
"""Practical workflow recipes for common Magent jobs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RECIPES_DIR = ROOT / "recipes"
REQUIRED_FIELDS = {
    "id",
    "title",
    "summary",
    "default_scope",
    "default_max",
    "task_template",
    "context",
    "outcome",
    "next_steps",
}


class RecipeError(ValueError):
    """Raised when a recipe is missing or malformed."""


def _validate_recipe(recipe: dict[str, Any], path: Path) -> dict[str, Any]:
    missing = sorted(REQUIRED_FIELDS - set(recipe))
    if missing:
        raise RecipeError(f"{path.name} missing fields: {', '.join(missing)}")
    if recipe["id"] != path.stem:
        raise RecipeError(f"{path.name} id must match filename stem")
    if not isinstance(recipe["next_steps"], list) or not all(isinstance(item, str) for item in recipe["next_steps"]):
        raise RecipeError(f"{path.name} next_steps must be a list of strings")
    return recipe


def load_recipes(recipes_dir: Path = RECIPES_DIR) -> list[dict[str, Any]]:
    recipes = []
    for path in sorted(recipes_dir.glob("*.json")):
        recipe = json.loads(path.read_text(encoding="utf-8"))
        recipes.append(_validate_recipe(recipe, path))
    return recipes


def get_recipe(recipe_id: str, recipes_dir: Path = RECIPES_DIR) -> dict[str, Any]:
    for recipe in load_recipes(recipes_dir):
        if recipe["id"] == recipe_id:
            return recipe
    available = ", ".join(recipe["id"] for recipe in load_recipes(recipes_dir))
    raise RecipeError(f"Unknown recipe '{recipe_id}'. Available recipes: {available}")


def render_recipe_task(recipe: dict[str, Any], user_task: str, scope: str) -> str:
    task_detail = user_task.strip() or "No extra task detail provided"
    return recipe["task_template"].format(task=task_detail, scope=scope)


def render_recipe_context(recipe: dict[str, Any], user_context: str) -> str:
    parts = [recipe["context"], f"Recipe outcome: {recipe['outcome']}"]
    if user_context.strip():
        parts.append(f"User context: {user_context.strip()}")
    return "\n".join(parts)


def format_recipe_list(recipes: list[dict[str, Any]]) -> str:
    lines = ["Practical recipes", "=" * 17]
    for recipe in recipes:
        lines.extend(
            [
                f"- {recipe['id']}: {recipe['title']}",
                f"  {recipe['summary']}",
                f"  Outcome: {recipe['outcome']}",
                f"  Start: python .agents\\magent.py start {recipe['id']} --scope \"{recipe['default_scope']}\" --task \"...\"",
            ]
        )
    return "\n".join(lines)


def format_recipe_detail(recipe: dict[str, Any]) -> str:
    lines = [
        f"{recipe['title']} ({recipe['id']})",
        "=" * (len(recipe["title"]) + len(recipe["id"]) + 3),
        recipe["summary"],
        "",
        f"Default scope: {recipe['default_scope']}",
        f"Default agents: {recipe['default_max']}",
        f"Outcome: {recipe['outcome']}",
        "",
        "Next steps:",
    ]
    lines.extend(f"- {step}" for step in recipe["next_steps"])
    lines.extend(
        [
            "",
            "Example:",
            f"python .agents\\magent.py start {recipe['id']} --scope \"{recipe['default_scope']}\" --task \"...\"",
        ]
    )
    return "\n".join(lines)
