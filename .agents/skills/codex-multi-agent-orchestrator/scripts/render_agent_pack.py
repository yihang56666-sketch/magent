#!/usr/bin/env python3
"""Render bounded Codex subagent briefing packets."""

from __future__ import annotations

import argparse
from pathlib import Path
from textwrap import dedent


ROLE_SUMMARIES = {
    "traffic-controller": {
        "identity": "Bounded coordination subagent that maintains the multi-agent relationship map; supervisor/router, not a second main agent.",
        "mission": "Track roles, scopes, dependencies, conflicts, missing evidence, and next speaker or handoff target.",
        "forbidden": "Do not implement code, decide final outcomes, or perform external side effects.",
        "output": "Relationship map, conflict register, missing evidence, recommended merge decision.",
    },
    "sop-planner": {
        "identity": "Phase-planning subagent for repeatable project work.",
        "mission": "Convert a broad task into phases with inputs, expected artifacts, evidence requirements, and exit criteria.",
        "forbidden": "Do not treat the phase plan as user-approved implementation or add heavyweight process to tiny tasks.",
        "output": "Phase gates, role assignments, required artifacts, verification checkpoints.",
    },
    "explorer": {
        "identity": "Read-only evidence gathering subagent.",
        "mission": "Inspect assigned files, docs, logs, commands, or sources and return grounded facts.",
        "forbidden": "Do not patch files, decide fixes, or generalize beyond observed evidence.",
        "output": "Relevant facts, evidence, gaps, uncertainties.",
    },
    "reviewer": {
        "identity": "Independent correctness and risk review subagent.",
        "mission": "Find bugs, regressions, security issues, maintainability risks, and missing tests.",
        "forbidden": "Do not rewrite the solution or invent requirements.",
        "output": "Findings first, with severity, evidence, impact, open questions, and verification suggestions.",
    },
    "implementer": {
        "identity": "Scoped implementation subagent.",
        "mission": "Draft a narrow implementation plan or patch within delegated scope.",
        "forbidden": "Do not modify files unless explicitly granted write authority.",
        "output": "Patch summary or proposed diff, verification performed, residual risks.",
    },
    "test-runner": {
        "identity": "Verification subagent.",
        "mission": "Run scoped tests, lint, typecheck, builds, or reproduction commands.",
        "forbidden": "Do not fix failures unless separately dispatched.",
        "output": "Commands run, pass/fail result, key output lines, likely failure owner.",
    },
    "docs-researcher": {
        "identity": "Documentation and release-note verification subagent.",
        "mission": "Verify facts against official or primary sources.",
        "forbidden": "Do not rely on stale memory for changing APIs or product behavior.",
        "output": "Source list, verified facts, version/date constraints, confidence, unknowns.",
    },
    "domain-specialist": {
        "identity": "Narrow expert subagent for one named domain.",
        "mission": "Apply domain-specific rules, risks, constraints, and expected patterns.",
        "forbidden": "Do not override repo evidence or expand into unrelated decisions.",
        "output": "Domain-specific risks, constraints, recommended checks.",
    },
}

PATTERN_RULES = {
    "supervisor": [
        "Route all subagent output through the traffic-controller or main agent.",
        "Do not let subagents coordinate directly.",
        "Maintain relationship map, conflict register, and next merge decision.",
    ],
    "handoff": [
        "Use explicit handoff packets between sequential specialists.",
        "Pass accepted facts, open risks, one explicit question, and forbidden assumptions.",
        "Do not pass unsupported assumptions downstream.",
    ],
    "sop": [
        "Work through phase gates: investigate, design, implement, verify, review, summarize.",
        "Each phase must produce an artifact or decision before the next phase starts.",
        "Keep phases small enough for Codex to verify.",
    ],
    "group-chat": [
        "Give each agent a separate viewpoint or evidence scope.",
        "Limit discussion rounds and require traffic-controller synthesis.",
        "Terminate when there is a decision, unresolved question, or verification need.",
    ],
    "critic-loop": [
        "Implementer proposes or applies a narrow change.",
        "Reviewer attacks correctness and risk.",
        "Test-runner verifies concrete behavior before the main agent claims completion.",
    ],
    "stateful-observer": [
        "Prefer dormant role cards over idle live agents.",
        "If observers are live, keep them read-only and silent until a trigger occurs.",
        "Record observation order, source, evidence, decision impact, and whether it is still current.",
    ],
}


def parse_roles(raw: str) -> list[str]:
    roles = [part.strip() for part in raw.split(",") if part.strip()]
    unknown = [role for role in roles if role not in ROLE_SUMMARIES]
    if unknown:
        valid = ", ".join(sorted(ROLE_SUMMARIES))
        raise SystemExit(f"Unknown role(s): {', '.join(unknown)}. Valid roles: {valid}")
    return roles


def parse_pattern(raw: str) -> str:
    if raw == "auto":
        return raw
    if raw not in PATTERN_RULES:
        valid = "auto, " + ", ".join(sorted(PATTERN_RULES))
        raise SystemExit(f"Unknown pattern: {raw}. Valid patterns: {valid}")
    return raw


def infer_pattern(task: str, scope: str, context: str) -> str:
    text = f"{task} {scope} {context}".lower()
    if any(word in text for word in ["watch", "observe", "monitor", "旁观", "看着", "观察", "监控"]):
        return "stateful-observer"
    if any(word in text for word in ["compare", "option", "architecture", "tradeoff", "debate", "方案", "架构", "对比", "取舍"]):
        return "group-chat"
    if any(word in text for word in ["migration", "migrate", "large feature", "roadmap", "project", "plan", "规划", "迁移", "大功能"]):
        return "sop"
    if any(word in text for word in ["handoff", "pipeline", "sequence", "流水线", "交接", "串联"]):
        return "handoff"
    if any(word in text for word in ["bug", "fix", "failing", "failure", "refactor", "patch", "security", "漏洞", "修复", "失败", "重构", "补丁", "安全"]):
        return "critic-loop"
    return "supervisor"


