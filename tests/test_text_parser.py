from unytt_parser.models import SourceType
from unytt_parser.parsers import text_parser


def test_parse_text_success():
    text = 'Dette er en tekst. "Dette er et sitat", sa Per Hansen.'
    parsed = text_parser.parse_text(text, source_id="source-3")

    assert parsed.source_id == "source-3"
    assert parsed.source_type == SourceType.TEXT
    assert parsed.error is None
    assert parsed.markdown == text


def test_parse_text_empty_content():
    parsed = text_parser.parse_text("   ", source_id="source-4")

    assert parsed.source_type == SourceType.TEXT
    assert parsed.error == "Empty text content provided"
