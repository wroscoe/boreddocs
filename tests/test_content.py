from boreddocs.content import parse_sections, split_frontmatter


def test_split_frontmatter_basic():
    src = "---\ntitle: Hello\n---\n# 1. Section\n\n## A. Item\n"
    meta, body = split_frontmatter(src)
    assert meta == {"title": "Hello"}
    assert body.startswith("# 1.")


def test_split_frontmatter_missing_returns_empty_meta():
    src = "# 1. Section\n"
    meta, body = split_frontmatter(src)
    assert meta == {}
    assert body == src


def test_parse_sections_groups_by_heading():
    body = """\
# 1. Call to Order

## A. Executive Session

## B. Regular Meeting

# 2. Approval of Agenda

## A. Approve agenda

some body text
"""
    sections = parse_sections(body)
    assert [s.number for s in sections] == ["1", "2"]
    assert sections[0].title == "Call to Order"
    assert [i.letter for i in sections[0].items] == ["A", "B"]
    assert sections[1].items[0].body_md.strip() == "some body text"


def test_parse_sections_preserves_body_for_motion():
    body = """\
# 1. Action

## A. Approve

::motion
text: m
made_by: a
seconded_by: b
::
"""
    sections = parse_sections(body)
    item = sections[0].items[0]
    assert "::motion" in item.body_md
    assert "::" in item.body_md
