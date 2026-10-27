from types import SimpleNamespace

import pytest

from unytt_parser.parsers import url_parser
from unytt_parser.parsers.url_parser import _extract_labrador_article
from unytt_parser.models import SourceType


class _DummyMeta:
    title = "Testtittel"
    author = "Byline Navn"
    date = "2026-02-17"
    sitename = "Eksempelavisen"


def test_parse_url_success(monkeypatch):
    monkeypatch.setattr(url_parser, "_fetch_html", lambda url, **kwargs: "<html>ok</html>")
    monkeypatch.setattr(url_parser.trafilatura, "extract_metadata", lambda _: _DummyMeta())
    monkeypatch.setattr(
        url_parser.trafilatura,
        "extract",
        lambda *args, **kwargs: "# Tittel\n\nBrødtekst i markdown.",
    )

    parsed = url_parser.parse_url("https://example.com/article", source_id="source-10")

    assert parsed.source_id == "source-10"
    assert parsed.source_type == SourceType.URL
    assert parsed.error is None
    assert parsed.headline == "Testtittel"
    assert parsed.byline == "Byline Navn"
    assert parsed.publication_date == "2026-02-17"
    assert parsed.publication == "Eksempelavisen"
    assert parsed.markdown == "# Tittel\n\nBrødtekst i markdown."


def test_parse_url_fetch_failure(monkeypatch):
    monkeypatch.setattr(url_parser, "_fetch_html", lambda url, **kwargs: None)

    parsed = url_parser.parse_url("https://example.com/missing", source_id="source-2")

    assert parsed.source_id == "source-2"
    assert parsed.error is not None
    assert "Failed to fetch URL" in parsed.error


def test_parse_url_empty_body_surfaces_error(monkeypatch):
    monkeypatch.setattr(url_parser, "_fetch_html", lambda url, **kwargs: "<html>ok</html>")
    monkeypatch.setattr(url_parser.trafilatura, "extract_metadata", lambda _: _DummyMeta())
    monkeypatch.setattr(url_parser.trafilatura, "extract", lambda *args, **kwargs: "   ")

    parsed = url_parser.parse_url("https://example.com/empty")

    assert parsed.error is not None
    assert "No article content extracted" in parsed.error


def test_extract_labrador_article_isolates_main():
    html = """
    <html><body>
    <script>var labClientAPI = {};</script>
    <section id="mainArticleSection">
      <article><p>Main article content here.</p></article>
    </section>
    <aside>
      <article><p>Sidebar item 1</p></article>
      <article><p>Sidebar item 2</p></article>
    </aside>
    </body></html>
    """
    result = _extract_labrador_article(html)
    assert result is not None
    assert "Main article content here" in result
    assert "Sidebar item" not in result


def test_extract_labrador_article_returns_none_for_non_labrador():
    assert _extract_labrador_article("<html><body>Normal page</body></html>") is None


def test_parse_url_uses_labrador_extraction(monkeypatch):
    labrador_html = """
    <html><body>
    <script>var labClientAPI = {};</script>
    <section id="mainArticleSection">
      <article><p>Real article body.</p></article>
    </section>
    <aside>
      <article><p>Sidebar noise</p></article>
    </aside>
    </body></html>
    """
    monkeypatch.setattr(url_parser, "_fetch_html", lambda url, **kwargs: labrador_html)
    monkeypatch.setattr(url_parser.trafilatura, "extract_metadata", lambda _: _DummyMeta())

    # Use real trafilatura.extract so we verify narrowed HTML is passed
    parsed = url_parser.parse_url("https://example.com/labrador-article")

    assert parsed.error is None
    assert "Sidebar noise" not in (parsed.markdown or "")
    assert "Real article body" in (parsed.markdown or "")


def test_extract_labrador_article_direct_article_tag():
    """Dagbladet-style: <article id='mainArticleSection'> (no wrapping section)."""
    html = """
    <html><body>
    <script>var labClientAPI = {};</script>
    <article id="mainArticleSection"><p>Dagbladet article.</p></article>
    <aside>
      <article><p>Sidebar item</p></article>
    </aside>
    </body></html>
    """
    result = _extract_labrador_article(html)
    assert result is not None
    assert "Dagbladet article" in result
    assert "Sidebar item" not in result


_BARE = "Mozilla/5.0"
_CHROME = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
)
_TRAFILATURA_DEFAULT = ""


@pytest.mark.parametrize(
    "statuses, expected_uas, ok",
    [
        # arabnews.com: bare UA passes, the others 403.
        ([200], [_BARE], True),
        # gemini.no: bare UA 403s, full browser UA passes.
        ([403, 200], [_BARE, _CHROME], True),
        ([403, 403, 200], [_BARE, _CHROME, _TRAFILATURA_DEFAULT], True),
        ([403, 403, 403], [_BARE, _CHROME, _TRAFILATURA_DEFAULT], False),
        ([404], [_BARE], False),
        ([None], [_BARE], False),
    ],
    ids=["200-first", "403-then-200", "403x2-then-200", "all-403", "404-no-retry", "network-error-no-retry"],
)
def test_parse_url_retries_user_agents_only_on_403(monkeypatch, statuses, expected_uas, ok):
    """Regression: gemini.no (Cloudflare) 403s the bare UA that arabnews.com needs."""
    seen_uas: list[str] = []
    replies = iter(statuses)

    def _fetch_response(url: str, **kwargs):
        seen_uas.append(kwargs["config"].get("DEFAULT", "USER_AGENTS"))
        status = next(replies)
        if status is None:
            return None
        return SimpleNamespace(status=status, data=b"<html>x</html>", html="<html>x</html>")

    monkeypatch.setattr(url_parser.urllib.request, "urlopen", _offline)
    monkeypatch.setattr(url_parser, "fetch_response", _fetch_response)
    monkeypatch.setattr(url_parser.trafilatura, "extract_metadata", lambda _: _DummyMeta())
    monkeypatch.setattr(url_parser.trafilatura, "extract", lambda *args, **kwargs: "Brødtekst.")

    parsed = url_parser.parse_url("https://example.com/cloudflare")

    assert seen_uas == expected_uas
    assert parsed.error == (None if ok else "Failed to fetch URL: https://example.com/cloudflare")


def test_parse_url_200_with_empty_body_is_fetch_failure(monkeypatch):
    monkeypatch.setattr(url_parser.urllib.request, "urlopen", _offline)
    monkeypatch.setattr(
        url_parser, "fetch_response", lambda url, **kwargs: SimpleNamespace(status=200, data=b"", html="")
    )

    parsed = url_parser.parse_url("https://example.com/empty-200")

    assert parsed.error == "Failed to fetch URL: https://example.com/empty-200"


def _offline(req, timeout=None):
    raise OSError("offline")


def test_pdf_probe_sends_same_user_agent(monkeypatch):
    seen: dict[str, object] = {}

    def _urlopen(req, timeout=None):
        seen["ua"] = req.get_header("User-agent")
        raise OSError("offline")

    monkeypatch.setattr(url_parser.urllib.request, "urlopen", _urlopen)
    monkeypatch.setattr(url_parser, "_fetch_html", lambda url, **kwargs: None)
    url_parser.parse_url("https://example.com/maybe-pdf")

    assert seen["ua"] == "Mozilla/5.0"
