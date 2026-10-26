"""Perform advisory static checks for a basic accessible HTML document contract."""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re
import sys


class ContractParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.html_lang = False
        self.title = False
        self.viewport = False
        self.landmarks: set[str] = set()
        self.headings: list[int] = []
        self.images_missing_alt = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "html" and values.get("lang"):
            self.html_lang = True
        if tag == "meta" and values.get("name", "").casefold() == "viewport":
            self.viewport = True
        if tag in {"main", "nav", "header", "footer"}:
            self.landmarks.add(tag)
        if tag == "img" and "alt" not in values:
            self.images_missing_alt += 1
        if re.fullmatch(r"h[1-6]", tag):
            self.headings.append(int(tag[1]))

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.title = self.title or self.get_starttag_text() is not None


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: check_html_contract.py PAGE.html", file=sys.stderr)
        return 2
    try:
        source = Path(argv[1]).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"cannot read page: {exc}", file=sys.stderr)
        return 2
    parser = ContractParser()
    parser.feed(source)
    findings: list[str] = []
    if not parser.html_lang:
        findings.append("html lang is missing")
    if "<title" not in source.casefold():
        findings.append("document title is missing")
    if not parser.viewport:
        findings.append("viewport meta is missing")
    if "main" not in parser.landmarks:
        findings.append("main landmark is missing")
    if not parser.headings or parser.headings[0] != 1:
        findings.append("first heading should be h1")
    if any(next_level > current + 1 for current, next_level in zip(parser.headings, parser.headings[1:])):
        findings.append("heading levels skip a level")
    if parser.images_missing_alt:
        findings.append(f"{parser.images_missing_alt} image(s) lack alt")
    if ":focus-visible" not in source:
        findings.append("no :focus-visible rule found; inspect focus styling manually")
    if findings:
        print("WARN\n" + "\n".join(f"- {item}" for item in findings))
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
