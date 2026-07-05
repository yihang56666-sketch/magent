#!/usr/bin/env python3
"""Test agent_contract resolves specialist identity, not execution role."""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".agents" / "scripts"))

from agent_contract import (  # noqa: E402
    cache_identity_key,
    execution_role,
    find_identity_card,
    identity_id,
    load_identity_text,
)


FRONTEND = {
    "id": "frontend-ui-engineer",
    "title": "Frontend UI Engineer",
    "agent_type": "worker",
    "primary": True,
    "prompt": "## Frontend UI Engineer (frontend-ui-engineer)\nrendered prompt body",
}

REVIEWER = {
    "id": "code-reviewer",
    "title": "Code Reviewer",
    "agent_type": "explorer",
    "prompt": "## Code Reviewer rendered",
}


def test_identity_id_is_specialist_not_role():
    assert identity_id(FRONTEND) == "frontend-ui-engineer"
    assert identity_id(REVIEWER) == "code-reviewer"


def test_execution_role_is_role():
    assert execution_role(FRONTEND) == "worker"
    assert execution_role(REVIEWER) == "explorer"


def test_role_never_leaks_as_identity():
    assert identity_id(FRONTEND) != "worker"
    assert cache_identity_key(FRONTEND) == "frontend-ui-engineer"
    assert cache_identity_key(REVIEWER) == "code-reviewer"


def test_finds_card_across_subgroups():
    assert find_identity_card("frontend-ui-engineer") is not None
    assert find_identity_card("code-reviewer") is not None
    assert find_identity_card("worker") is None
    assert find_identity_card("explorer") is None


def test_loaded_identity_contains_specialist_not_role():
    text = load_identity_text(FRONTEND)
    assert "Frontend UI Engineer" in text
    assert text.strip() != "You are a worker."

    rtext = load_identity_text(REVIEWER)
    assert "Code Reviewer" in rtext or "code-reviewer" in rtext.lower()


def test_fallback_to_rendered_prompt_when_no_card():
    unknown = {"id": "no-such-identity", "title": "Ghost", "agent_type": "worker", "prompt": "## Ghost rendered body"}
    assert load_identity_text(unknown) == "## Ghost rendered body"


def run():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = failed = 0
    for t in tests:
        try:
            t()
            print(f"OK  {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL {t.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"ERR  {t.__name__}: {type(e).__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(run())