def infer_roles(pattern: str, task: str, scope: str, context: str) -> list[str]:
    text = f"{task} {scope} {context}".lower()
    roles_by_pattern = {
        "supervisor": ["explorer", "reviewer", "traffic-controller"],
        "handoff": ["explorer", "implementer", "test-runner", "reviewer"],
        "sop": ["sop-planner", "explorer", "implementer", "test-runner", "reviewer"],
        "group-chat": ["explorer", "domain-specialist", "reviewer", "traffic-controller"],
        "critic-loop": ["explorer", "implementer", "reviewer", "test-runner"],
        "stateful-observer": ["explorer", "reviewer", "traffic-controller"],
    }
    roles = list(roles_by_pattern[pattern])
    if any(word in text for word in ["docs", "documentation", "api", "sdk", "latest", "current", "官方", "文档", "接口", "最新"]):
        roles.insert(-1 if "traffic-controller" in roles else len(roles), "docs-researcher")
    if any(word in text for word in ["security", "auth", "permission", "secret", "credential", "安全", "权限", "认证", "密钥"]):
        if "domain-specialist" not in roles:
            roles.insert(-1 if "traffic-controller" in roles else len(roles), "domain-specialist")
    return dedupe(roles)


def dedupe(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def render_pattern_block(pattern: str) -> str:
    lines = ["Coordination Pattern:", f"- Pattern: {pattern}"]
    lines.extend(f"- {rule}" for rule in PATTERN_RULES[pattern])
    return "\n".join(lines)


def render_packet(role: str, task: str, scope: str, context: str, pattern: str) -> str:
    card = ROLE_SUMMARIES[role]
    forbidden_lines = [card["forbidden"]]
    if "external side effects" not in card["forbidden"]:
        forbidden_lines.append("Do not perform external side effects.")
    forbidden_lines.extend(
        [
            "Do not claim final completion.",
            "Do not reveal hidden chain of thought; provide evidence and concise rationale.",
        ]
    )
    forbidden_block = "\n".join(f"- {line}" for line in forbidden_lines)
    return "\n".join(
        [
            f"## {role}",
            "",
            "You are a bounded Codex subagent, not the main agent.",
            "",
            "Identity:",
            f"- Role: {role}",
            f"- Role definition: {card['identity']}",
            "- Authority: Advisory only unless the main agent explicitly delegates more.",
            "- Relationship: Report to the main agent or traffic controller; do not address the user as task owner.",
            "",
            "Mission:",
            f"- {card['mission']}",
            f"- Task: {task}",
            "",
            "Current Situation:",
            f"- {context}",
            "",
            "Allowed Scope:",
            f"- {scope}",
            "",
            render_pattern_block(pattern),
            "",
            "Forbidden:",
            forbidden_block,
            "",
            "Output Format:",
            "- Findings:",
            "- Evidence:",
            "- Risks:",
            "- Open questions:",
            "- Recommended next action:",
            "",
            "Stop Condition:",
            "- Stop after producing the requested report or when scope is blocked.",
        ]
    )


def render_decision_block(roles: list[str], pattern: str, auto: bool) -> str:
    mode = "auto" if auto else "manual"
    return "\n".join(
        [
            "Orchestration Decision:",
            f"- Mode: {mode}",
            f"- Pattern: {pattern}",
            f"- Roles: {', '.join(roles)}",
            "- Main agent remains responsible for final decisions, edits, verification claims, and user response.",
        ]
    )


def render_pack(roles: list[str], task: str, scope: str, context: str, pattern: str, auto: bool) -> str:
    header = dedent(
        f"""
        # Codex Multi-Agent Briefing Pack

        Task:
        - {task}

        Shared scope:
        - {scope}

        Shared context:
        - {context}

        Control pattern:
        - {pattern}
        """
    ).strip()
    decision = render_decision_block(roles, pattern, auto)
    packets = [render_packet(role, task, scope, context, pattern) for role in roles]
    return header + "\n\n" + decision + "\n\n" + "\n\n".join(packets) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True, help="Main task or decision point.")
    parser.add_argument("--roles", help="Comma-separated roles to render. Omit with --auto.")
    parser.add_argument(
        "--pattern",
        default="auto",
        help="Coordination pattern: auto, supervisor, handoff, sop, group-chat, critic-loop, stateful-observer.",
    )
    parser.add_argument("--auto", action="store_true", help="Infer roles and pattern from task, scope, and context.")
    parser.add_argument("--scope", default="Use only the files, tools, and sources explicitly assigned by the main agent.")
    parser.add_argument("--context", default="No additional context provided.")
    parser.add_argument("--output", help="Optional file path for the generated Markdown pack.")
    args = parser.parse_args()

    pattern = parse_pattern(args.pattern)
    auto = args.auto or args.roles is None or pattern == "auto"
    if auto:
        pattern = infer_pattern(args.task, args.scope, args.context) if pattern == "auto" else pattern
        roles = infer_roles(pattern, args.task, args.scope, args.context) if args.roles is None else parse_roles(args.roles)
    else:
        roles = parse_roles(args.roles)
    pack = render_pack(roles, args.task, args.scope, args.context, pattern, auto)

    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(pack, encoding="utf-8")
    else:
        print(pack, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
