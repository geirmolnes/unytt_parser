from unytt_parser.parsers import url_parser
from unytt_parser.parsers.url_parser import _extract_labrador_article
from unytt_parser.models import SourceType


class _DummyMeta:
    title = "Testtittel"
    author = "Byline Navn"
    date = "2026-02-17"
    sitename = "Eksempelavisen"


def test_parse_url_success(monkeypatch):
    monkeypatch.setattr(url_parser.trafilatura, "fetch_url", lambda url, **kwargs: "<html>ok</html>")
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
    monkeypatch.setattr(url_parser.trafilatura, "fetch_url", lambda url, **kwargs: None)

    parsed = url_parser.parse_url("https://example.com/missing", source_id="source-2")

    assert parsed.source_id == "source-2"
    assert parsed.error is not None
    assert "Failed to fetch URL" in parsed.error


def test_parse_url_empty_body_surfaces_error(monkeypatch):
    monkeypatch.setattr(url_parser.trafilatura, "fetch_url", lambda url, **kwargs: "<html>ok</html>")
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
    monkeypatch.setattr(url_parser.trafilatura, "fetch_url", lambda url, **kwargs: labrador_html)
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


def test_parse_url_fetches_with_cloudflare_safe_user_agent(monkeypatch):
    """Regression: arabnews.com (Cloudflare) 403s trafilatura's default UA."""
    seen: dict[str, object] = {}

    def _fetch(url: str, **kwargs):
        seen["config"] = kwargs.get("config")
        return None

    monkeypatch.setattr(url_parser.trafilatura, "fetch_url", _fetch)
    url_parser.parse_url("https://example.com/cloudflare")

    assert seen["config"].get("DEFAULT", "USER_AGENTS") == "Mozilla/5.0"


def test_pdf_probe_sends_same_user_agent(monkeypatch):
    seen: dict[str, object] = {}

    def _urlopen(req, timeout=None):
        seen["ua"] = req.get_header("User-agent")
        raise OSError("offline")

    monkeypatch.setattr(url_parser.urllib.request, "urlopen", _urlopen)
    monkeypatch.setattr(url_parser.trafilatura, "fetch_url", lambda url, **kwargs: None)
    url_parser.parse_url("https://example.com/maybe-pdf")

    assert seen["ua"] == "Mozilla/5.0"
