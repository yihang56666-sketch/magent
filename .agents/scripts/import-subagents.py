#!/usr/bin/env python3
"""Import MIT-licensed open-source subagent definitions into the local identity bank.

Sources (all MIT-licensed):
  - VoltAgent/awesome-claude-code-subagents (default)

Parses the Claude Code subagent convention (YAML frontmatter + sectioned body)
and maps each role into the local identity schema:
  id, title, keywords, skills, mission, boundaries, output_focus

The importer is idempotent: existing identities are preserved, only new ids are
added. Run with --dry-run first to preview.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import urllib.request
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
IDENTITIES_PATH = ROOT / "skills" / "codex-agent-identity-bank" / "references" / "identities.json"
NOTICE_PATH = ROOT / "skills" / "codex-agent-identity-bank" / "references" / "IMPORT_NOTICE.md"

SOURCES = {
    "volt": {
        "repo": "VoltAgent/awesome-claude-code-subagents",
        "branch": "main",
        "path_prefix": "categories/",
        "license": "MIT",
        "title": "VoltAgent/awesome-claude-code-subagents",
        "url": "https://github.com/VoltAgent/awesome-claude-code-subagents",
    },
}

def _http_get(url: str, timeout: int = 30) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "magent-import/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 (trusted GitHub hosts)
        return response.read().decode("utf-8")


def list_source_files(source: dict) -> list[str]:
    tree_url = f"https://api.github.com/repos/{source['repo']}/git/trees/{source['branch']}?recursive=1"
    tree = json.loads(_http_get(tree_url))
    prefix = source["path_prefix"]
    return [
        node["path"]
        for node in tree.get("tree", [])
        if node["path"].endswith(".md")
        and node["path"].startswith(prefix)
        and not node["path"].endswith("README.md")
    ]


def fetch_raw(source: dict, path: str) -> str:
    raw_url = f"https://raw.githubusercontent.com/{source['repo']}/{source['branch']}/{path}"
    return _http_get(raw_url)


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Split a subagent markdown file into (frontmatter dict, body)."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    raw_front = text[3:end].strip("\n")
    body = text[end + 4 :].lstrip("\n")
    front: dict[str, str] = {}
    for line in raw_front.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        front[key.strip()] = value.strip().strip('"').strip("'")
    return front, body


SECTION_RE = re.compile(r"^([A-Z][A-Za-z0-9 /&,'+-]{2,40}):\s*$")
STOPWORDS = {
    "the", "and", "for", "with", "you", "are", "use", "this", "agent", "when",
    "your", "that", "from", "into", "based", "need", "needs", "data", "team",
    "across", "while", "their", "have", "will", "make", "build", "using",
    "expertise", "focus", "emphasis", "senior", "expert", "specialist", "master",
    "specializing", "specialized", "deep", "modern", "best", "high", "real",
    # generic process/filler words that pollute routing across many roles
    "optimize", "optimization", "management", "manage", "checklist", "context",
    "patterns", "pattern", "tools", "tool", "maintenance", "collaboration",
    "strategies", "strategy", "project", "projects", "repository", "establish",
    "design", "develop", "development", "implement", "implementation", "create",
    "review", "analyze", "analysis", "assess", "ensure", "improve", "tracking",
    "progress", "excellence", "delivery", "integration", "approach", "priorities",
    "execute", "comprehensive", "systematic", "phases", "scope", "quality",
    "performance", "production", "advanced", "support", "various", "including",
}

# section titles that every VoltAgent file shares — no routing signal
BOILERPLATE_SECTIONS = {
    "when invoked",
    "integration with other agents",
}


def _is_boilerplate_section(title: str) -> bool:
    if title in BOILERPLATE_SECTIONS:
        return True
    return any(
        marker in title
        for marker in ("checklist", "tracking", "notification", "context query", "priorities", "approach")
    )


def _section_topics(body: str) -> dict[str, list[str]]:
    """Return {section_title: [list items]} for sectioned subagent bodies.

    Captures both bullet items ("- foo") and numbered steps ("1. foo").
    """
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in body.splitlines():
        match = SECTION_RE.match(line.strip())
        if match:
            current = match.group(1).strip().lower()
            sections[current] = []
            continue
        stripped = line.strip()
        if not current:
            continue
        if stripped.startswith(("- ", "* ")):
            sections[current].append(stripped[2:].strip())
        else:
            numbered = re.match(r"^\d+\.\s+(.*)", stripped)
            if numbered:
                sections[current].append(numbered.group(1).strip())
    return sections


def _first_paragraph(body: str) -> str:
    lines: list[str] = []
    for line in body.splitlines():
        if line.strip():
            lines.append(line.strip())
        elif lines:
            break
    return " ".join(lines)


def _derive_keywords(name: str, description: str, sections: dict[str, list[str]]) -> list[str]:
    keywords: list[str] = []
    seen: set[str] = set()

    def add(token: str) -> None:
        token = token.strip().lower().strip(".,;:!?()[]{}\"'")
        token = re.sub(r"[^a-z0-9+#.-]", "", token).strip(".-")
        if len(token) < 3 or token in STOPWORDS or token in seen:
            return
        seen.add(token)
        keywords.append(token)

    for part in name.split("-"):
        add(part)
    add(name.replace("-", ""))
    for word in re.findall(r"[A-Za-z][A-Za-z0-9+#.-]{2,}", description):
        add(word)
    # section titles carry the strongest domain signal
    for title in list(sections.keys())[:14]:
        if _is_boilerplate_section(title):
            continue
        for word in title.replace("/", " ").replace("&", " ").split():
            add(word)
    return keywords[:24]


def _derive_skills(name: str, tools: str, sections: dict[str, list[str]]) -> list[str]:
    skills: list[str] = []
    seen: set[str] = set()

    def add(token: str) -> None:
        token = token.strip().lower().strip(".,;:!?()[]{}\"'")
        token = re.sub(r"[^a-z0-9+#.-]", "", token).strip(".-")
        if len(token) < 2 or token in STOPWORDS or token in seen:
            return
        seen.add(token)
        skills.append(token)

    add(name.split("-")[-1])
    # domain skills from section headers, skipping generic process sections
    for title in sections:
        if _is_boilerplate_section(title):
            continue
        words = title.replace("/", " ").replace("&", " ").split()
        if words:
            add(words[0])
    add("workflow")
    return skills[:8]


def _derive_boundaries(title: str) -> list[str]:
    return [
        f"Operate strictly within the {title} remit; defer cross-domain calls to the main agent.",
        "Advisory only unless the main agent explicitly delegates write authority.",
        "Do not claim final completion; report evidence and a recommended next action.",
    ]


def _derive_output_focus(sections: dict[str, list[str]]) -> list[str]:
    invoked = sections.get("when invoked", [])
    focus = [item for item in invoked[:4]]
    if not focus:
        # fall back to the first concrete topic section
        for title, items in sections.items():
            if title not in {"when invoked"} and items:
                focus = items[:4]
                break
    focus.append("evidence with file or source references")
    return focus[:6]


def map_to_identity(front: dict[str, str], body: str, source: dict) -> dict[str, Any] | None:
    name = front.get("name", "").strip()
    if not name or not re.fullmatch(r"[a-z0-9-]+", name):
        return None
    description = front.get("description", "").strip()
    tools = front.get("tools", "")
    sections = _section_topics(body)
    title = " ".join(word.capitalize() for word in name.split("-"))
    mission = _first_paragraph(body) or description or f"Act as a bounded {title} specialist."
    mission = re.sub(r"^You are an?\s+", "", mission)
    mission = mission[:400].rstrip()

    return {
        "id": name,
        "title": title,
        "keywords": _derive_keywords(name, description, sections),
        "skills": _derive_skills(name, tools, sections),
        "mission": mission,
        "boundaries": _derive_boundaries(title),
        "output_focus": _derive_output_focus(sections),
        "_source": source["title"],
    }


def load_existing() -> dict[str, Any]:
    return json.loads(IDENTITIES_PATH.read_text(encoding="utf-8"))


def validate_identity(identity: dict[str, Any]) -> list[str]:
    problems = []
    for field in ("id", "title", "keywords", "skills", "mission", "boundaries", "output_focus"):
        value = identity.get(field)
        if not value:
            problems.append(f"{identity.get('id', '?')}: empty {field}")
    return problems


def merge_identities(existing: dict[str, Any], imported: list[dict[str, Any]]) -> tuple[list[dict], list[str], list[str]]:
    current = existing["identities"]
    current_ids = {item["id"] for item in current}
    added: list[str] = []
    skipped: list[str] = []
    seen_new: set[str] = set()
    result = list(current)

    for identity in imported:
        ident_id = identity["id"]
        if ident_id in current_ids or ident_id in seen_new:
            skipped.append(ident_id)
            continue
        problems = validate_identity(identity)
        if problems:
            skipped.append(f"{ident_id} (invalid)")
            continue
        seen_new.add(ident_id)
        added.append(ident_id)
        result.append(identity)
    return result, added, skipped


def write_notice(sources_used: list[dict], added_count: int) -> None:
    lines = [
        "# Imported Identity Attribution",
        "",
        "Some identities in `identities.json` were derived from MIT-licensed",
        "open-source subagent collections. Original authors retain copyright;",
        "the MIT license permits reuse with attribution.",
        "",
        "Each imported identity carries a `_source` field naming its origin.",
        "",
        "## Sources",
        "",
    ]
    for source in sources_used:
        lines.append(f"- [{source['title']}]({source['url']}) — License: {source['license']}")
    lines.extend(["", f"Last import added {added_count} new identities.", ""])
    NOTICE_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", choices=sorted(SOURCES), default="volt", help="Which open-source collection to import")
    parser.add_argument("--max", type=int, default=0, help="Max new identities to import (0 = no limit)")
    parser.add_argument("--categories", default="", help="Comma-separated path substrings to include (e.g. 08-business,10-research)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()

    source = SOURCES[args.source]
    logger.info(f"Listing files from {source['repo']} ({source['license']})...")
    try:
        paths = list_source_files(source)
    except Exception as exc:
        logger.error(f"Failed to list source files: {exc}")
        return 1

    if args.categories:
        wanted = [chunk.strip() for chunk in args.categories.split(",") if chunk.strip()]
        paths = [path for path in paths if any(chunk in path for chunk in wanted)]

    logger.info(f"Found {len(paths)} candidate files")
    imported: list[dict[str, Any]] = []
    for path in paths:
        try:
            front, body = parse_frontmatter(fetch_raw(source, path))
            identity = map_to_identity(front, body, source)
            if identity:
                imported.append(identity)
        except Exception as exc:
            logger.warning(f"Skipped {path}: {exc}")

    logger.info(f"Parsed {len(imported)} identities from source")

    existing = load_existing()
    merged, added, skipped = merge_identities(existing, imported)

    if args.max and len(added) > args.max:
        keep = set(added[: args.max])
        merged = [item for item in merged if item["id"] not in set(added) - keep]
        added = added[: args.max]

    logger.info(f"New: {len(added)} | Skipped (existing/invalid): {len(skipped)} | Total after merge: {len(merged)}")
    if added:
        logger.info("Added: " + ", ".join(added[:40]) + (" ..." if len(added) > 40 else ""))

    if args.dry_run:
        logger.info("Dry run — no files written")
        return 0

    existing["identities"] = merged
    IDENTITIES_PATH.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_notice([source], len(added))
    logger.info(f"Wrote {IDENTITIES_PATH}")
    logger.info(f"Wrote {NOTICE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
