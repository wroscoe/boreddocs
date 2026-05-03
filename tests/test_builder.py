"""End-to-end smoke test: build the bundled sample-district into a temp dir."""

import shutil
from pathlib import Path

from boreddocs.builder import Builder
from boreddocs.config import load_config

REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE = REPO_ROOT / "examples" / "sample-district"


def test_sample_district_builds(tmp_path):
    work = tmp_path / "sample-district"
    shutil.copytree(SAMPLE, work)
    cfg = load_config(work / "boreddocs.yml")
    counts = Builder(cfg).build()

    assert counts["meetings"] == 2
    assert counts["policies"] == 2

    site = work / "_site"
    assert (site / "index.html").exists()
    assert (site / "meetings" / "index.html").exists()
    assert (site / "meetings" / "2025-09-10-regular" / "index.html").exists()
    assert (site / "meetings" / "2025-08-13-regular-minutes" / "index.html").exists()
    assert (site / "policies" / "AA" / "index.html").exists()
    assert (site / "static" / "styles.css").exists()
    assert (site / "static" / "app.js").exists()
    assert (site / "static" / "img" / "logo.svg").exists()


def test_minutes_render_motion_blocks(tmp_path):
    work = tmp_path / "sample-district"
    shutil.copytree(SAMPLE, work)
    cfg = load_config(work / "boreddocs.yml")
    Builder(cfg).build()

    minutes = (work / "_site" / "meetings" / "2025-08-13-regular-minutes" / "index.html").read_text()
    assert 'class="motion"' in minutes
    assert "Yes: Alex Rivera" in minutes
    assert "No: Dr. Pat Hughes" in minutes  # the non-unanimous bus-route motion
    assert "Unanimously approved" in minutes


def test_seo_friendly_html_includes_content_in_raw_html(tmp_path):
    """Pre-rendered HTML must contain the agenda body without any JS execution."""
    work = tmp_path / "sample-district"
    shutil.copytree(SAMPLE, work)
    cfg = load_config(work / "boreddocs.yml")
    Builder(cfg).build()

    agenda = (work / "_site" / "meetings" / "2025-09-10-regular" / "index.html").read_text()
    assert "Call to Order" in agenda
    assert "Pledge of Allegiance" in agenda
    assert "Adjourn" in agenda


def test_overrides_directory_shadows_theme(tmp_path):
    work = tmp_path / "sample-district"
    shutil.copytree(SAMPLE, work)

    # Add an override that replaces the header partial
    override_dir = work / "overrides" / "templates" / "partials"
    override_dir.mkdir(parents=True, exist_ok=True)
    (override_dir / "header.html").write_text("<header>OVERRIDDEN_HEADER</header>")

    cfg = load_config(work / "boreddocs.yml")
    Builder(cfg).build()

    home = (work / "_site" / "index.html").read_text()
    assert "OVERRIDDEN_HEADER" in home
    assert "site-header" not in home  # the default theme's class is gone


def test_base_url_prefixes_static_and_internal_links(tmp_path):
    """When site.base_url is set, /static/... and internal links must be prefixed."""
    work = tmp_path / "sample-district"
    shutil.copytree(SAMPLE, work)

    config_path = work / "boreddocs.yml"
    config_path.write_text(
        config_path.read_text().replace('base_url: ""', 'base_url: /my-repo')
    )

    cfg = load_config(config_path)
    Builder(cfg).build()

    home = (work / "_site" / "index.html").read_text()
    assert 'href="/my-repo/static/styles.css"' in home
    assert 'src="/my-repo/static/app.js"' in home
    assert 'href="/my-repo/meetings/"' in home
    assert 'href="/my-repo/policies/"' in home

    listing = (work / "_site" / "meetings" / "index.html").read_text()
    assert 'href="/my-repo/meetings/2025-09-10-regular/"' in listing


def test_empty_base_url_keeps_root_relative_paths(tmp_path):
    work = tmp_path / "sample-district"
    shutil.copytree(SAMPLE, work)
    cfg = load_config(work / "boreddocs.yml")
    Builder(cfg).build()

    home = (work / "_site" / "index.html").read_text()
    assert 'href="/static/styles.css"' in home
    assert 'href="/meetings/"' in home


def test_meeting_pages_link_to_source_and_edit_on_github(tmp_path):
    work = tmp_path / "sample-district"
    shutil.copytree(SAMPLE, work)
    cfg = load_config(work / "boreddocs.yml")
    Builder(cfg).build()

    minutes = (work / "_site" / "meetings" / "2025-08-13-regular-minutes" / "index.html").read_text()
    assert (
        "https://github.com/example/sample-school-district/blob/main/content/meetings/2025-08-13-regular-minutes.md"
        in minutes
    )
    assert (
        "https://github.com/example/sample-school-district/edit/main/content/meetings/2025-08-13-regular-minutes.md"
        in minutes
    )
    assert "Edit this page on GitHub" in minutes


def test_policy_pages_link_to_source(tmp_path):
    work = tmp_path / "sample-district"
    shutil.copytree(SAMPLE, work)
    cfg = load_config(work / "boreddocs.yml")
    Builder(cfg).build()

    policy = (work / "_site" / "policies" / "AA" / "index.html").read_text()
    assert "/blob/main/content/policies/AA.md" in policy
    assert "/edit/main/content/policies/AA.md" in policy


def test_listing_pages_show_repo_link_only(tmp_path):
    """Listings have no source markdown file; they should fall back to the repo link."""
    work = tmp_path / "sample-district"
    shutil.copytree(SAMPLE, work)
    cfg = load_config(work / "boreddocs.yml")
    Builder(cfg).build()

    listing = (work / "_site" / "meetings" / "index.html").read_text()
    assert "View source repo" in listing
    assert "Edit this page on GitHub" not in listing


def test_overrides_static_overlays_theme_static(tmp_path):
    work = tmp_path / "sample-district"
    shutil.copytree(SAMPLE, work)

    override_static = work / "overrides" / "static" / "img"
    override_static.mkdir(parents=True, exist_ok=True)
    (override_static / "logo.svg").write_text("<!-- overridden logo -->")

    cfg = load_config(work / "boreddocs.yml")
    Builder(cfg).build()

    out_logo = (work / "_site" / "static" / "img" / "logo.svg").read_text()
    assert "overridden logo" in out_logo
