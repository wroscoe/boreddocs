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
