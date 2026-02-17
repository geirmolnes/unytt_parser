"""Shared utilities for source parsers."""

from __future__ import annotations

import re

HEADING_PATTERN = re.compile(r"^\s*#{1,6}\s+(.+?)\s*$", re.MULTILINE)


def first_markdown_heading(markdown: str) -> str | None:
    """Return the text of the first markdown heading, or None."""
    match = HEADING_PATTERN.search(markdown)
    if not match:
        return None
    heading = match.group(1).strip()
    return heading or None
