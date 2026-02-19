"""Pydantic models for parsed source data."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class SourceType(str, Enum):
    """Supported source input types."""

    URL = "URL"
    PDF = "PDF"
    MARKDOWN = "MARKDOWN"
    TEXT = "TEXT"


class ParsedSource(BaseModel):
    """Parsed output for one source input."""

    source_id: str
    source_type: SourceType
    source: str
    headline: str | None = None
    byline: str | None = None
    publication_date: str | None = None
    publication: str | None = None
    markdown: str | None = None
    pdf_bytes: bytes | None = None
    error: str | None = None


class SourceBundle(BaseModel):
    """Collection of parsed source outputs."""

    sources: list[ParsedSource] = Field(default_factory=list)
