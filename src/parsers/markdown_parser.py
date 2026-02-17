"""Parser for Markdown sources."""

from __future__ import annotations

from pathlib import Path
import re

from src.models import ParsedSource, SourceType

HEADING_PATTERN = re.compile(r"^\s*#{1,6}\s+(.+?)\s*$", re.MULTILINE)


def _first_markdown_heading(markdown: str) -> str | None:
    match = HEADING_PATTERN.search(markdown)
    if not match:
        return None
    heading = match.group(1).strip()
    return heading or None


def parse_markdown(markdown_input: str, source_id: str | None = None) -> ParsedSource:
    """Parse Markdown text or a Markdown file path."""

    source_id = source_id or "source-1"
    raw_input = markdown_input if isinstance(markdown_input, str) else str(markdown_input)
    result = ParsedSource(source_id=source_id, source_type=SourceType.MARKDOWN, source=raw_input)

    content = raw_input
    normalized = raw_input.strip()
    looks_like_md_path = normalized.lower().endswith((".md", ".markdown"))

    if looks_like_md_path:
        md_path = Path(normalized)
        try:
            content = md_path.read_text(encoding="utf-8")
        except Exception as exc:
            result.error = f"Markdown parsing failed for {raw_input}: {exc}"
            return result

    if not content.strip():
        result.markdown = content
        result.error = "Empty markdown content provided"
        return result

    result.headline = _first_markdown_heading(content)
    result.markdown = content
    return result
