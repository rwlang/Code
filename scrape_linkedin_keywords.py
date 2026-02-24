#!/usr/bin/env python3
"""Scrape a website and extract candidate keywords for LinkedIn audience targeting."""

from __future__ import annotations

import argparse
import collections
import html
import re
import urllib.error
import urllib.request
from html.parser import HTMLParser
from typing import Iterable

STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "as", "at",
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
    "can", "cannot", "could",
    "did", "do", "does", "doing", "down", "during",
    "each",
    "few", "for", "from", "further",
    "had", "has", "have", "having", "he", "her", "here", "hers", "herself", "him", "himself", "his", "how",
    "i", "if", "in", "into", "is", "it", "its", "itself",
    "just",
    "me", "more", "most", "my", "myself",
    "no", "nor", "not", "now",
    "of", "off", "on", "once", "only", "or", "other", "our", "ours", "ourselves", "out", "over", "own",
    "same", "she", "should", "so", "some", "such",
    "than", "that", "the", "their", "theirs", "them", "themselves", "then", "there", "these", "they", "this", "those", "through", "to", "too",
    "under", "until", "up",
    "very",
    "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom", "why", "will", "with", "you", "your", "yours", "yourself", "yourselves",
}

WORD_RE = re.compile(r"[A-Za-z][A-Za-z\-']{2,}")


class VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._skip_stack: list[str] = []
        self._chunks: list[str] = []
        self.title_parts: list[str] = []
        self.meta_description = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag in {"script", "style", "noscript", "svg", "img", "footer", "header"}:
            self._skip_stack.append(tag)
        if tag == "meta" and attrs_dict.get("name", "").lower() == "description":
            self.meta_description = attrs_dict.get("content") or self.meta_description

    def handle_endtag(self, tag: str) -> None:
        if self._skip_stack and self._skip_stack[-1] == tag:
            self._skip_stack.pop()

    def handle_data(self, data: str) -> None:
        if self._skip_stack:
            return
        text = data.strip()
        if not text:
            return
        self._chunks.append(text)

    @property
    def text(self) -> str:
        return " ".join(self._chunks)


def fetch_html(url: str, timeout: int = 20) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/123.0 Safari/537.36"
            )
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def extract_visible_text(page_html: str) -> str:
    parser = VisibleTextParser()
    parser.feed(page_html)
    parser.close()
    combined = " ".join(part for part in [parser.meta_description, parser.text] if part)
    return html.unescape(combined)


def tokenize(text: str) -> Iterable[str]:
    for token in WORD_RE.findall(text.lower()):
        token = token.strip("-'")
        if len(token) < 3 or token in STOPWORDS or token.isdigit():
            continue
        yield token


def extract_keywords(text: str, top_n: int = 30) -> list[tuple[str, int]]:
    counts = collections.Counter(tokenize(text))
    return counts.most_common(top_n)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape one website and output frequent keywords for LinkedIn campaign audience research."
    )
    parser.add_argument("url", help="Website URL to scrape (e.g. https://example.com)")
    parser.add_argument("--top", type=int, default=30, help="Number of keywords to display")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        page_html = fetch_html(args.url)
    except urllib.error.URLError as exc:
        print(f"Error fetching URL: {exc}")
        return 1

    text = extract_visible_text(page_html)
    keywords = extract_keywords(text, top_n=args.top)

    if not keywords:
        print("No keywords found. Try another page.")
        return 0

    print(f"Top {len(keywords)} keywords for LinkedIn audience ideas from {args.url}:\n")
    for idx, (word, count) in enumerate(keywords, start=1):
        print(f"{idx:>2}. {word:<25} {count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
