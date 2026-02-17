"""URL parser using trafilatura for article extraction."""

from __future__ import annotations

from urllib.parse import urlparse

import trafilatura

from src.models import ParsedSource, SourceType


def _metadata_value(metadata: object, key: str) -> str | None:
    if metadata is None:
        return None
    if isinstance(metadata, dict):
        value = metadata.get(key)
    else:
        value = getattr(metadata, key, None)
    if value is None:
        return None
    value_str = str(value).strip()
    return value_str or None


def parse_url(url: str, source_id: str | None = None) -> ParsedSource:
    """Parse one URL into structured source data."""

    source_id = source_id or "source-1"
    result = ParsedSource(source_id=source_id, source_type=SourceType.URL, source=url)
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            result.error = f"Failed to fetch URL: {url}"
            return result

        metadata = None
        try:
            metadata = trafilatura.extract_metadata(downloaded)
        except Exception:
            metadata = None

        markdown = (
            trafilatura.extract(
                downloaded,
                output_format="markdown",
                include_formatting=True,
                include_links=True,
            )
            or ""
        )
        markdown = markdown.strip()

        result.headline = _metadata_value(metadata, "title")
        result.byline = _metadata_value(metadata, "author")
        result.publication_date = _metadata_value(metadata, "date")
        result.publication = (
            _metadata_value(metadata, "sitename")
            or _metadata_value(metadata, "hostname")
            or urlparse(url).netloc
            or None
        )

        if not markdown:
            result.error = f"No article content extracted from URL: {url}"
            return result

        result.markdown = markdown
        return result
    except Exception as exc:
        result.error = f"URL parsing failed for {url}: {exc}"
        return result
