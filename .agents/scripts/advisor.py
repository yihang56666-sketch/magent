#!/usr/bin/env python3
"""Advise whether a task is worth a Magent multi-agent run."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

from recipes import get_recipe


ROOT = Path(__file__).resolve().parents[1]
ROUTER_DIR = ROOT / "skills" / "codex-agent-identity-bank" / "scripts"
if str(ROUTER_DIR) not in sys.path:
    sys.path.insert(0, str(ROUTER_DIR))

from route_identity import all_skills, route  # noqa: E402


RECIPE_KEYWORDS = {
    "bugfix": ("bug", "fix", "failing", "failure", "error", "crash", "broken", "regression", "500"),
    "code-review": ("review", "merge", "pull request", "pr", "diff", "change", "patch"),
    "release-readiness": ("release", "readiness", "production", "ship", "publish", "tag", "launch", "v1", "version"),
    "docs-polish": ("docs", "documentation", "readme", "onboarding", "guide", "tutorial"),
    "test-plan": ("test", "coverage", "qa", "verification", "validate", "plan"),
}

HIGH_VALUE_SIGNALS = (
    "auth",
    "security",
    "payment",
    "migration",
    "refactor",
    "release",
    "production",
    "bug",
    "failing",
    "regression",
    "performance",
    "architecture",
    "cross-module",
    "tests",
)

LOW_VALUE_SIGNALS = (
    "typo",
    "format",
    "formatting",
    "rename",
    "comment",
    "single line",
    "one line",
    "small copy",
)


def normalize(text: str) -> str:
    return " ".join(text.casefold().split())


def scope_items(scope: str) -> list[str]:
    return [item for item in re.split(r"[\s,;]+", scope.strip()) if item]


def keyword_matches(keyword: str, normalized_text: str) -> bool:
    normalized_keyword = normalize(keyword)
    if " " in normalized_keyword:
        return normalized_keyword in normalized_text
    if all(ord(char) < 128 for char in normalized_keyword):
        return re.search(rf"(?<![a-z0-9]){re.escape(normalized_keyword)}(?![a-z0-9])", normalized_text) is not None
    return normalized_keyword in normalized_text


def match_recipe(task: str, scope: str, context: str) -> dict[str, Any] | None:
    text = normalize(" ".join([task, scope, context]))
    scores = []
    for recipe_id, keywords in RECIPE_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword_matches(keyword, text))
        if score:
            scores.append((score, recipe_id))
    if not scores:
        return None
    scores.sort(key=lambda item: (-item[0], item[1]))
    return get_recipe(scores[0][1])


def is_low_overhead_task(task: str, scope: str, context: str) -> bool:
    text = normalize(" ".join([task, scope, context]))
    if any(signal in text for signal in HIGH_VALUE_SIGNALS):
        return False
    has_low_value_signal = any(signal in text for signal in LOW_VALUE_SIGNALS)
    return has_low_value_signal or (len(text.split()) <= 10 and len(scope_items(scope)) <= 1)


def reasons_for(
    task: str,
    scope: str,
    context: str,
    recipe: dict[str, Any] | None,
    agent_count: int,
    low_overhead: bool,
) -> list[str]:
    text = normalize(" ".join([task, scope, context]))
    reasons = []
    if low_overhead:
        return ["Task looks small or low-risk; manual orchestration likely costs more than it saves."]
    if recipe:
        reasons.append(f"Matches the `{recipe['id']}` recipe: {recipe['summary']}")
    if any(signal in text for signal in HIGH_VALUE_SIGNALS):
        reasons.append("Contains risk signals where independent review can catch missed issues.")
    if len(scope_items(scope)) > 2:
        reasons.append("Scope spans multiple paths, so specialist perspectives may reduce blind spots.")
    if agent_count >= 3:
        reasons.append(f"Router selected {agent_count} identities, which indicates cross-functional work.")
    if not reasons:
        reasons.append("No strong multi-agent signal found; manual orchestration may cost more than it saves.")
    return reasons


def recommendation_for(low_overhead: bool, recipe: dict[str, Any] | None) -> str:
    if low_overhead:
        return "keep-local"
    if recipe:
        return "use-recipe"
    return "orchestrate"


def suggested_command(recommendation: str, recipe: dict[str, Any] | None, task: str, scope: str, context: str, max_agents: int) -> str:
    escaped_task = task.replace('"', "'")
    escaped_scope = scope.replace('"', "'")
    escaped_context = context.replace('"', "'")
    if recommendation == "keep-local":
        return "Handle this directly in the current Codex session; use `magent advise` again if scope grows."
    if recommendation == "use-recipe" and recipe:
        command = f'python .agents\\magent.py start {recipe["id"]} --scope "{escaped_scope}" --task "{escaped_task}"'
    else:
        command = f'python .agents\\magent.py run --scope "{escaped_scope}" --task "{escaped_task}" --max {max_agents}'
    if escaped_context:
        command += f' --context "{escaped_context}"'
    return command


def build_advice(task: str, scope: str = ".", context: str = "", max_agents: int = 4) -> dict[str, Any]:
    max_agents = max(1, max_agents)
    selected, pattern = route(task=task, scope=scope, context=context, max_identities=max_agents, include_skills=set())
    low_overhead = is_low_overhead_task(task, scope, context)
    recipe = None if low_overhead else match_recipe(task, scope, context)
    recommendation = recommendation_for(low_overhead, recipe)
    identities = [identity["id"] for identity in selected]
    agent_count = 0 if recommendation == "keep-local" else len(identities)
    return {
        "recommendation": recommendation,
        "recipe": recipe["id"] if recipe and recommendation == "use-recipe" else None,
        "pattern": pattern if recommendation != "keep-local" else "none",
        "identities": identities if recommendation != "keep-local" else [],
        "skills": all_skills(selected) if recommendation != "keep-local" else [],
        "manual_overhead": {
            "agent_packets": agent_count,
            "output_files": agent_count,
            "requires_sync": recommendation != "keep-local",
            "requires_merge": recommendation != "keep-local",
        },
        "reasons": reasons_for(task, scope, context, recipe, len(identities), low_overhead),
        "suggested_command": suggested_command(recommendation, recipe, task, scope, context, max_agents),
    }


def format_advice(advice: dict[str, Any]) -> str:
    lines = [
        "Magent advice",
        "=============",
        f"Recommendation: {advice['recommendation']}",
    ]
    if advice.get("recipe"):
        lines.append(f"Recipe: {advice['recipe']}")
    lines.extend(
        [
            f"Pattern: {advice['pattern']}",
            f"Identities: {', '.join(advice['identities']) if advice['identities'] else 'none'}",
            "",
            "Why:",
        ]
    )
    lines.extend(f"- {reason}" for reason in advice["reasons"])
    overhead = advice["manual_overhead"]
    lines.extend(
        [
            "",
            "Estimated overhead:",
            f"- Agent packets: {overhead['agent_packets']}",
            f"- Output files: {overhead['output_files']}",
            f"- Sync needed: {str(overhead['requires_sync']).lower()}",
            f"- Merge needed: {str(overhead['requires_merge']).lower()}",
            "",
            "Suggested next command:",
            advice["suggested_command"],
        ]
    )
    return "\n".join(lines)


def advice_json(advice: dict[str, Any]) -> str:
    return json.dumps(advice, ensure_ascii=False, indent=2)
