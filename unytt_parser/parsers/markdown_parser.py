"""Parser for Markdown sources."""

from __future__ import annotations

from pathlib import Path

from unytt_parser.models import ParsedSource, SourceType
from unytt_parser.parsers.utils import first_markdown_heading


def parse_markdown(markdown_input: str, source_id: str | None = None) -> ParsedSource:
    """Parse Markdown text or a Markdown file path."""

    source_id = source_id or "source-1"
    result = ParsedSource(source_id=source_id, source_type=SourceType.MARKDOWN, source=markdown_input)

    content = markdown_input
    normalized = markdown_input.strip()
    looks_like_md_path = normalized.lower().endswith((".md", ".markdown"))

    if looks_like_md_path:
        md_path = Path(normalized)
        try:
            content = md_path.read_text(encoding="utf-8")
        except Exception as exc:
            result.error = f"Markdown parsing failed for {markdown_input}: {exc}"
            return result

    if not content.strip():
        result.markdown = content
        result.error = "Empty markdown content provided"
        return result

    result.headline = first_markdown_heading(content)
    result.markdown = content
    return result
