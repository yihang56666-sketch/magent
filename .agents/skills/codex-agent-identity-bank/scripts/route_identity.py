#!/usr/bin/env python3
"""Route a task to bounded specialist Codex identities and skills."""

from __future__ import annotations

import argparse
from functools import lru_cache
import json
import re
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
IDENTITIES_PATH = SKILL_DIR / "references" / "identities.json"


@lru_cache(maxsize=1)
def load_identities() -> dict:
    return json.loads(IDENTITIES_PATH.read_text(encoding="utf-8"))


def normalize(text: str) -> str:
    return " ".join(text.casefold().split())


def _normalized_terms(*terms: str) -> tuple[str, ...]:
    return tuple(normalize(term) for term in terms)


def _keyword_matches_normalized(keyword: str, normalized_text: str) -> bool:
    if " " in keyword:
        return keyword in normalized_text
    if all(ord(char) < 128 for char in keyword):
        return re.search(rf"(?<![a-z0-9]){re.escape(keyword)}(?![a-z0-9])", normalized_text) is not None
    return keyword in normalized_text


def keyword_matches(keyword: str, text: str) -> bool:
    return _keyword_matches_normalized(normalize(keyword), normalize(text))


def keyword_hit_count(text: str, keywords: tuple[str, ...]) -> int:
    normalized_text = normalize(text)
    return sum(1 for keyword in keywords if _keyword_matches_normalized(normalize(keyword), normalized_text))


def score_identity(identity: dict, text: str, include_skills: set[str]) -> int:
    normalized_text = normalize(text)
    score = 0
    for keyword in identity["keywords"]:
        normalized_keyword = normalize(keyword)
        if _keyword_matches_normalized(normalized_keyword, normalized_text):
            score += 3 if " " in normalized_keyword else 2
    for skill in identity["skills"]:
        if skill in include_skills:
            score += 5
    if identity["id"].replace("-", " ") in normalized_text:
        score += 6
    return score


WATCH_WORDS = _normalized_terms("watch", "observe", "monitor", "看着", "旁观", "观察")
ARCH_WORDS = _normalized_terms("architecture", "compare", "option", "tradeoff", "架构", "方案", "对比")
SOP_WORDS = _normalized_terms("migration", "roadmap", "large feature", "规划", "迁移", "大功能")
REVIEW_SUPPORT_WORDS = _normalized_terms(
    "auth",
    "security",
    "secret",
    "payment",
    "migration",
    "refactor",
    "failing",
    "bug",
    "optimize",
    "performance",
    "latency",
    "throughput",
    "benchmark",
)
TEST_WORDS = _normalized_terms("test", "failing", "regression", "测试", "失败")

AUTH_WORDS = _normalized_terms(
    "auth",
    "authentication",
    "login",
    "password",
    "session",
    "oauth",
    "jwt",
    "token",
    "permission",
)

DATABASE_WORDS = _normalized_terms(
    "database",
    "sql",
    "postgres",
    "mysql",
    "sqlite",
    "migration",
    "schema",
    "orm",
    "prisma",
)

STRONG_WRITE_WORDS = _normalized_terms(
    "implement",
    "fix",
    "change",
    "edit",
    "build",
    "create",
    "add",
    "repair",
    "optimize",
    "improve",
    "update",
    "cleanup",
    "clean up",
    "polish",
    "tune",
    "实现",
    "修复",
    "修改",
    "编辑",
    "创建",
    "新增",
    "重做",
    "优化",
    "改进",
    "更新",
    "清理",
    "调整",
)

MODERATE_WRITE_WORDS = _normalized_terms(
    "refactor",
    "redesign",
    "rewrite",
    "migrate",
    "migration",
    "重构",
    "重设计",
    "重写",
    "迁移",
    "改造",
)

READ_ONLY_WORDS = _normalized_terms(
    "review",
    "audit",
    "inspect",
    "analyze",
    "analyse",
    "compare",
    "plan",
    "evaluate",
    "investigate",
    "审查",
    "审阅",
    "检查",
    "分析",
    "比较",
    "规划",
    "评估",
    "调查",
)


def contains_any(normalized_text: str, terms: tuple[str, ...]) -> bool:
    return any(term in normalized_text for term in terms)


def matches_any_term(normalized_text: str, terms: tuple[str, ...]) -> bool:
    return any(_keyword_matches_normalized(term, normalized_text) for term in terms)


HARDWARE_IDENTITY_IDS = {"embedded-firmware-engineer", "hardware-bringup-engineer"}
HARDWARE_ANCHOR_WORDS = _normalized_terms(
    "embedded",
    "firmware",
    "mcu",
    "stm32",
    "rtos",
    "bootloader",
    "i2c",
    "spi",
    "uart",
    "can bus",
    "can-fd",
    "can id",
    "can frame",
    "dbc",
    "usb-can",
    "jlink",
    "j-link",
    "openocd",
    "keil",
    "gcc",
    "probe-rs",
    "probe",
    "board",
    "schematic",
    "oscilloscope",
    "logic analyzer",
    "power rail",
    "gpio",
    "swd",
    "jtag",
    "rtt",
    "swo",
    "peripheral",
    "reset line",
    "hardware",
)

