"""URL parser using trafilatura for article extraction."""

from __future__ import annotations

from urllib.parse import urlparse

import lxml.html
import trafilatura
from lxml.html import tostring as html_tostring

from unytt_parser.models import ParsedSource, SourceType


def _extract_labrador_article(html: str) -> str | None:
    """Isolate main article from Labrador CMS pages to avoid sidebar noise."""
    if "labClientAPI" not in html:
        return None
    doc = lxml.html.fromstring(html)
    hits = doc.xpath('//*[@id="mainArticleSection"]')
    if not hits:
        return None
    el = hits[0]
    # Dagbladet: <article id="mainArticleSection">
    # Khrono/Utdanningsnytt: <section id="mainArticleSection"><article>...
    if el.tag != "article":
        nested = el.xpath('.//article')
        if not nested:
            return None
        el = nested[0]
    article_html = html_tostring(el, encoding="unicode")
    return f"<html><body>{article_html}</body></html>"


def _metadata_value(metadata: object, key: str) -> str | None:
    """Extract metadata field. Handles dict and object since trafilatura returns different types across versions."""
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

        content_html = _extract_labrador_article(downloaded) or downloaded
        markdown = (
            trafilatura.extract(
                content_html,
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
