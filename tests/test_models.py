from src.models import ParsedSource, SourceBundle, SourceType


def test_source_type_enum_values():
    assert SourceType.URL.value == "URL"
    assert SourceType.PDF.value == "PDF"
    assert SourceType.MARKDOWN.value == "MARKDOWN"
    assert SourceType.TEXT.value == "TEXT"


def test_models_can_be_composed():
    source = ParsedSource(
        source_id="source-1",
        source_type=SourceType.TEXT,
        source="Hei",
        markdown="# Hei\n\nDette er tekst.",
    )
    bundle = SourceBundle(sources=[source])

    assert bundle.sources[0].source_id == "source-1"
    assert bundle.sources[0].markdown == "# Hei\n\nDette er tekst."