PENTEST_IDENTITY_IDS = {"penetration-tester"}
PENTEST_ANCHOR_WORDS = _normalized_terms(
    "pentest",
    "penetration",
    "ethical hacking",
    "exploit",
    "vulnerability",
    "attack surface",
    "red team",
    "reconnaissance",
    "xss",
    "csrf",
    "injection",
    "ssrf",
    "rce",
    "wireless",
    "security test",
)


def identity_domain_applicable(identity: dict, normalized_text: str) -> bool:
    """Filter generic keyword collisions before ranking identities."""
    identity_id = identity["id"]
    if identity_id in HARDWARE_IDENTITY_IDS:
        return matches_any_term(normalized_text, HARDWARE_ANCHOR_WORDS)
    if identity_id in PENTEST_IDENTITY_IDS:
        return matches_any_term(normalized_text, PENTEST_ANCHOR_WORDS)
    return True


def infer_pattern(selected: list[dict], text: str) -> str:
    normalized_text = normalize(text)
    ids = {identity["id"] for identity in selected}
    if contains_any(normalized_text, WATCH_WORDS):
        return "stateful-observer"
    if contains_any(normalized_text, ARCH_WORDS):
        return "group-chat"
    if contains_any(normalized_text, SOP_WORDS):
        return "sop"
    if ids & {"qa-test-automation-engineer", "code-reviewer", "security-engineer"}:
        return "critic-loop"
    if len(selected) >= 3:
        return "supervisor"
    return "handoff"


def _replacement_index(selected: list[dict], text: str) -> int | None:
    if not selected:
        return None
    start = 1 if len(selected) > 1 else 0

    def replacement_key(item: tuple[int, dict]) -> tuple[int, int, int, int]:
        index, identity = item
        sourced = bool(identity.get("_source"))
        anchored = _anchor_present(identity, text)
        score = score_identity(identity, text, set())
        return (1 if sourced and not anchored else 0, 1 if sourced else 0, -score, index)

    return max(enumerate(selected[start:], start), key=replacement_key)[0]


def ensure_identity(selected: list[dict], identity_id: str, lookup: dict[str, dict], max_identities: int, text: str) -> list[dict]:
    if identity_id in {identity["id"] for identity in selected} or identity_id not in lookup:
        return selected
    if len(selected) < max_identities:
        selected.append(lookup[identity_id])
        return selected
    replacement = _replacement_index(selected, text)
    if replacement is not None:
        selected[replacement] = lookup[identity_id]
    return selected


def ensure_domain_support(selected: list[dict], text: str, identities: list[dict], max_identities: int) -> list[dict]:
    lookup = {identity["id"]: identity for identity in identities}
    if matches_any_term(text, AUTH_WORDS):
        selected = ensure_identity(selected, "backend-api-engineer", lookup, max_identities, text)
        selected = ensure_identity(selected, "security-engineer", lookup, max_identities, text)
    if matches_any_term(text, DATABASE_WORDS):
        selected = ensure_identity(selected, "database-engineer", lookup, max_identities, text)
    return selected


def ensure_review_support(selected: list[dict], text: str, identities: list[dict], max_identities: int) -> list[dict]:
    normalized_text = normalize(text)
    lookup = {identity["id"]: identity for identity in identities}

    if contains_any(normalized_text, REVIEW_SUPPORT_WORDS):
        selected = ensure_identity(selected, "code-reviewer", lookup, max_identities, text)
    if contains_any(normalized_text, TEST_WORDS):
        selected = ensure_identity(selected, "qa-test-automation-engineer", lookup, max_identities, text)
    return selected


def _anchor_present(identity: dict, normalized_text: str) -> bool:
    """True if the identity's primary domain token (leading id segment) is in text.

    Used only as a tie-breaker so a domain-specific role (e.g. rust-engineer for a
    Rust task) wins over peers that merely share generic keywords like 'async'/'web'.
    """
    token = identity["id"].split("-")[0]
    return _keyword_matches_normalized(normalize(token), normalized_text)


def route(task: str, scope: str, context: str, max_identities: int, include_skills: set[str]) -> tuple[list[dict], str]:
    data = load_identities()
    text = normalize(" ".join(part for part in [task, scope, context] if part))

    scored = []
    for identity in data["identities"]:
        if not identity_domain_applicable(identity, text):
            continue
        score = score_identity(identity, text, include_skills)
        if score:
            scored.append((score, identity["id"], identity))
    scored.sort(key=lambda item: (-item[0], 0 if _anchor_present(item[2], text) else 1, item[1]))

    selected = [identity for _, _, identity in scored[:max_identities]]
    if not selected:
        lookup = {identity["id"]: identity for identity in data["identities"]}
        fallback_ids = ["software-architect", "code-reviewer"]
        selected = [lookup[identity_id] for identity_id in fallback_ids if identity_id in lookup]

    selected = ensure_domain_support(selected, text, data["identities"], max_identities)
    selected = ensure_review_support(selected, text, data["identities"], max_identities)
    selected = selected[:max_identities]
    return selected, infer_pattern(selected, text)


