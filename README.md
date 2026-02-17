# unytt_parser

Lightweight source parser for URLs, PDFs, Markdown files, and raw text.

## Current Scope

The parser currently focuses on one core output: Markdown-formatted text.

- No quote extraction
- No LLM dependency
- Deterministic parsing behavior

## Features

- Auto-detect source type (`URL`, `PDF`, `MARKDOWN`, `TEXT`)
- Return parsed markdown in `ParsedSource.markdown`
- Keep metadata when available (`headline`, `byline`, `publication_date`, `publication`)
- Surface clear errors without dropping sources

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/)

## Install

```bash
uv sync
```

## Use In Another Project (Editable)

Use this while the API is still changing:

```bash
uv add --editable /Users/geirmolnes/unytt/unytt_parser
```

## Project Structure

```text
unytt_parser/
  models.py                 # Pydantic models and enums
  parser.py                 # Top-level parse_source / parse_sources
  __main__.py               # CLI entrypoint (unytt-parse)
  parsers/
    url_parser.py           # URL parsing with trafilatura -> markdown
    pdf_parser.py           # PDF parsing with pymupdf4llm -> markdown
    markdown_parser.py      # Markdown input (file path or raw markdown string)
    text_parser.py          # Raw text passthrough as markdown
tests/
```

## Output

`parse_source()` returns a `ParsedSource`, `parse_sources()` returns a `SourceBundle`.

```python
class ParsedSource:
    source_id: str            # caller-provided; defaults to "source-1"
    source_type: SourceType   # URL | PDF | MARKDOWN | TEXT
    source: str               # original input string
    headline: str | None      # first heading or extracted title
    byline: str | None        # author (URL only, via trafilatura)
    publication_date: str | None  # date (URL only, via trafilatura)
    publication: str | None   # site name (URL only, via trafilatura)
    markdown: str | None      # full content converted to markdown
    error: str | None         # error message if parsing failed

class SourceBundle:
    sources: list[ParsedSource]  # parse_sources() uses source-1..source-N
```

Metadata fields (`byline`, `publication_date`, `publication`) are only populated for URL sources. `headline` is extracted from the first markdown heading for PDF/Markdown sources, or from trafilatura metadata for URLs. On parse failures, `error` is set and `markdown` is usually `None` (for empty text/markdown input, the original empty content is preserved in `markdown`).

Example `parse_source("plain text input")` output:

```json
{
  "source_id": "source-1",
  "source_type": "TEXT",
  "source": "plain text input",
  "headline": null,
  "byline": null,
  "publication_date": null,
  "publication": null,
  "markdown": "plain text input",
  "error": null
}
```

Example `parse_sources(["a", "b"])` output shape:

```json
{
  "sources": [
    {
      "source_id": "source-1",
      "source_type": "TEXT",
      "source": "a",
      "headline": null,
      "byline": null,
      "publication_date": null,
      "publication": null,
      "markdown": "a",
      "error": null
    },
    {
      "source_id": "source-2",
      "source_type": "TEXT",
      "source": "b",
      "headline": null,
      "byline": null,
      "publication_date": null,
      "publication": null,
      "markdown": "b",
      "error": null
    }
  ]
}
```

## Quick Usage

```python
from unytt_parser import parse_source, parse_sources

# Single input
single = parse_source("https://example.com/article")
print(single.source_type, single.markdown, single.error)

# Mixed inputs
bundle = parse_sources([
    "https://example.com/article",
    "/path/to/document.pdf",
    "/path/to/notes.md",
    "Plain text input that is returned as markdown text.",
])

for item in bundle.sources:
    print(item.source_id, item.source_type, bool(item.markdown), item.error)
```

## CLI Usage

After install/sync:

```bash
uv run unytt-parse "https://example.com/article"
uv run unytt-parse "/tmp/article.pdf" "/tmp/notes.md" "plain text source"
```

## Source-Type Detection

- Starts with `http://` or `https://` -> `URL`
- Ends with `.pdf` (case-insensitive) -> `PDF`
- Ends with `.md` or `.markdown` (case-insensitive) -> `MARKDOWN`
- Otherwise -> `TEXT`

## Error Handling

Each input always returns one `ParsedSource` object:

- Failed URL fetch -> `error` is set
- Empty URL extraction -> `error` is set
- Corrupted/unreadable PDF -> `error` is set
- Missing/unreadable Markdown file -> `error` is set
- Empty text/markdown input -> `error` is set

This preserves input/output alignment for `parse_sources()`.

## Run Tests

```bash
uv run pytest
```

Or run targeted suites:

```bash
uv run pytest tests/test_models.py
uv run pytest tests/test_url_parser.py
uv run pytest tests/test_pdf_parser.py
uv run pytest tests/test_markdown_parser.py
uv run pytest tests/test_text_parser.py
uv run pytest tests/test_parser.py
uv run pytest tests/test_error_handling.py
```
