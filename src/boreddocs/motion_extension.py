"""python-markdown extension that renders ::motion ... :: blocks as styled
voting blocks inside meeting minutes."""

import re
import xml.etree.ElementTree as etree

import yaml
from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension

FENCE_OPEN = re.compile(r"^::motion\s*$", re.MULTILINE)
FENCE_CLOSE = re.compile(r"^::\s*$", re.MULTILINE)


class MotionBlockProcessor(BlockProcessor):
    def test(self, parent, block):
        return FENCE_OPEN.match(block) is not None

    def run(self, parent, blocks):
        # Look ahead WITHOUT mutating `blocks` until we are sure we can handle
        # this match. Mutating then returning False corrupts the parser state.
        body_chunks = []
        consume = 0
        found_close = False

        first = blocks[0]
        first_lines = first.split("\n")

        # Case 1: open and close fence in the same block.
        for i, line in enumerate(first_lines[1:], start=1):
            if FENCE_CLOSE.match(line):
                body_chunks.append("\n".join(first_lines[1:i]))
                consume = 1
                found_close = True
                break

        # Case 2: open in blocks[0], close in a later block.
        if not found_close:
            body_chunks.append("\n".join(first_lines[1:]))
            for i in range(1, len(blocks)):
                chunk = blocks[i]
                if FENCE_CLOSE.search(chunk):
                    close_idx = chunk.index("::")
                    before = chunk[:close_idx].rstrip("\n")
                    if before:
                        body_chunks.append(before)
                    consume = i + 1
                    found_close = True
                    break
                body_chunks.append(chunk)

        if not found_close:
            return False

        body = "\n\n".join(c for c in body_chunks if c).strip()
        try:
            data = yaml.safe_load(body) or {}
        except yaml.YAMLError:
            return False
        if not isinstance(data, dict):
            return False

        for _ in range(consume):
            blocks.pop(0)
        self._render(parent, data)
        return True

    def _render(self, parent, data):
        wrap = etree.SubElement(parent, "aside")
        wrap.set("class", "motion")

        text = data.get("text")
        if text:
            p = etree.SubElement(wrap, "p")
            p.set("class", "motion-text")
            p.text = str(text)

        made_by = data.get("made_by")
        if made_by:
            p = etree.SubElement(wrap, "p")
            p.set("class", "motion-meta")
            strong = etree.SubElement(p, "strong")
            strong.text = "Motion made by:"
            strong.tail = f" {made_by}"

        seconded_by = data.get("seconded_by")
        if seconded_by:
            p = etree.SubElement(wrap, "p")
            p.set("class", "motion-meta")
            strong = etree.SubElement(p, "strong")
            strong.text = "Motion seconded by:"
            strong.tail = f" {seconded_by}"

        votes = data.get("votes") or []
        result = data.get("result")
        if votes or result:
            box = etree.SubElement(wrap, "div")
            box.set("class", "voting-results")

            label = etree.SubElement(box, "p")
            label.set("class", "voting-results-label")
            em = etree.SubElement(label, "em")
            em.text = "Voting results:"
            if result:
                em.tail = f" {result}"

            if votes:
                ul = etree.SubElement(box, "ul")
                ul.set("class", "votes")
                for v in votes:
                    if not isinstance(v, dict):
                        continue
                    li = etree.SubElement(ul, "li")
                    raw_vote = v.get("vote", "")
                    # PyYAML parses "Yes"/"No" as booleans (YAML 1.1).
                    # Normalize back to the original string form.
                    if raw_vote is True:
                        vote = "Yes"
                    elif raw_vote is False:
                        vote = "No"
                    else:
                        vote = str(raw_vote)
                    name = v.get("name", "")
                    li.text = f"{vote}: {name}"


class MotionExtension(Extension):
    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(
            MotionBlockProcessor(md.parser), "motion", 175
        )


def makeExtension(**kwargs):
    return MotionExtension(**kwargs)
