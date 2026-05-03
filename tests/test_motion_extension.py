import markdown

from boreddocs.motion_extension import MotionExtension


def render(src: str) -> str:
    md = markdown.Markdown(
        extensions=["extra", "sane_lists", MotionExtension()],
        output_format="html5",
    )
    return md.convert(src)


def test_renders_voting_results():
    src = """\
::motion
text: I move to approve.
made_by: Sam Patel
seconded_by: Jordan Kim
result: Unanimously approved
votes:
  - { vote: Yes, name: Alex Rivera }
  - { vote: Yes, name: Sam Patel }
::
"""
    html = render(src)
    assert 'class="motion"' in html
    assert "I move to approve." in html
    assert "Sam Patel" in html
    assert "Jordan Kim" in html
    assert "Unanimously approved" in html
    assert "Yes: Alex Rivera" in html


def test_renders_without_text():
    src = """\
::motion
made_by: Sam Patel
seconded_by: Jordan Kim
result: Unanimously approved
votes:
  - { vote: Yes, name: Alex Rivera }
::
"""
    html = render(src)
    assert "Sam Patel" in html
    assert "Yes: Alex Rivera" in html


def test_yaml_yes_no_normalized_to_string():
    src = """\
::motion
text: m
made_by: x
seconded_by: y
votes:
  - { vote: Yes, name: A }
  - { vote: No, name: B }
::
"""
    html = render(src)
    assert "Yes: A" in html
    assert "No: B" in html
    # Make sure we never leak Python's "True"/"False" reprs
    assert "True:" not in html
    assert "False:" not in html


def test_no_close_fence_falls_through_to_paragraph():
    src = "::motion\ntext: x\n"  # no closing ::
    html = render(src)
    assert 'class="motion"' not in html
    assert "::motion" in html  # rendered as paragraph text


def test_motion_followed_by_other_content():
    src = """\
Before paragraph.

::motion
text: m
made_by: a
seconded_by: b
::

After paragraph.
"""
    html = render(src)
    assert "Before paragraph." in html
    assert "After paragraph." in html
    assert 'class="motion"' in html
