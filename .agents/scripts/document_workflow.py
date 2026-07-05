#!/usr/bin/env python3
"""Document-driven workflow with structured templates (inspired by MetaGPT)."""

from pathlib import Path
from typing import Any


class DocumentTemplate:
    """Structured document templates for each workflow phase."""

    TEMPLATES = {
        "product_requirements": """# Product Requirements Document

## Problem Statement
{problem}

## User Stories
{user_stories}

## Acceptance Criteria
{acceptance_criteria}

## Non-Functional Requirements
{nfr}

## Success Metrics
{metrics}
""",

        "architecture_design": """# Architecture Design Document

## System Overview
{overview}

## Components
{components}

## Data Flow
{data_flow}

## Technology Stack
{tech_stack}

## Tradeoffs & Decisions
{tradeoffs}

## Risks & Mitigations
{risks}
""",

        "implementation_plan": """# Implementation Plan

## Tasks
{tasks}

## Dependencies
{dependencies}

## Timeline
{timeline}

## Testing Strategy
{testing}

## Deployment Plan
{deployment}
""",

        "test_plan": """# Test Plan

## Test Cases
{test_cases}

## Coverage Requirements
{coverage}

## Test Data
{test_data}

## Expected Results
{expected}

## Edge Cases
{edge_cases}
"""
    }

    @classmethod
    def render(cls, template_name: str, **kwargs) -> str:
        """Render template with provided data."""
        template = cls.TEMPLATES.get(template_name, "")
        return template.format(**kwargs)

    @classmethod
    def parse(cls, template_name: str, content: str) -> dict[str, str]:
        """Parse document back to structured data."""
        import re
        sections = {}

        # Extract sections between ## headers
        pattern = r'## (.+?)\n(.*?)(?=\n## |\Z)'
        matches = re.findall(pattern, content, re.DOTALL)

        for header, body in matches:
            key = header.strip().lower().replace(' ', '_')
            sections[key] = body.strip()

        return sections


class DocumentDrivenWorkflow:
    """Workflow where each phase outputs structured documents."""

    def __init__(self, run_dir: Path):
        self.run_dir = run_dir
        self.docs_dir = run_dir / "documents"
        self.docs_dir.mkdir(exist_ok=True)

    def save_document(self, phase: str, template_name: str, content: str):
        """Save phase document."""
        doc_file = self.docs_dir / f"{phase}_{template_name}.md"
        doc_file.write_text(content, encoding="utf-8")

    def load_document(self, phase: str, template_name: str) -> str | None:
        """Load previous phase document."""
        doc_file = self.docs_dir / f"{phase}_{template_name}.md"
        if doc_file.exists():
            return doc_file.read_text(encoding="utf-8")
        return None

    def build_context_from_previous(self, phase: str) -> str:
        """Build context from all previous documents."""
        context = "## Context from Previous Phases:\n\n"

        # Read all documents
        for doc_file in sorted(self.docs_dir.glob("*.md")):
            if doc_file.stem.split('_')[0] < phase:  # Earlier phases
                context += f"### {doc_file.stem}\n"
                content = doc_file.read_text(encoding="utf-8")
                context += content[:500] + "...\n\n"

        return context

    def validate_document(self, template_name: str, content: str) -> dict[str, Any]:
        """Validate document completeness."""
        import re
        required_sections = {
            "product_requirements": ["Problem Statement", "User Stories", "Acceptance Criteria"],
            "architecture_design": ["System Overview", "Components", "Data Flow"],
            "implementation_plan": ["Tasks", "Dependencies", "Timeline"],
            "test_plan": ["Test Cases", "Coverage Requirements", "Expected Results"]
        }

        sections = required_sections.get(template_name, [])
        missing = []

        for section in sections:
            if not re.search(rf'##\s*{re.escape(section)}', content):
                missing.append(section)

        return {
            "valid": len(missing) == 0,
            "missing_sections": missing,
            "completeness": 1.0 - (len(missing) / len(sections)) if sections else 1.0
        }
