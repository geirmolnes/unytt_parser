"""PDF parser using pymupdf4llm Markdown extraction."""

from __future__ import annotations

import re

import pymupdf4llm

from src.models import ParsedSource, SourceType

HEADING_PATTERN = re.compile(r"^\s*#{1,6}\s+(.+?)\s*$", re.MULTILINE)


def _first_markdown_heading(markdown: str) -> str | None:
    match = HEADING_PATTERN.search(markdown)
    if not match:
        return None
    heading = match.group(1).strip()
    return heading or None


def parse_pdf(pdf_path: str, source_id: str | None = None) -> ParsedSource:
    """Parse one PDF file path into structured source data."""

    source_id = source_id or "source-1"
    result = ParsedSource(source_id=source_id, source_type=SourceType.PDF, source=pdf_path)
    try:
        markdown = pymupdf4llm.to_markdown(pdf_path) or ""
        markdown = markdown.strip()
        if not markdown:
            result.error = f"No text extracted from PDF: {pdf_path}"
            return result

        result.headline = _first_markdown_heading(markdown)
        result.markdown = markdown
        return result
    except Exception as exc:
        result.error = f"PDF parsing failed for {pdf_path}: {exc}"
        return result
