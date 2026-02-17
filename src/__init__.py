"""Top-level package for source parsing."""

from src.models import ParsedSource, SourceBundle, SourceType
from src.parser import detect_source_type, parse_source, parse_sources

__all__ = [
    "ParsedSource",
    "SourceBundle",
    "SourceType",
    "detect_source_type",
    "parse_source",
    "parse_sources",
]
