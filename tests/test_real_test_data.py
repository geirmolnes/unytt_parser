from __future__ import annotations

import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from src import parser
from src.models import SourceType

TEST_DATA_DIR = Path(__file__).parent / "test_data"


class _FixtureRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(TEST_DATA_DIR), **kwargs)

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return None


@pytest.fixture()
def fixture_http_base_url() -> str:
    server = ThreadingHTTPServer(("127.0.0.1", 0), _FixtureRequestHandler)
    host, port = server.server_address

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_parse_source_with_real_url_fixture(fixture_http_base_url: str):
    source_input = f"{fixture_http_base_url}/url_article.html"

    parsed = parser.parse_source(source_input, source_id="source-url")

    assert parsed.source_type == SourceType.URL
    assert parsed.error is None
    assert parsed.headline == "Kommunen åpner ny skole"
    assert parsed.byline == "Kari Nordmann"
    assert parsed.publication_date == "2026-02-10"
    assert parsed.publication == "Lokalsamfunnsnytt"
    assert "Ordføreren klippet snoren" in (parsed.markdown or "")


def test_parse_source_with_real_pdf_fixture():
    source_input = str(TEST_DATA_DIR / "article.pdf")

    parsed = parser.parse_source(source_input, source_id="source-pdf")

    assert parsed.source_type == SourceType.PDF
    assert parsed.error is None
    assert parsed.headline == "Nytt kulturhus åpnet"
    assert "Arrangementet fortsatte med konserter" in (parsed.markdown or "")


def test_parse_source_with_real_markdown_fixture():
    source_input = str(TEST_DATA_DIR / "article.md")

    parsed = parser.parse_source(source_input, source_id="source-md")

    assert parsed.source_type == SourceType.MARKDOWN
    assert parsed.error is None
    assert parsed.headline == "Nytt kulturhus åpnet"
    assert "## Reaksjoner" in (parsed.markdown or "")


def test_parse_source_with_real_text_fixture():
    source_input = (TEST_DATA_DIR / "article.txt").read_text(encoding="utf-8")

    parsed = parser.parse_source(source_input, source_id="source-text")

    assert parsed.source_type == SourceType.TEXT
    assert parsed.error is None
    assert "kulturhuset åpnet" in (parsed.markdown or "")


def test_parse_sources_with_real_fixture_set(fixture_http_base_url: str):
    text_input = (TEST_DATA_DIR / "article.txt").read_text(encoding="utf-8")
    source_inputs = [
        f"{fixture_http_base_url}/url_article.html",
        str(TEST_DATA_DIR / "article.pdf"),
        str(TEST_DATA_DIR / "article.md"),
        text_input,
    ]

    bundle = parser.parse_sources(source_inputs)

    assert len(bundle.sources) == 4
    assert [source.source_id for source in bundle.sources] == ["source-1", "source-2", "source-3", "source-4"]
    assert [source.source_type for source in bundle.sources] == [
        SourceType.URL,
        SourceType.PDF,
        SourceType.MARKDOWN,
        SourceType.TEXT,
    ]
    assert all(source.error is None for source in bundle.sources)
