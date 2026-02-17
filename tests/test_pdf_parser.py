from unytt_parser.models import SourceType
from unytt_parser.parsers import pdf_parser


def test_parse_pdf_success(monkeypatch):
    markdown = "# PDF Tittel\n\nIngress.\n\nDette er markdowntekst."
    monkeypatch.setattr(pdf_parser.pymupdf4llm, "to_markdown", lambda _: markdown)

    parsed = pdf_parser.parse_pdf("/tmp/test.pdf", source_id="source-5")

    assert parsed.source_id == "source-5"
    assert parsed.source_type == SourceType.PDF
    assert parsed.error is None
    assert parsed.headline == "PDF Tittel"
    assert parsed.markdown == markdown


def test_parse_pdf_corrupted_file(monkeypatch):
    def _raise(_):
        raise RuntimeError("corrupted")

    monkeypatch.setattr(pdf_parser.pymupdf4llm, "to_markdown", _raise)

    parsed = pdf_parser.parse_pdf("/tmp/bad.pdf")

    assert parsed.error is not None
    assert "PDF parsing failed" in parsed.error


def test_parse_pdf_empty_text(monkeypatch):
    monkeypatch.setattr(pdf_parser.pymupdf4llm, "to_markdown", lambda _: "  ")

    parsed = pdf_parser.parse_pdf("/tmp/empty.pdf")

    assert parsed.error is not None
    assert "No text extracted from PDF" in parsed.error
