#!/usr/bin/env python3
"""Configuration manager for the Codex-only multi-agent workflow."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ConfigManager:
    """Manage lightweight local configuration."""

    LEGACY_KEYS = {"api_key", "api_base"}

    def __init__(self, config_dir: Path | None = None):
        self.config_dir = config_dir or (Path.home() / ".magent")
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def get(self, key: str, default: Any = None) -> Any:
        if key in self.LEGACY_KEYS:
            return default
        return self._load_config().get(key, default)

    def set(self, key: str, value: Any) -> None:
        if key in self.LEGACY_KEYS:
            config = self._load_config()
            if key in config:
                del config[key]
                self._save_config(config)
            return
        config = self._load_config()
        config[key] = value
        self._save_config(config)

    def delete(self, key: str) -> None:
        config = self._load_config()
        if key in config:
            del config[key]
            self._save_config(config)

    def list(self) -> dict[str, Any]:
        return {key: value for key, value in self._load_config().items() if key not in self.LEGACY_KEYS}

    def get_default_model(self) -> str:
        """Return a local label for the current Codex session."""
        return self.get("default_model", "codex-current-session")

    def get_default_budget(self) -> int | None:
        """Return an optional user note for manual review scope."""
        return self.get("default_budget")

    def get_cache_ttl_days(self) -> int:
        return self.get("cache_ttl_days", 7)

    def get_max_workers(self) -> int:
        return self.get("max_workers", 3)

    def _load_config(self) -> dict[str, Any]:
        if not self.config_file.exists():
            return {}
        try:
            return json.loads(self.config_file.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save_config(self, config: dict[str, Any]) -> None:
        self.config_file.write_text(
            json.dumps(config, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


_config: ConfigManager | None = None


def get_config() -> ConfigManager:
    global _config
    if _config is None:
        _config = ConfigManager()
    return _config
