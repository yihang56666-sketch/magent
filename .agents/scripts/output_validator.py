#!/usr/bin/env python3
"""Advanced output validation with schema enforcement (inspired by CrewAI + MetaGPT)."""

import re
from typing import Any


class OutputValidator:
    """Validate agent output against expected schema."""

    # Schema definitions per agent type
    SCHEMAS = {
        "security-engineer": {
            "required_sections": ["Vulnerabilities", "Risks", "Remediation"],
            "min_findings": 1,
            "required_fields": ["severity", "file", "description"]
        },
        "code-reviewer": {
            "required_sections": ["Code Quality", "Issues", "Recommendations"],
            "min_findings": 1,
            "required_fields": ["severity", "line", "issue"]
        },
        "software-architect": {
            "required_sections": ["Architecture Analysis", "Tradeoffs", "Recommendations"],
            "min_findings": 1,
            "required_fields": ["component", "rationale"]
        },
        "_default": {
            "required_sections": ["Findings", "Evidence", "Recommended Next Action"],
            "min_findings": 1
        }
    }

    @classmethod
    def validate(cls, agent_type: str, content: str) -> dict[str, Any]:
        """Validate output against schema."""
        schema = cls.SCHEMAS.get(agent_type, cls.SCHEMAS["_default"])

        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "score": 0.0
        }

        # Check required sections
        for section in schema["required_sections"]:
            pattern = rf"##\s*{re.escape(section)}"
            if not re.search(pattern, content, re.IGNORECASE):
                results["errors"].append(f"Missing required section: {section}")
                results["valid"] = False

        # Check minimum content
        if len(content.strip()) < 100:
            results["errors"].append("Output too short (< 100 chars)")
            results["valid"] = False

        # Check findings count
        findings = re.findall(r'^[-*]\s+.+$', content, re.MULTILINE)
        if len(findings) < schema.get("min_findings", 0):
            results["warnings"].append(f"Low findings count: {len(findings)}")

        # Check for evidence (file paths, line numbers)
        has_files = bool(re.search(r'\w+\.\w+:\d+', content))
        has_code = bool(re.search(r'```\w*\n', content))

        if not (has_files or has_code):
            results["warnings"].append("No concrete evidence (file paths or code snippets)")

        # Calculate quality score
        score = 1.0
        if results["errors"]:
            score -= 0.5
        if results["warnings"]:
            score -= 0.1 * len(results["warnings"])
        if len(findings) >= schema.get("min_findings", 0) * 2:
            score += 0.2  # Bonus for thorough analysis

        results["score"] = max(0.0, min(1.0, score))

        return results

    @classmethod
    def get_schema(cls, agent_type: str) -> dict:
        """Get schema for agent type."""
        return cls.SCHEMAS.get(agent_type, cls.SCHEMAS["_default"])
