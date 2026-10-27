"""PDF parser using pymupdf4llm Markdown extraction."""

from __future__ import annotations

from pathlib import Path

# Importing pymupdf.layout before pymupdf4llm switches to_markdown to the ML
# layout engine: real markdown tables and headings instead of flattened text.
# Trade-off: it drops hyperlinks and is ~2x slower.
import pymupdf.layout  # noqa: F401
import pymupdf4llm

from unytt_parser.models import ParsedSource, SourceType
from unytt_parser.parsers.utils import first_markdown_heading


def parse_pdf(pdf_path: str, source_id: str | None = None) -> ParsedSource:
    """Parse one PDF file path into structured source data."""

    source_id = source_id or "source-1"
    result = ParsedSource(source_id=source_id, source_type=SourceType.PDF, source=pdf_path)
    try:
        result.pdf_bytes = Path(pdf_path).read_bytes()
        markdown = pymupdf4llm.to_markdown(pdf_path) or ""
        markdown = markdown.strip()
        if not markdown:
            result.error = f"No text extracted from PDF: {pdf_path}"
            return result

        result.headline = first_markdown_heading(markdown)
        result.markdown = markdown
        return result
    except Exception as exc:
        result.error = f"PDF parsing failed for {pdf_path}: {exc}"
        return result
