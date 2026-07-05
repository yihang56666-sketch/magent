#!/usr/bin/env python3
"""Compatibility shim for the removed external model API adapter."""

from __future__ import annotations


class APIAdapter:
    """Legacy adapter kept only to explain the Codex-only runtime."""

    def __init__(self):
        self.mode = "codex-only"

    def create_message(self, model: str, max_tokens: int, messages: list) -> dict:
        raise RuntimeError(
            "External model API execution has been removed. "
            "Use the current Codex session to answer each agent prompt manually."
        )


def get_client() -> APIAdapter:
    return APIAdapter()
