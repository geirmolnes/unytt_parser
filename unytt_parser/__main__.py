"""Command-line entrypoint for unytt_parser."""

from __future__ import annotations

import argparse

from unytt_parser import parse_source, parse_sources


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="unytt-parse",
        description="Parse one or more inputs (URL, PDF path, Markdown, or text) to markdown.",
    )
    parser.add_argument(
        "sources",
        nargs="+",
        help="One or more source inputs to parse.",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation width (default: 2).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if len(args.sources) == 1:
        parsed = parse_source(args.sources[0], source_id="source-1")
        print(parsed.model_dump_json(indent=args.indent))
        return 0

    bundle = parse_sources(args.sources)
    print(bundle.model_dump_json(indent=args.indent))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
