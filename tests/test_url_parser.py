from src.parsers import url_parser
from src.models import SourceType


class _DummyMeta:
    title = "Testtittel"
    author = "Byline Navn"
    date = "2026-02-17"
    sitename = "Eksempelavisen"


def test_parse_url_success(monkeypatch):
    monkeypatch.setattr(url_parser.trafilatura, "fetch_url", lambda _: "<html>ok</html>")
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
    monkeypatch.setattr(url_parser.trafilatura, "fetch_url", lambda _: None)

    parsed = url_parser.parse_url("https://example.com/missing", source_id="source-2")

    assert parsed.source_id == "source-2"
    assert parsed.error is not None
    assert "Failed to fetch URL" in parsed.error


def test_parse_url_empty_body_surfaces_error(monkeypatch):
    monkeypatch.setattr(url_parser.trafilatura, "fetch_url", lambda _: "<html>ok</html>")
    monkeypatch.setattr(url_parser.trafilatura, "extract_metadata", lambda _: _DummyMeta())
    monkeypatch.setattr(url_parser.trafilatura, "extract", lambda *args, **kwargs: "   ")

    parsed = url_parser.parse_url("https://example.com/empty")

    assert parsed.error is not None
    assert "No article content extracted" in parsed.error
