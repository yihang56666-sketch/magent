#!/usr/bin/env python3
"""Validate the Codex multi-agent identity repository."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IDENTITIES_JSON = ROOT / "skills" / "codex-agent-identity-bank" / "references" / "identities.json"


REQUIRED_PATHS = [
    ROOT.parent / 'AGENTS.md',
    ROOT.parent / '.codex' / 'config.toml',
    ROOT.parent / '.codex' / 'agents' / 'explorer.toml',
    ROOT.parent / '.codex' / 'agents' / 'reviewer.toml',
    ROOT.parent / '.codex' / 'agents' / 'docs-researcher.toml',
    ROOT.parent / '.codex' / 'agents' / 'traffic-controller.toml',
    ROOT.parent / '.codex' / 'agents' / 'implementer.toml',
    ROOT / "identity-bank" / "INDEX.md",
    ROOT / "skills" / "codex-agent-identity-bank" / "SKILL.md",
    ROOT / "skills" / "codex-multi-agent-orchestrator" / "SKILL.md",
    ROOT / "workflows" / "bugfix.yaml",
    ROOT / "workflows" / "embedded-debug.yaml",
    ROOT / "workflows" / "frontend-polish.yaml",
    ROOT / "presets" / "small-team.json",
    ROOT / "presets" / "embedded-team.json",
    ROOT / "reports" / "runs" / ".keep",
]


def main() -> int:
    errors = []
    for path in REQUIRED_PATHS:
        if not path.exists():
            errors.append(f"missing: {path}")

    try:
        data = json.loads(IDENTITIES_JSON.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid identities.json: {exc}")
        data = {"identities": []}

    identity_count = len(data.get("identities", []))
    if identity_count < 12:
        errors.append(f"expected at least 12 identities, found {identity_count}")

    for identity in data.get("identities", []):
        for key in ["id", "title", "keywords", "skills", "mission", "boundaries", "output_focus"]:
            if key not in identity:
                errors.append(f"{identity.get('id', '<unknown>')} missing {key}")

    if errors:
        print("Identity repository validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Identity repository valid: {identity_count} identities")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
