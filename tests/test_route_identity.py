#!/usr/bin/env python3
"""Test suite for route_identity.py"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".agents" / "skills" / "codex-agent-identity-bank" / "scripts"))

from route_identity import (  # noqa: E402
    dispatch_plan,
    infer_pattern,
    keyword_matches,
    normalize,
    route,
    score_identity,
    task_requests_write,
)


def test_normalize():
    assert normalize("Hello   World") == "hello world"
    assert normalize("React Native") == "react native"


def test_keyword_matches():
    assert keyword_matches("embedded", "embedded firmware project")
    assert not keyword_matches("embedded", "embeddedX")
    assert keyword_matches("React Native", "using react native for mobile")


def test_score_identity():
    identity = {
        "id": "embedded-firmware-engineer",
        "keywords": ["embedded", "firmware", "mcu"],
        "skills": ["gcc", "jlink"],
    }

    text = normalize("fix embedded firmware bug")
    score = score_identity(identity, text, set())
    assert score > 0

    text_with_skill = normalize("fix embedded bug")
    score_with_skill = score_identity(identity, text_with_skill, {"gcc"})
    assert score_with_skill > score


def test_infer_pattern():
    selected = [{"id": "qa-test-automation-engineer"}, {"id": "code-reviewer"}]
    assert infer_pattern(selected, "fix bug") == "critic-loop"
    assert infer_pattern([{"id": "software-architect"}], "compare architecture options") == "group-chat"


def test_task_requests_write_handles_optimize_and_review():
    assert task_requests_write("optimize this project", "")
    assert task_requests_write("review and fix auth flow", "")
    assert not task_requests_write("review architecture options", "")


def test_route_adds_review_support_for_optimization():
    selected, pattern = route(
        task="optimize this project",
        scope="repository-wide maintainability, performance, correctness",
        context="",
        max_identities=4,
        include_skills=set(),
    )
    ids = [identity["id"] for identity in selected]
    assert ids[0] == "code-reviewer"
    assert "performance-engineer" in ids
    assert pattern == "critic-loop"


def test_route_password_reset_auth_stays_in_software_domain():
    selected, pattern = route(
        task="login returns 500 after password reset",
        scope="src/auth tests/auth",
        context="",
        max_identities=4,
        include_skills=set(),
    )
    ids = [identity["id"] for identity in selected]

    assert "backend-api-engineer" in ids
    assert "security-engineer" in ids
    assert "qa-test-automation-engineer" in ids
    assert "hardware-bringup-engineer" not in ids
    assert "penetration-tester" not in ids
    assert pattern == "critic-loop"


def test_route_bugfix_recipe_auth_avoids_strategy_noise():
    selected, pattern = route(
        task=(
            "Fix or investigate this bug: login returns 500 after password reset. "
            "Focus on root cause, smallest safe patch, and regression tests in scope: src/auth tests/auth."
        ),
        scope="src/auth tests/auth",
        context=(
            "Expected outcome: accepted root-cause evidence, risky assumptions, files to inspect, "
            "recommended patch, and verification commands. Recipe outcome: A root-cause-focused fix plan "
            "with test coverage guidance."
        ),
        max_identities=4,
        include_skills=set(),
    )
    ids = [identity["id"] for identity in selected]

    assert "backend-api-engineer" in ids
    assert "security-engineer" in ids
    assert "qa-test-automation-engineer" in ids
    assert "code-reviewer" in ids
    assert "assumption-mapping" not in ids
    assert pattern == "critic-loop"


def test_route_anchor_breaks_ties_for_language_specialists():
    """A Rust task must select rust-engineer over peers sharing generic keywords."""
    selected, _ = route(
        task="write a rust async web server",
        scope="",
        context="",
        max_identities=4,
        include_skills=set(),
    )
    assert selected[0]["id"] == "rust-engineer"


def test_dispatch_plan_separates_identity_from_execution_role():
    identity = {
        "id": "frontend-ui-engineer",
        "title": "Frontend UI Engineer",
        "keywords": ["frontend"],
        "skills": ["playwright"],
        "mission": "Build UI",
        "boundaries": ["Stay in scope"],
        "output_focus": ["browser verification"],
    }

    item = dispatch_plan([identity], "handoff", "build frontend dashboard", "src", "")[0]
    assert item["id"] == "frontend-ui-engineer"
    assert item["identity_id"] == "frontend-ui-engineer"
    assert item["agent_type"] == "worker"
    assert item["execution_role"] == "worker"


def run_tests():
    tests = [
        ("normalize", test_normalize),
        ("keyword_matches", test_keyword_matches),
        ("score_identity", test_score_identity),
        ("infer_pattern", test_infer_pattern),
        ("task_requests_write", test_task_requests_write_handles_optimize_and_review),
        ("route_review_support", test_route_adds_review_support_for_optimization),
        ("route_password_reset_auth", test_route_password_reset_auth_stays_in_software_domain),
        ("route_bugfix_recipe_auth", test_route_bugfix_recipe_auth_avoids_strategy_noise),
        ("route_anchor_tiebreak", test_route_anchor_breaks_ties_for_language_specialists),
        ("dispatch_plan_contract", test_dispatch_plan_separates_identity_from_execution_role),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func()
            print(f"OK  {name}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL {name}: {e}")
            failed += 1
        except Exception as e:
            print(f"ERR  {name}: {type(e).__name__}: {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run_tests())
