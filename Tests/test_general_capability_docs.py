"""Keep the General Skills and General Prompts indexes aligned with source files."""

from __future__ import annotations

import re
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "01-Skills-General"
PROMPTS_ROOT = ROOT / "02-Prompt-General"
SKILLS_PAGE = ROOT / "docs" / "guides" / "General-Skills.md"
PROMPTS_PAGE = ROOT / "docs" / "guides" / "General-Prompts.md"
README = ROOT / "README.md"

ENTRY_PATTERN = re.compile(
    r"^### (?P<title>[^\n]+)\n\n`(?P<technical>[^`]+)`\n"
    r"(?P<body>.*?)^\*\*Source:\*\* \[[^\]]+\]\((?P<source>[^)]+)\)",
    re.MULTILINE | re.DOTALL,
)
LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def _entries(page: Path) -> list[dict[str, str]]:
    return [match.groupdict() for match in ENTRY_PATTERN.finditer(page.read_text(encoding="utf-8"))]


def _resolve_link(page: Path, link: str) -> tuple[Path, str]:
    parsed = urlsplit(link)
    target = (page.parent / unquote(parsed.path)).resolve() if parsed.path else page.resolve()
    return target, unquote(parsed.fragment)


def _heading_anchors(page: Path) -> set[str]:
    headings = re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", page.read_text(encoding="utf-8"), re.MULTILINE)
    anchors = set()
    for heading in headings:
        anchor = re.sub(r"[^\w\- ]", "", heading.casefold()).strip().replace(" ", "-")
        anchors.add(anchor)
    return anchors


class GeneralCapabilityDocumentationTests(unittest.TestCase):
    def test_skills_page_matches_all_skill_masters_in_alphabetical_order(self) -> None:
        sources = sorted(SKILLS_ROOT.glob("*/SKILL.md"), key=lambda path: path.parent.name.casefold())
        page_text = SKILLS_PAGE.read_text(encoding="utf-8")
        entries = _entries(SKILLS_PAGE)

        self.assertEqual(len(entries), 13)
        self.assertEqual(len(entries), len(sources))
        self.assertIn(f"Browse the {len(sources)} Skills", page_text)
        titles = [entry["title"] for entry in entries]
        technical_names = [entry["technical"] for entry in entries]
        self.assertEqual(titles, sorted(titles, key=str.casefold))
        self.assertEqual(len(technical_names), len(set(technical_names)))
        self.assertEqual(set(technical_names), {source.parent.name for source in sources})

        for entry in entries:
            self.assertTrue(all(word[0].isupper() for word in entry["title"].split()))
            for label in ("Description", "When to Use", "How to Use"):
                self.assertIn(f"**{label}:**", entry["body"])
            source, _ = _resolve_link(SKILLS_PAGE, entry["source"])
            self.assertTrue(source.is_file(), entry["source"])
            self.assertEqual(source.name, "SKILL.md")
            self.assertEqual(source.parent.name, entry["technical"])

    def test_prompts_page_matches_all_standalone_prompts_in_alphabetical_order(self) -> None:
        sources = sorted(
            (
                path
                for path in PROMPTS_ROOT.rglob("*")
                if path.is_file()
                and path.name.casefold() != "readme.md"
                and path.suffix.casefold() in {".md", ".txt", ".prompt"}
            ),
            key=lambda path: path.name.casefold(),
        )
        page_text = PROMPTS_PAGE.read_text(encoding="utf-8")
        entries = _entries(PROMPTS_PAGE)

        self.assertEqual(len(entries), 1)
        self.assertEqual(len(entries), len(sources))
        self.assertIn(f"Browse the **{len(sources)} standalone Prompt**", page_text)
        titles = [entry["title"] for entry in entries]
        technical_names = [entry["technical"] for entry in entries]
        self.assertEqual(titles, sorted(titles, key=str.casefold))
        self.assertEqual(len(technical_names), len(set(technical_names)))
        self.assertEqual(set(technical_names), {source.name for source in sources})

        for entry in entries:
            self.assertTrue(all(word[0].isupper() for word in entry["title"].split()))
            for label in ("Description", "When to Use", "How to Use"):
                self.assertIn(f"**{label}:**", entry["body"])
            source, _ = _resolve_link(PROMPTS_PAGE, entry["source"])
            self.assertTrue(source.is_file(), entry["source"])
            self.assertEqual(source.name, entry["technical"])

    def test_index_links_and_navigation_targets_resolve(self) -> None:
        readme = README.read_text(encoding="utf-8")
        self.assertIn('href="#explore-skills-and-prompts"', readme)
        self.assertIn("explore-skills-and-prompts", _heading_anchors(README))
        for index_path in ("docs/guides/General-Skills.md", "docs/guides/General-Prompts.md"):
            self.assertIn(f"]({index_path})", readme)
            self.assertTrue((ROOT / index_path).is_file(), index_path)

        for page in (SKILLS_PAGE, PROMPTS_PAGE):
            page_text = page.read_text(encoding="utf-8")
            self.assertIn("[← Back To Project Home](../../README.md)", page_text)
            anchors = _heading_anchors(page)
            for link in LINK_PATTERN.findall(page_text):
                if link.startswith(("https://", "http://", "mailto:")):
                    continue
                target, fragment = _resolve_link(page, link)
                self.assertTrue(target.exists(), f"{page.name}: {link}")
                if fragment:
                    self.assertIn(fragment, _heading_anchors(target) if target != page else anchors)


if __name__ == "__main__":
    unittest.main()
