#!/usr/bin/env python3
"""Group chat coordinator with speaker selection (inspired by AutoGen)."""

import json
from pathlib import Path
from typing import Any


class GroupChatCoordinator:
    """Coordinate multi-agent discussions with automatic speaker selection."""

    def __init__(self, run_dir: Path):
        self.run_dir = run_dir
        self.chat_log = run_dir / "group-chat.jsonl"
        self.max_rounds = 5

    def select_next_speaker(self, agents: list[dict], history: list[dict], current_speaker: str | None) -> str:
        """Select next speaker based on conversation context."""
        if not history:
            # First round: prioritize architect or product (by specialist id)
            priority_roles = ["software-architect", "product-engineer"]
            for agent in agents:
                if agent["id"] in priority_roles:
                    return agent["id"]
            return agents[0]["id"]

        # Extract keywords from last message
        last_msg = history[-1]["content"]
        keywords = self._extract_keywords(last_msg)

        # Score agents by relevance
        scores = {}
        for agent in agents:
            if agent["id"] == current_speaker:
                scores[agent["id"]] = -1  # Avoid back-to-back
                continue

            score = 0
            agent_keywords = self._get_agent_keywords(agent["id"])

            # Keyword match
            for kw in keywords:
                if kw in agent_keywords:
                    score += 2

            # Mention detection (by specialist id)
            if agent["id"].replace("-", " ") in last_msg.lower():
                score += 5

            # Round robin bonus
            appearance_count = sum(1 for h in history if h["speaker"] == agent["id"])
            score -= appearance_count

            scores[agent["id"]] = score

        # Select highest score
        if scores:
            return max(scores, key=scores.get)
        return agents[0]["id"]

    def run_group_chat(self, agents: list[dict], task: str, scope: str) -> list[dict]:
        """Run multi-round group discussion."""
        history = []
        current_speaker = None

        for round_num in range(self.max_rounds):
            # Select speaker
            speaker_id = self.select_next_speaker(agents, history, current_speaker)
            agent = next(a for a in agents if a["id"] == speaker_id)

            # Build context from history
            context = self._build_context(history)

            # Agent speaks
            message = {
                "round": round_num + 1,
                "speaker": speaker_id,
                "identity_id": agent.get("identity_id", agent["id"]),
                "agent_type": agent["agent_type"],
                "execution_role": agent.get("execution_role", agent["agent_type"]),
                "content": f"[Agent {speaker_id} would analyze based on: {task}]\n\n{context}"
            }

            history.append(message)
            current_speaker = speaker_id

            # Log
            with open(self.chat_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(message) + "\n")

            # Check consensus
            if self._has_consensus(history):
                break

        return history

    def _extract_keywords(self, text: str) -> list[str]:
        """Extract important keywords from text."""
        keywords = []
        patterns = [
            r'\b(security|vulnerability|auth|crypto)\b',
            r'\b(performance|latency|memory|optimization)\b',
            r'\b(architecture|design|pattern|structure)\b',
            r'\b(bug|error|crash|issue)\b',
            r'\b(test|qa|coverage|validation)\b'
        ]

        for pattern in patterns:
            import re
            matches = re.findall(pattern, text.lower())
            keywords.extend(matches)

        return list(set(keywords))

    def _get_agent_keywords(self, agent_type: str) -> list[str]:
        """Get keywords for agent type."""
        keyword_map = {
            "security-engineer": ["security", "vulnerability", "auth", "crypto"],
            "performance-engineer": ["performance", "latency", "memory", "optimization"],
            "software-architect": ["architecture", "design", "pattern", "structure"],
            "qa-test-automation-engineer": ["test", "qa", "coverage", "validation"],
            "code-reviewer": ["bug", "error", "quality", "issue"]
        }
        return keyword_map.get(agent_type, [])

    def _build_context(self, history: list[dict]) -> str:
        """Build conversation context for agent."""
        if not history:
            return ""

        context = "## Previous Discussion:\n"
        for msg in history[-3:]:  # Last 3 messages
            context += f"- **{msg.get('identity_id', msg['agent_type'])}**: {msg['content'][:100]}...\n"

        return context

    def _has_consensus(self, history: list[dict]) -> bool:
        """Check if agents reached consensus."""
        if len(history) < 3:
            return False

        # Simple heuristic: if last 2 messages agree
        last_two = history[-2:]
        keywords_1 = set(self._extract_keywords(last_two[0]["content"]))
        keywords_2 = set(self._extract_keywords(last_two[1]["content"]))

        overlap = len(keywords_1 & keywords_2)
        return overlap >= 2
