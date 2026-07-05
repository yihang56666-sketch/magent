#!/usr/bin/env python3
"""Standalone smoke test for the manual execution workflow."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".agents" / "scripts"))

from config_manager import ConfigManager  # noqa: E402
from manual_execution import initialize_manual_run, sync_manual_run  # noqa: E402


def main() -> int:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        run_dir = temp_root / "run"
        run_dir.mkdir(exist_ok=True)

        plan = {
            "task": "Smoke test",
            "scope": "tests",
            "context": "",
            "pattern": "critic-loop",
            "primary_identity": "code-reviewer",
            "dispatch_plan": [
                {
                    "id": "code-reviewer",
                    "title": "Code Reviewer",
                    "identity_id": "code-reviewer",
                    "agent_type": "explorer",
                    "execution_role": "explorer",
                    "mission": "Review the smoke test",
                    "prompt": "## Code Reviewer",
                }
            ],
        }
        (run_dir / "dispatch-plan.json").write_text(json.dumps(plan), encoding="utf-8")

        cfg = ConfigManager(temp_root / ".magent")
        cfg.set("api_key", "legacy")
        cfg.set("api_base", "legacy")
        cfg.set("default_model", "codex-current-session")

        assert cfg.get_default_model() == "codex-current-session"
        assert "api_key" not in cfg.list()
        assert "api_base" not in cfg.list()

        summary = initialize_manual_run(run_dir)
        assert summary["total"] == 1

        (run_dir / "code-reviewer.output.md").write_text(
            "## Findings\nok\n\n## Evidence\nx\n\n## Risks\nnone\n\n## Open Questions\nnone\n\n## Recommended Next Action\nship\n",
            encoding="utf-8",
        )
        refreshed = sync_manual_run(run_dir)
        assert refreshed["completed"] == 1
        assert refreshed["pending"] == 0

    print("OK  manual_execution_smoke")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
