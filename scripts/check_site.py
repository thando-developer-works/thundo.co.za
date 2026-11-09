#!/usr/bin/env python3
"""Check static portfolio pages using only the Python standard library.

Usage: python3 check_site.py /path/to/site
This checks source markup and local references; it is not a browser or a full
HTML conformance/accessibility validator and does not contact external sites.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


IGNORED_DIRECTORIES = {".git", "node_modules", ".venv", "venv", "__pycache__"}


@dataclass
class Page:
    path: Path
    ids: Counter = field(default_factory=Counter)
    references: list[tuple[int, str, str]] = field(default_factory=list)
    issues: list[tuple[int, str]] = field(default_factory=list)
    headings: int = 0
    landmarks: int = 0
    titles: list[str] = field(default_factory=list)
    descriptions: list[str] = field(default_factory=list)


class PageParser(HTMLParser):
    def __init__(self, page: Page):
        super().__init__(convert_charrefs=True)
        self.page = page
        self.title_parts: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        attributes = dict(attrs)
        line, _ = self.getpos()
        page = self.page
        identifier = attributes.get("id")
        if identifier is not None:
            if not identifier.strip():
                page.issues.append((line, "Empty id attribute"))
            page.ids[identifier] += 1
        if tag == "h1":
            page.headings += 1
        if tag == "main" or "main" in (attributes.get("role") or "").split():
            page.landmarks += 1
        if tag == "title":
            self.title_parts = []
        if tag == "meta" and (attributes.get("name") or "").lower() == "description":
            page.descriptions.append((attributes.get("content") or "").strip())
        if tag == "img" and "alt" not in attributes:
            page.issues.append((line, "Image is missing an alt attribute"))
        for attribute in ("href", "src"):
            if attribute in attributes:
                value = attributes[attribute]
                if value is None or not value.strip():
                    page.issues.append((line, f"Empty {attribute} on <{tag}>"))
                else:
                    page.references.append((line, attribute, value.strip()))
        if tag == "base":
            page.issues.append((line, "<base> is not supported by this checker; use explicit local paths"))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_data(self, data: str):
        if self.title_parts is not None:
            self.title_parts.append(data)

    def handle_endtag(self, tag: str):
        if tag == "title" and self.title_parts is not None:
            self.page.titles.append("".join(self.title_parts).strip())
            self.title_parts = None


def parse_page(path: Path) -> Page:
    page = Page(path)
    parser = PageParser(page)
    try:
        parser.feed(path.read_text(encoding="utf-8-sig"))
        parser.close()
    except (OSError, UnicodeError) as error:
        page.issues.append((1, f"Could not read page: {error}"))
    if page.headings != 1:
        page.issues.append((1, f"Expected one h1, found {page.headings}"))
    if page.landmarks != 1:
        page.issues.append((1, f"Expected one main landmark, found {page.landmarks}"))
    if len(page.titles) != 1 or not page.titles[0]:
        page.issues.append((1, "Expected one nonempty title"))
    if len(page.descriptions) != 1 or not page.descriptions[0]:
        page.issues.append((1, "Expected one nonempty meta description"))
    for identifier, count in page.ids.items():
        if count > 1:
            page.issues.append((1, f"Duplicate id {identifier!r} ({count} occurrences)"))
    return page


def check_references(page: Page, root: Path, pages: dict[Path, Page]) -> int:
    checked = 0
    for line, attribute, value in page.references:
        try:
            url = urlsplit(value)
        except ValueError as error:
            page.issues.append((line, f"Invalid {attribute} {value!r}: {error}"))
            continue
        if url.scheme or url.netloc or value.startswith("//"):
            continue
        checked += 1
        raw_path = unquote(url.path)
        if raw_path.startswith("/"):
            target = root / raw_path.lstrip("/")
        elif raw_path:
            target = page.path.parent / raw_path
        else:
            target = page.path
        target = target.resolve()
        if target.is_dir():
            index = next((target / name for name in ("index.html", "index.htm") if (target / name).is_file()), None)
            if index is None:
                page.issues.append((line, f"Directory has no index page: {value!r}"))
                continue
            target = index.resolve()
        if not target.is_file():
            page.issues.append((line, f"Missing local {attribute} target: {value!r}"))
            continue
        fragment = unquote(url.fragment)
        # Text fragments target browser-selected text rather than an element id.
        fragment = fragment.split(":~:text=", 1)[0]
        if fragment and target.suffix.lower() in {".html", ".htm"}:
            target_page = pages.get(target)
            if target_page is None:
                target_page = parse_page(target)
                pages[target] = target_page
            if fragment not in target_page.ids:
                page.issues.append((line, f"Missing local fragment: {value!r}"))
    return checked


def main() -> int:
    argument_parser = argparse.ArgumentParser(description=__doc__)
    argument_parser.add_argument("root", type=Path, help="Static site's document root")
    args = argument_parser.parse_args()
    root = args.root.expanduser().resolve()
    if not root.is_dir():
        argument_parser.error(f"Not a directory: {root}")
    paths = sorted(path.resolve() for path in root.rglob("*")
                   if path.is_file() and path.suffix.lower() in {".html", ".htm"}
                   and not IGNORED_DIRECTORIES.intersection(path.relative_to(root).parts))
    if not paths:
        print(f"FAIL: No HTML pages found in {root}")
        return 1
    pages = {path: parse_page(path) for path in paths}
    references = sum(check_references(pages[path], root, pages) for path in paths)
    failures = 0
    for path in paths:
        for line, message in pages[path].issues:
            print(f"{path.relative_to(root)}:{line}: {message}")
            failures += 1
    if failures:
        print(f"FAIL: {failures} issues in {len(paths)} HTML pages; checked {references} local references.")
        return 1
    print(f"PASS: {len(paths)} HTML pages; {references} local references; headings, main landmarks, metadata, image alt attributes and unique IDs checked.")
    print("External links, rendering, contrast, keyboard behaviour, form delivery and full HTML conformance require separate checks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
