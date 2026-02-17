from src import parser
from src.models import ParsedSource, SourceType


def _mk(source_id: str, source_type: SourceType, source: str) -> ParsedSource:
    return ParsedSource(source_id=source_id, source_type=source_type, source=source, markdown="ok")


def test_detect_source_type():
    assert parser.detect_source_type("https://example.com") == SourceType.URL
    assert parser.detect_source_type("HTTP://example.com") == SourceType.URL
    assert parser.detect_source_type("/tmp/doc.PDF") == SourceType.PDF
    assert parser.detect_source_type("/tmp/readme.md") == SourceType.MARKDOWN
    assert parser.detect_source_type("plain text") == SourceType.TEXT


def test_parse_source_dispatches_to_url(monkeypatch):
    monkeypatch.setattr(parser, "parse_url", lambda source, source_id=None: _mk(source_id or "", SourceType.URL, source))

    parsed = parser.parse_source("https://example.com", source_id="source-1")

    assert parsed.source_type == SourceType.URL
    assert parsed.source_id == "source-1"


def test_parse_source_dispatches_to_pdf(monkeypatch):
    monkeypatch.setattr(parser, "parse_pdf", lambda source, source_id=None: _mk(source_id or "", SourceType.PDF, source))

    parsed = parser.parse_source("/tmp/file.pdf", source_id="source-2")

    assert parsed.source_type == SourceType.PDF
    assert parsed.source_id == "source-2"


def test_parse_source_dispatches_to_text(monkeypatch):
    monkeypatch.setattr(parser, "parse_text", lambda source, source_id=None: _mk(source_id or "", SourceType.TEXT, source))

    parsed = parser.parse_source("raw text", source_id="source-3")

    assert parsed.source_type == SourceType.TEXT
    assert parsed.source_id == "source-3"


def test_parse_source_dispatches_to_markdown(monkeypatch):
    monkeypatch.setattr(
        parser,
        "parse_markdown",
        lambda source, source_id=None: _mk(source_id or "", SourceType.MARKDOWN, source),
    )

    parsed = parser.parse_source("/tmp/readme.md", source_id="source-4")

    assert parsed.source_type == SourceType.MARKDOWN
    assert parsed.source_id == "source-4"


def test_parse_sources_assigns_sequential_ids(monkeypatch):
    monkeypatch.setattr(parser, "parse_source", lambda source, source_id=None: _mk(source_id or "", SourceType.TEXT, source))

    bundle = parser.parse_sources(["a", "b", "c"])

    assert len(bundle.sources) == 3
    assert [src.source_id for src in bundle.sources] == ["source-1", "source-2", "source-3"]
    assert [src.source for src in bundle.sources] == ["a", "b", "c"]
