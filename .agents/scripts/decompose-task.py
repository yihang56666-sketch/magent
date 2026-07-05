#!/usr/bin/env python3
"""Dynamically decompose complex tasks into subtasks with agent assignments."""

from __future__ import annotations

import argparse
import json
import logging
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class Subtask:
    """A decomposed subtask."""
    id: str
    description: str
    dependencies: list[str]
    estimated_complexity: str  # low, medium, high
    recommended_agent: str
    scope: str
    acceptance_criteria: list[str]


@dataclass
class TaskDecomposition:
    """Complete task breakdown."""
    original_task: str
    subtasks: list[Subtask]
    execution_order: list[str]
    total_complexity: str
    critical_path: list[str]


def estimate_complexity(task: str) -> str:
    """Estimate task complexity based on keywords."""
    task_lower = task.lower()

    high_indicators = ["refactor", "migrate", "redesign", "architecture", "重构", "迁移", "架构"]
    medium_indicators = ["implement", "build", "create", "add feature", "实现", "构建", "添加功能"]
    low_indicators = ["fix", "update", "adjust", "tweak", "修复", "更新", "调整"]

    if any(ind in task_lower for ind in high_indicators):
        return "high"
    elif any(ind in task_lower for ind in medium_indicators):
        return "medium"
    else:
        return "low"


def detect_task_type(task: str) -> str:
    """Detect primary task type."""
    task_lower = task.lower()

    patterns = {
        "bugfix": ["fix", "bug", "error", "crash", "修复", "错误", "崩溃"],
        "feature": ["add", "implement", "create", "build", "feature", "添加", "实现", "功能"],
        "refactor": ["refactor", "redesign", "cleanup", "重构", "清理"],
        "security": ["security", "vulnerability", "exploit", "安全", "漏洞"],
        "performance": ["slow", "optimize", "performance", "latency", "性能", "优化", "延迟"],
        "test": ["test", "coverage", "测试", "覆盖"],
    }

    for task_type, keywords in patterns.items():
        if any(kw in task_lower for kw in keywords):
            return task_type

    return "general"


def decompose_bugfix(task: str, scope: str) -> list[Subtask]:
    """Decompose a bug fix task."""
    return [
        Subtask(
            id="bugfix-1",
            description="Reproduce the bug and gather evidence",
            dependencies=[],
            estimated_complexity="low",
            recommended_agent="qa-test-automation-engineer",
            scope=scope,
            acceptance_criteria=["Bug reproduced consistently", "Failure logs captured"],
        ),
        Subtask(
            id="bugfix-2",
            description="Investigate root cause",
            dependencies=["bugfix-1"],
            estimated_complexity="medium",
            recommended_agent="primary-routed-identity",
            scope=scope,
            acceptance_criteria=["Root cause identified", "Evidence documented"],
        ),
        Subtask(
            id="bugfix-3",
            description="Implement fix",
            dependencies=["bugfix-2"],
            estimated_complexity="medium",
            recommended_agent="primary-routed-identity",
            scope=scope,
            acceptance_criteria=["Fix implemented", "Code compiles"],
        ),
        Subtask(
            id="bugfix-4",
            description="Verify fix and check for regressions",
            dependencies=["bugfix-3"],
            estimated_complexity="low",
            recommended_agent="qa-test-automation-engineer",
            scope=scope,
            acceptance_criteria=["Bug no longer reproduces", "No new failures"],
        ),
        Subtask(
            id="bugfix-5",
            description="Review code changes",
            dependencies=["bugfix-3"],
            estimated_complexity="low",
            recommended_agent="code-reviewer",
            scope=scope,
            acceptance_criteria=["No security issues", "No maintainability concerns"],
        ),
    ]


def decompose_feature(task: str, scope: str) -> list[Subtask]:
    """Decompose a feature implementation task."""
    return [
        Subtask(
            id="feature-1",
            description="Define acceptance criteria and user requirements",
            dependencies=[],
            estimated_complexity="low",
            recommended_agent="product-engineer",
            scope=scope,
            acceptance_criteria=["User stories defined", "Edge cases documented"],
        ),
        Subtask(
            id="feature-2",
            description="Design architecture and data model",
            dependencies=["feature-1"],
            estimated_complexity="medium",
            recommended_agent="software-architect",
            scope=scope,
            acceptance_criteria=["Architecture diagram", "API contracts defined"],
        ),
        Subtask(
            id="feature-3",
            description="Implement backend logic",
            dependencies=["feature-2"],
            estimated_complexity="high",
            recommended_agent="backend-api-engineer",
            scope=scope,
            acceptance_criteria=["API endpoints work", "Tests pass"],
        ),
        Subtask(
            id="feature-4",
            description="Implement frontend UI",
            dependencies=["feature-2"],
            estimated_complexity="high",
            recommended_agent="frontend-ui-engineer",
            scope=scope,
            acceptance_criteria=["UI matches design", "Responsive"],
        ),
        Subtask(
            id="feature-5",
            description="Integration testing",
            dependencies=["feature-3", "feature-4"],
            estimated_complexity="medium",
            recommended_agent="qa-test-automation-engineer",
            scope=scope,
            acceptance_criteria=["E2E tests pass", "80%+ coverage"],
        ),
        Subtask(
            id="feature-6",
            description="Security review",
            dependencies=["feature-3", "feature-4"],
            estimated_complexity="low",
            recommended_agent="security-engineer",
            scope=scope,
            acceptance_criteria=["No critical vulnerabilities", "Auth verified"],
        ),
    ]


