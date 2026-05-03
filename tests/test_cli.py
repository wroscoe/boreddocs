"""Smoke tests for the boreddocs CLI."""

import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE = REPO_ROOT / "examples" / "sample-district"


def _run(args, cwd):
    return subprocess.run(
        [sys.executable, "-m", "boreddocs.cli", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )


def test_cli_build(tmp_path):
    work = tmp_path / "sample-district"
    shutil.copytree(SAMPLE, work)
    proc = _run(["build"], work)
    assert proc.returncode == 0, proc.stderr
    assert "Built" in proc.stdout
    assert (work / "_site" / "index.html").exists()


def test_cli_check_passes_on_sample(tmp_path):
    work = tmp_path / "sample-district"
    shutil.copytree(SAMPLE, work)
    proc = _run(["check"], work)
    assert proc.returncode == 0, proc.stderr
    assert "passed checks" in proc.stdout


def test_cli_check_flags_missing_title(tmp_path):
    work = tmp_path / "sample-district"
    shutil.copytree(SAMPLE, work)
    bad = work / "content" / "meetings" / "broken.md"
    bad.write_text("---\ntype: agenda\n---\n# 1. X\n")
    proc = _run(["check"], work)
    assert proc.returncode == 1
    assert "missing title" in proc.stderr


def test_cli_new_scaffolds_into_empty_dir(tmp_path):
    target = tmp_path / "demo-district"
    proc = _run(["new", str(target)], tmp_path)
    assert proc.returncode == 0, proc.stderr
    assert (target / "boreddocs.yml").exists()
    assert (target / "content" / "meetings").exists()
    assert (target / "content" / "policies").exists()


def test_cli_new_refuses_existing_nonempty_dir(tmp_path):
    target = tmp_path / "existing"
    target.mkdir()
    (target / "marker.txt").write_text("don't clobber me")
    proc = _run(["new", str(target)], tmp_path)
    assert proc.returncode != 0
    assert (target / "marker.txt").read_text() == "don't clobber me"
