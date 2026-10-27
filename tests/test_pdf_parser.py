from unytt_parser.models import SourceType
from unytt_parser.parsers import pdf_parser


def _fake_pdf(tmp_path, name: str) -> str:
    """parse_pdf reads the file's bytes before extraction, so the path must exist."""
    path = tmp_path / name
    path.write_bytes(b"%PDF-1.4 fake")
    return str(path)


def test_parse_pdf_success(monkeypatch, tmp_path):
    markdown = "# PDF Tittel\n\nIngress.\n\nDette er markdowntekst."
    monkeypatch.setattr(pdf_parser.pymupdf4llm, "to_markdown", lambda _: markdown)

    parsed = pdf_parser.parse_pdf(_fake_pdf(tmp_path, "test.pdf"), source_id="source-5")

    assert parsed.source_id == "source-5"
    assert parsed.source_type == SourceType.PDF
    assert parsed.error is None
    assert parsed.headline == "PDF Tittel"
    assert parsed.markdown == markdown
    assert parsed.pdf_bytes == b"%PDF-1.4 fake"


def test_parse_pdf_corrupted_file(monkeypatch, tmp_path):
    def _raise(_):
        raise RuntimeError("corrupted")

    monkeypatch.setattr(pdf_parser.pymupdf4llm, "to_markdown", _raise)
    path = _fake_pdf(tmp_path, "bad.pdf")

    parsed = pdf_parser.parse_pdf(path)

    assert parsed.error == f"PDF parsing failed for {path}: corrupted"


def test_parse_pdf_empty_text(monkeypatch, tmp_path):
    monkeypatch.setattr(pdf_parser.pymupdf4llm, "to_markdown", lambda _: "  ")
    path = _fake_pdf(tmp_path, "empty.pdf")

    parsed = pdf_parser.parse_pdf(path)

    assert parsed.error == f"No text extracted from PDF: {path}"


def test_parse_pdf_missing_file(tmp_path):
    path = str(tmp_path / "missing.pdf")

    parsed = pdf_parser.parse_pdf(path)

    assert parsed.error.startswith(f"PDF parsing failed for {path}: [Errno 2]")
