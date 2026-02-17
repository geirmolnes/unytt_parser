from pathlib import Path

from unytt_parser.models import SourceType
from unytt_parser.parsers import markdown_parser


def test_parse_markdown_from_file(tmp_path: Path):
    md_file = tmp_path / "article.md"
    md_file.write_text('# Tittel\n\n"Dette er viktig", sier Kari Nordmann.', encoding="utf-8")

    parsed = markdown_parser.parse_markdown(str(md_file), source_id="source-7")

    assert parsed.source_id == "source-7"
    assert parsed.source_type == SourceType.MARKDOWN
    assert parsed.error is None
    assert parsed.headline == "Tittel"
    assert parsed.markdown == '# Tittel\n\n"Dette er viktig", sier Kari Nordmann.'


def test_parse_markdown_raw_text():
    markdown = "## Undertittel\n\n'Et sitat', sa Per Hansen."

    parsed = markdown_parser.parse_markdown(markdown, source_id="source-8")

    assert parsed.source_type == SourceType.MARKDOWN
    assert parsed.error is None
    assert parsed.headline == "Undertittel"
    assert parsed.markdown == markdown


def test_parse_markdown_missing_file_surfaces_error():
    parsed = markdown_parser.parse_markdown("/tmp/does-not-exist.md")

    assert parsed.error is not None
    assert "Markdown parsing failed" in parsed.error


def test_parse_markdown_empty_content_error():
    parsed = markdown_parser.parse_markdown("   ")

    assert parsed.source_type == SourceType.MARKDOWN
    assert parsed.error == "Empty markdown content provided"
