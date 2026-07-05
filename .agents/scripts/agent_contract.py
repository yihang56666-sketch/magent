#!/usr/bin/env python3
"""Dispatch-plan field contract shared by all executors."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
IDENTITIES_DIR = ROOT / "identities"
EXECUTION_ROLES = {"worker", "explorer"}


def identity_id(agent: dict[str, Any]) -> str:
    return agent.get("id") or agent.get("identity_id") or agent.get("agent_type") or "specialist"


def execution_role(agent: dict[str, Any]) -> str:
    role = agent.get("execution_role") or agent.get("agent_type", "explorer")
    return role if role in EXECUTION_ROLES else "explorer"


def specialist_label(agent: dict[str, Any]) -> str:
    return agent.get("title") or identity_id(agent)


@lru_cache(maxsize=256)
def _load_identity_card(agent_id: str) -> str | None:
    if not agent_id:
        return None
    matches = sorted(IDENTITIES_DIR.glob(f"**/{agent_id}.md"))
    if not matches:
        return None
    return matches[0].read_text(encoding="utf-8")


def find_identity_card(agent_id: str) -> Path | None:
    if not agent_id:
        return None
    matches = sorted(IDENTITIES_DIR.glob(f"**/{agent_id}.md"))
    return matches[0] if matches else None


def load_identity_text(agent: dict[str, Any]) -> str:
    card = _load_identity_card(identity_id(agent))
    if card is not None:
        return card

    rendered = agent.get("prompt")
    if rendered:
        return rendered

    return f"You are a {specialist_label(agent)}."


def cache_identity_key(agent: dict[str, Any]) -> str:
    return identity_id(agent)
