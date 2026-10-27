"""Shared utilities for source parsers."""

from __future__ import annotations

import re

HEADING_PATTERN = re.compile(r"^\s*#{1,6}\s+(.+?)\s*$", re.MULTILINE)
# pymupdf's layout mode wraps headings in bold, e.g. "## **Innledning**".
_STRONG_MARKERS = re.compile(r"\*\*|__")


def first_markdown_heading(markdown: str) -> str | None:
    """Return the text of the first markdown heading, or None."""
    match = HEADING_PATTERN.search(markdown)
    if not match:
        return None
    heading = _STRONG_MARKERS.sub("", match.group(1)).strip()
    return heading or None