def decompose_refactor(task: str, scope: str) -> list[Subtask]:
    """Decompose a refactoring task."""
    return [
        Subtask(
            id="refactor-1",
            description="Map current behavior and test coverage",
            dependencies=[],
            estimated_complexity="medium",
            recommended_agent="code-reviewer",
            scope=scope,
            acceptance_criteria=["Current behavior documented", "Test coverage measured"],
        ),
        Subtask(
            id="refactor-2",
            description="Define refactoring boundaries and phases",
            dependencies=["refactor-1"],
            estimated_complexity="medium",
            recommended_agent="software-architect",
            scope=scope,
            acceptance_criteria=["Refactor plan", "Risk assessment"],
        ),
        Subtask(
            id="refactor-3",
            description="Implement refactoring incrementally",
            dependencies=["refactor-2"],
            estimated_complexity="high",
            recommended_agent="primary-routed-identity",
            scope=scope,
            acceptance_criteria=["Code refactored", "Tests still pass"],
        ),
        Subtask(
            id="refactor-4",
            description="Verify behavior preservation",
            dependencies=["refactor-3"],
            estimated_complexity="medium",
            recommended_agent="qa-test-automation-engineer",
            scope=scope,
            acceptance_criteria=["All tests pass", "No behavior changes"],
        ),
    ]


def decompose_task(task: str, scope: str, context: str) -> TaskDecomposition:
    """Main task decomposition logic."""
    task_type = detect_task_type(task)
    logger.info(f"Detected task type: {task_type}")

    if task_type == "bugfix":
        subtasks = decompose_bugfix(task, scope)
    elif task_type == "feature":
        subtasks = decompose_feature(task, scope)
    elif task_type == "refactor":
        subtasks = decompose_refactor(task, scope)
    else:
        # Generic decomposition
        subtasks = [
            Subtask(
                id="generic-1",
                description="Analyze requirements and scope",
                dependencies=[],
                estimated_complexity="low",
                recommended_agent="software-architect",
                scope=scope,
                acceptance_criteria=["Requirements clear"],
            ),
            Subtask(
                id="generic-2",
                description=f"Implement: {task}",
                dependencies=["generic-1"],
                estimated_complexity=estimate_complexity(task),
                recommended_agent="primary-routed-identity",
                scope=scope,
                acceptance_criteria=["Implementation complete"],
            ),
            Subtask(
                id="generic-3",
                description="Review and test",
                dependencies=["generic-2"],
                estimated_complexity="low",
                recommended_agent="code-reviewer",
                scope=scope,
                acceptance_criteria=["Review passed", "Tests added"],
            ),
        ]

    # Calculate execution order (topological sort)
    execution_order = topological_sort(subtasks)

    # Find critical path (longest dependency chain)
    critical_path = find_critical_path(subtasks)

    # Estimate total complexity
    complexity_counts = {"high": 0, "medium": 0, "low": 0}
    for subtask in subtasks:
        complexity_counts[subtask.estimated_complexity] += 1

    if complexity_counts["high"] > 0:
        total_complexity = "high"
    elif complexity_counts["medium"] > 1:
        total_complexity = "high"
    elif complexity_counts["medium"] > 0:
        total_complexity = "medium"
    else:
        total_complexity = "low"

    return TaskDecomposition(
        original_task=task,
        subtasks=subtasks,
        execution_order=execution_order,
        total_complexity=total_complexity,
        critical_path=critical_path,
    )


def topological_sort(subtasks: list[Subtask]) -> list[str]:
    """Sort subtasks by dependencies."""
    # Simple topological sort
    sorted_ids = []
    remaining = {s.id: s for s in subtasks}

    while remaining:
        # Find tasks with no unmet dependencies
        ready = [
            task_id for task_id, task in remaining.items()
            if all(dep in sorted_ids for dep in task.dependencies)
        ]

        if not ready:
            # Circular dependency or error
            ready = [list(remaining.keys())[0]]

        sorted_ids.extend(ready)
        for task_id in ready:
            del remaining[task_id]

    return sorted_ids


def find_critical_path(subtasks: list[Subtask]) -> list[str]:
    """Find longest dependency chain."""
    task_map = {s.id: s for s in subtasks}

    def path_length(task_id: str, visited: set) -> list[str]:
        if task_id in visited:
            return []
        visited.add(task_id)

        task = task_map[task_id]
        if not task.dependencies:
            return [task_id]

        max_path = []
        for dep in task.dependencies:
            dep_path = path_length(dep, visited.copy())
            if len(dep_path) > len(max_path):
                max_path = dep_path

        return max_path + [task_id]

    all_paths = [path_length(s.id, set()) for s in subtasks]
    return max(all_paths, key=len) if all_paths else []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True)
    parser.add_argument("--scope", default="")
    parser.add_argument("--context", default="")
    parser.add_argument("--output", type=Path, help="Save to file")
    args = parser.parse_args()

    try:
        decomposition = decompose_task(args.task, args.scope, args.context)

        result = {
            "original_task": decomposition.original_task,
            "total_complexity": decomposition.total_complexity,
            "subtasks": [asdict(s) for s in decomposition.subtasks],
            "execution_order": decomposition.execution_order,
            "critical_path": decomposition.critical_path,
        }

        output_json = json.dumps(result, ensure_ascii=False, indent=2)

        if args.output:
            args.output.write_text(output_json, encoding="utf-8")
            logger.info(f"✓ Saved to {args.output}")
        else:
            print(output_json)

        logger.info(f"✓ Decomposed into {len(decomposition.subtasks)} subtasks")
        logger.info(f"  Complexity: {decomposition.total_complexity}")
        logger.info(f"  Critical path: {' → '.join(decomposition.critical_path)}")

        return 0
    except Exception as e:
        logger.error(f"Decomposition failed: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
