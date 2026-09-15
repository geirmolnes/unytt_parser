from unytt_parser import parser
from unytt_parser.models import ParsedSource, SourceType
from unytt_parser.parsers import pdf_parser, url_parser
from unytt_parser.parsers.text_parser import parse_text


def test_url_fetch_failure_returns_error(monkeypatch):
    monkeypatch.setattr(url_parser.trafilatura, "fetch_url", lambda url, **kwargs: None)

    parsed = url_parser.parse_url("https://example.com/not-found")

    assert parsed.error is not None
    assert "Failed to fetch URL" in parsed.error


def test_corrupted_pdf_returns_error(monkeypatch):
    def _raise(_):
        raise ValueError("bad pdf")

    monkeypatch.setattr(pdf_parser.pymupdf4llm, "to_markdown", _raise)

    parsed = pdf_parser.parse_pdf("/tmp/corrupted.pdf")

    assert parsed.error is not None
    assert "PDF parsing failed" in parsed.error


def test_empty_text_returns_error():
    parsed = parse_text("")
    assert parsed.error == "Empty text content provided"


def test_parse_sources_never_drops_failing_sources(monkeypatch):
    def _url_fail(source: str, source_id: str | None = None) -> ParsedSource:
        return ParsedSource(
            source_id=source_id or "",
            source_type=SourceType.URL,
            source=source,
            error="Failed to fetch URL",
        )

    def _pdf_fail(source: str, source_id: str | None = None) -> ParsedSource:
        return ParsedSource(
            source_id=source_id or "",
            source_type=SourceType.PDF,
            source=source,
            error="PDF parsing failed",
        )

    def _text_fail(source: str, source_id: str | None = None) -> ParsedSource:
        return ParsedSource(
            source_id=source_id or "",
            source_type=SourceType.TEXT,
            source=source,
            error="Empty text content provided",
        )

    def _markdown_fail(source: str, source_id: str | None = None) -> ParsedSource:
        return ParsedSource(
            source_id=source_id or "",
            source_type=SourceType.MARKDOWN,
            source=source,
            error="Markdown parsing failed",
        )

    monkeypatch.setattr(parser, "parse_url", _url_fail)
    monkeypatch.setattr(parser, "parse_pdf", _pdf_fail)
    monkeypatch.setattr(parser, "parse_text", _text_fail)
    monkeypatch.setattr(parser, "parse_markdown", _markdown_fail)

    bundle = parser.parse_sources(["https://example.com", "/tmp/file.pdf", "/tmp/file.md", "   "])

    assert len(bundle.sources) == 4
    assert all(source.error for source in bundle.sources)
    assert [source.source_id for source in bundle.sources] == ["source-1", "source-2", "source-3", "source-4"]
