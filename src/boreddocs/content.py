"""Frontmatter parsing and meeting/agenda outline parsing."""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)
H1_RE = re.compile(r"^#\s+(\S+?)\.\s+(.*)$")
H2_RE = re.compile(r"^##\s+(\S+?)\.\s+(.*)$")


@dataclass
class SubItem:
    letter: str
    title: str
    body_md: str = ""
    body_html: str = ""


@dataclass
class Section:
    number: str
    title: str
    items: list[SubItem] = field(default_factory=list)


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Split a markdown file with YAML frontmatter into (meta, body)."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    meta = yaml.safe_load(m.group(1)) or {}
    return meta, m.group(2)


def parse_sections(body: str) -> list[Section]:
    """Parse a meeting body into numbered sections (H1) and lettered sub-items (H2).

    Conventions:
        # 1. Call to Order        -> Section(number="1", title="Call to Order")
        ## A. Some sub-item       -> SubItem(letter="A", title="Some sub-item")
    Body content between an `## A.` line and the next heading is captured as
    that sub-item's `body_md` (rendered later).
    """
    sections: list[Section] = []
    current_section: Section | None = None
    current_item: SubItem | None = None
    buf: list[str] = []

    def flush_item():
        nonlocal buf
        if current_item is not None:
            current_item.body_md = "\n".join(buf).strip()
        buf = []

    for line in body.splitlines():
        h1 = H1_RE.match(line)
        h2 = H2_RE.match(line)
        if h1:
            flush_item()
            current_item = None
            current_section = Section(number=h1.group(1), title=h1.group(2).strip())
            sections.append(current_section)
            continue
        if h2 and current_section is not None:
            flush_item()
            current_item = SubItem(letter=h2.group(1), title=h2.group(2).strip())
            current_section.items.append(current_item)
            continue
        if current_item is not None:
            buf.append(line)

    flush_item()
    return sections


def slug_from_path(path: Path) -> str:
    return path.stem
