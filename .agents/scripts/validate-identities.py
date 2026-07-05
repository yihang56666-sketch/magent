#!/usr/bin/env python3
"""Validate the multi-agent project registry, identities, workflows, and presets."""

from __future__ import annotations

import json
import logging
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
IDENTITIES_PATH = ROOT / "skills" / "codex-agent-identity-bank" / "references" / "identities.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict:
    if yaml is None:
        raise ImportError("PyYAML not installed. Install with: pip install pyyaml")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def main() -> int:
    try:
        identities = load_json(IDENTITIES_PATH)["identities"]
    except Exception as e:
        logger.error(f"Failed to load identities: {e}")
        return 1

    identity_ids = {identity["id"] for identity in identities}
    errors: list[str] = []

    for identity in identities:
        for field in ["id", "title", "keywords", "skills", "mission", "boundaries", "output_focus"]:
            if field not in identity:
                errors.append(f"identity {identity.get('id', '<unknown>')} missing {field}")

    for path in sorted((ROOT / "presets").glob("*.json")):
        try:
            preset = load_json(path)
            for identity_id in preset.get("identities", []):
                if identity_id not in identity_ids and identity_id != "primary-routed-identity":
                    errors.append(f"{path.name}: unknown identity {identity_id}")
        except Exception as e:
            errors.append(f"{path.name}: failed to parse: {e}")

    workflow_count = 0
    for ext, loader in [("*.json", load_json), ("*.yaml", load_yaml)]:
        for path in sorted((ROOT / "workflows").glob(ext)):
            workflow_count += 1
            try:
                workflow = loader(path)
                for identity_id in workflow.get("default_identities", []):
                    if identity_id not in identity_ids and identity_id != "primary-routed-identity":
                        errors.append(f"{path.name}: unknown default_identity {identity_id}")
                for phase in workflow.get("phases", []):
                    if isinstance(phase, dict):
                        identity_id = phase.get("identity")
                        if identity_id and identity_id not in identity_ids and identity_id != "primary-routed-identity":
                            errors.append(f"{path.name}: unknown phase identity {identity_id}")
            except Exception as e:
                errors.append(f"{path.name}: failed to parse: {e}")

    if errors:
        for error in errors:
            logger.error(error)
        return 1

    logger.info(
        f"[OK] Validated {len(identity_ids)} identities, "
        f"{len(list((ROOT / 'presets').glob('*.json')))} presets, {workflow_count} workflows"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