def all_skills(selected: list[dict]) -> list[str]:
    skills = {"codex-multi-agent-orchestrator"}
    for identity in selected:
        skills.update(identity["skills"])
    return sorted(skills)


def task_requests_write(task: str, context: str) -> bool:
    text = normalize(f"{task} {context}")
    if contains_any(text, STRONG_WRITE_WORDS):
        return True
    return contains_any(text, MODERATE_WRITE_WORDS) and not contains_any(text, READ_ONLY_WORDS)


def agent_type_for(identity: dict, task: str, context: str, primary: bool) -> str:
    implementation_ids = {
        "embedded-firmware-engineer",
        "frontend-ui-engineer",
        "backend-api-engineer",
        "database-engineer",
        "devops-platform-engineer",
        "data-ml-engineer",
        "llm-agent-engineer",
        "mobile-engineer",
        "performance-engineer",
    }
    if primary and identity["id"] in implementation_ids and task_requests_write(task, context):
        return "worker"
    return "explorer"


def dispatch_plan(selected: list[dict], pattern: str, task: str, scope: str, context: str) -> list[dict]:
    plan = []
    for index, identity in enumerate(selected):
        primary = index == 0
        role = agent_type_for(identity, task, context, primary)
        plan.append(
            {
                "id": identity["id"],
                "identity_id": identity["id"],
                "title": identity["title"],
                "agent_type": role,
                "execution_role": role,
                "primary": primary,
                "pattern": pattern,
                "skills": identity["skills"],
                "prompt": render_identity_prompt(identity, task, scope, context),
            }
        )
    return plan


def render_identity_prompt(identity: dict, task: str, scope: str, context: str) -> str:
    skills = ", ".join(identity["skills"]) or "none"
    boundaries = "\n".join(f"- {item}" for item in identity["boundaries"])
    outputs = "\n".join(f"- {item}" for item in identity["output_focus"])
    return "\n".join(
        [
            f"## {identity['title']} ({identity['id']})",
            "",
            "You are a bounded Codex specialist subagent, not the main agent.",
            "",
            "Identity:",
            f"- Specialist role: {identity['title']}",
            "- Authority: Advisory only unless the main agent explicitly delegates write authority.",
            "- Relationship: Report to the main agent or traffic controller.",
            "",
            "Mission:",
            f"- {identity['mission']}",
            f"- Task: {task}",
            "",
            "Scope:",
            f"- {scope or 'Use only scope assigned by the main agent.'}",
            "",
            "Context:",
            f"- {context or 'No additional context provided.'}",
            "",
            "Supporting skills to load when relevant:",
            f"- {skills}",
            "",
            "Boundaries:",
            boundaries,
            "- Do not perform external side effects.",
            "- Do not claim final completion.",
            "- Do not reveal hidden chain of thought; provide evidence and concise rationale.",
            "",
            "Output focus:",
            outputs,
            "- open questions",
            "- recommended next action",
        ]
    )


def render_pack(selected: list[dict], pattern: str, task: str, scope: str, context: str) -> str:
    skills = ", ".join(all_skills(selected))
    header = "\n".join(
        [
            "# Codex Agent Identity Routing Pack",
            "",
            "Task:",
            f"- {task}",
            "",
            "Recommended orchestration:",
            f"- Pattern: {pattern}",
            f"- Primary identity: {selected[0]['id']}",
            f"- Supporting identities: {', '.join(identity['id'] for identity in selected[1:]) or 'none'}",
            f"- Supporting skills: {skills}",
            "",
            "Main-agent rule:",
            "- The main agent owns final decisions, edits, verification claims, and user response.",
        ]
    )
    prompts = [render_identity_prompt(identity, task, scope, context) for identity in selected]
    return header + "\n\n" + "\n\n".join(prompts) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True, help="Task to route.")
    parser.add_argument("--scope", default="", help="Files, directories, tools, or systems in scope.")
    parser.add_argument("--context", default="", help="Additional context for routing.")
    parser.add_argument("--max", type=int, default=4, help="Maximum identities to return.")
    parser.add_argument("--include-skill", action="append", default=[], help="Force preference for an existing skill. Can be repeated.")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON.")
    args = parser.parse_args()

    selected, pattern = route(
        task=args.task,
        scope=args.scope,
        context=args.context,
        max_identities=max(1, args.max),
        include_skills=set(args.include_skill),
    )

    if args.json:
        print(
            json.dumps(
                {
                    "task": args.task,
                    "scope": args.scope,
                    "context": args.context,
                    "pattern": pattern,
                    "primary_identity": selected[0]["id"],
                    "supporting_identities": [identity["id"] for identity in selected[1:]],
                    "supporting_skills": all_skills(selected),
                    "dispatch_plan": dispatch_plan(selected, pattern, args.task, args.scope, args.context),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(render_pack(selected, pattern, args.task, args.scope, args.context), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
