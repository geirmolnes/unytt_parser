"""Parser for raw text sources."""

from __future__ import annotations

from unytt_parser.models import ParsedSource, SourceType


def parse_text(text: str, source_id: str | None = None) -> ParsedSource:
    """Parse raw text with minimal transformation."""

    source_id = source_id or "source-1"
    raw_text = text
    result = ParsedSource(source_id=source_id, source_type=SourceType.TEXT, source=raw_text)

    if not raw_text.strip():
        result.markdown = raw_text
        result.error = "Empty text content provided"
        return result

    result.markdown = raw_text
    return result
