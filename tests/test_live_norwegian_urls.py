from __future__ import annotations

import os

import pytest

from unytt_parser.models import SourceType
from unytt_parser.parsers.url_parser import parse_url

LIVE_TEST_ENV_VAR = "UNYTT_RUN_LIVE_URL_TESTS"
ARTICLE_MIN_MARKDOWN_LEN = 300

LIVE_ARTICLE_URLS = {
    "vg": [
        "https://www.vg.no/nyheter/i/RjrXJ5/kvinnens-far-vitner-fortalte-om-moetet-med-prinsen",
        "https://www.vg.no/nyheter/i/n1WJqL/raadyrene-i-botanisk-hage-flyttet-til-toeyenparken-i-oslo",
    ],
    "nrk": [
        "https://www.nrk.no/nordland/hydrogenferger-til-lofoten-forsinka-_-torghatten-nord-taper-flere-titalls-millioner-1.17749490",
        "https://www.nrk.no/norge/krf-vil-skrote-nye-rad-om-moter-med-kjonnsmangfold-1.17772139",
    ],
    "dagbladet": [
        "https://www.dagbladet.no/nyheter/kvinnens-far-veldig-mye-sinne/84246984",
        "https://www.dagbladet.no/nyheter/han-er-borte-om-tre-ar/84239732",
    ],
    "khrono": [
        "https://khrono.no/professor-mot-professor-pa-nhh-leverte-varsel-etter-debatt-om-skatt/1038053",
        "https://khrono.no/mange-bekymret-for-sine-doktorgradsprogrammer/1037388",
    ],
}

pytestmark = pytest.mark.skipif(
    os.getenv(LIVE_TEST_ENV_VAR) != "1",
    reason=f"Live URL tests disabled. Set {LIVE_TEST_ENV_VAR}=1 to run them.",
)


def _find_first_parseable_article(article_urls: list[str]) -> tuple[str, object] | None:
    for article_url in article_urls:
        parsed = parse_url(article_url)
        if parsed.error is not None:
            continue
        markdown = (parsed.markdown or "").strip()
        if len(markdown) < ARTICLE_MIN_MARKDOWN_LEN:
            continue
        return article_url, parsed
    return None


@pytest.mark.parametrize("source_name,article_urls", LIVE_ARTICLE_URLS.items())
def test_parse_live_norwegian_news_articles(source_name: str, article_urls: list[str]):
    result = _find_first_parseable_article(article_urls)
    assert result is not None, f"Could not parse any configured live article for {source_name}"

    article_url, parsed = result
    assert parsed.source_type == SourceType.URL
    assert parsed.error is None, f"Unexpected parse failure for {source_name}: {article_url}"
    assert parsed.publication is not None
    assert parsed.markdown is not None
    assert len(parsed.markdown.strip()) >= ARTICLE_MIN_MARKDOWN_LEN
