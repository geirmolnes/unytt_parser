"""Top-level source parser orchestration."""

from __future__ import annotations

from collections.abc import Iterable

from unytt_parser.models import ParsedSource, SourceBundle, SourceType
from unytt_parser.parsers.markdown_parser import parse_markdown
from unytt_parser.parsers.pdf_parser import parse_pdf
from unytt_parser.parsers.text_parser import parse_text
from unytt_parser.parsers.url_parser import parse_url


def detect_source_type(source_input: str) -> SourceType:
    """Infer source type based on a simple input heuristic."""

    normalized = (source_input or "").strip().lower()
    if normalized.startswith(("http://", "https://")):
        return SourceType.URL
    if normalized.endswith(".pdf"):
        return SourceType.PDF
    if normalized.endswith((".md", ".markdown")):
        return SourceType.MARKDOWN
    return SourceType.TEXT


def parse_source(
    source_input: str, source_id: str | None = None, html: str | None = None
) -> ParsedSource:
    """Parse one source input and return a ParsedSource result.

    `html` is only meaningful for URL inputs: supply the already-downloaded
    page (an authenticated fetch, a cached copy) and the parser will use it
    instead of downloading anonymously.
    """

    source_id = source_id or "source-1"
    raw_input = source_input
    source_type = detect_source_type(raw_input)
    try:
        if source_type == SourceType.URL:
            return parse_url(raw_input, source_id=source_id, html=html)
        if source_type == SourceType.PDF:
            return parse_pdf(raw_input, source_id=source_id)
        if source_type == SourceType.MARKDOWN:
            return parse_markdown(raw_input, source_id=source_id)
        return parse_text(raw_input, source_id=source_id)
    except Exception as exc:
        return ParsedSource(
            source_id=source_id,
            source_type=source_type,
            source=raw_input,
            error=f"Unexpected parser error: {exc}",
        )


def parse_sources(source_inputs: Iterable[str]) -> SourceBundle:
    """Parse multiple source inputs with sequential source IDs."""

    parsed_sources: list[ParsedSource] = []
    for index, source_input in enumerate(source_inputs, start=1):
        parsed_sources.append(parse_source(source_input, source_id=f"source-{index}"))
    return SourceBundle(sources=parsed_sources)
