"""Static site builder.

Reads content (Markdown + YAML) from a configured project dir, renders pages
via Jinja2 templates from the active theme (with optional consumer-side
overrides), writes the output tree to `<project>/_site/`.
"""

from __future__ import annotations

import shutil
from importlib import resources
from pathlib import Path
from typing import Any

import markdown
import yaml
from jinja2 import ChoiceLoader, Environment, FileSystemLoader, select_autoescape

from boreddocs import __version__
from boreddocs.config import Config
from boreddocs.content import (
    Section,
    parse_sections,
    slug_from_path,
    split_frontmatter,
)
from boreddocs.motion_extension import MotionExtension


def _theme_root(theme_name: str) -> Path:
    """Locate <package>/themes/<theme_name>/ on disk for the installed package."""
    pkg = resources.files("boreddocs")
    candidate = pkg / "themes" / theme_name
    return Path(str(candidate))


class Builder:
    def __init__(self, config: Config):
        self.config = config

    # ---------- public API ----------

    def build(self) -> dict[str, int]:
        """Render the full site. Returns counts {meetings, policies}."""
        meetings = self._load_meetings()
        policies = self._load_policies()
        data = self._load_data()
        env = self._make_env()

        out = self.config.output_path
        if out.exists():
            shutil.rmtree(out)
        out.mkdir(parents=True)

        site_ctx = self._site_context()
        base_ctx = {"site": site_ctx, "data": data, "boreddocs_version": __version__}

        # Home
        (out / "index.html").write_text(env.get_template("home.html").render(**base_ctx))

        # Meetings
        meeting_tpl = env.get_template("meeting.html")
        for m in meetings:
            d = out / "meetings" / m["slug"]
            d.mkdir(parents=True, exist_ok=True)
            (d / "index.html").write_text(meeting_tpl.render(meeting=m, **base_ctx))

        listing_tpl = env.get_template("meetings_listing.html")
        (out / "meetings").mkdir(exist_ok=True)
        (out / "meetings" / "index.html").write_text(
            listing_tpl.render(meetings=meetings, **base_ctx)
        )

        # Policies
        policy_tpl = env.get_template("policy.html")
        for p in policies:
            d = out / "policies" / str(p["code"])
            d.mkdir(parents=True, exist_ok=True)
            (d / "index.html").write_text(policy_tpl.render(policy=p, **base_ctx))

        pol_listing_tpl = env.get_template("policies_listing.html")
        categories = data.get("policy_categories", {}).get("categories", [])
        (out / "policies").mkdir(exist_ok=True)
        (out / "policies" / "index.html").write_text(
            pol_listing_tpl.render(policies=policies, categories=categories, **base_ctx)
        )

        self._copy_static(out)

        return {"meetings": len(meetings), "policies": len(policies)}

    # ---------- helpers ----------

    def _site_context(self) -> dict[str, Any]:
        """Build the `site` context exposed to templates.

        Top-level config keys (`nav`, `footer`, `theme`) are nested under
        `site` so templates can stay terse: `{{ site.nav }}`, `{{ site.footer.mission_statement }}`.
        """
        return {
            **self.config.site,
            "nav": self.config.nav,
            "footer": self.config.footer,
            "theme": self.config.theme,
        }

    def _md(self) -> markdown.Markdown:
        return markdown.Markdown(
            extensions=["extra", "sane_lists", MotionExtension()],
            output_format="html5",
        )

    def _make_env(self) -> Environment:
        loaders = []
        overrides_tpl = self.config.overrides_dir / "templates"
        if overrides_tpl.exists():
            loaders.append(FileSystemLoader(str(overrides_tpl)))
        theme_tpl = _theme_root(self.config.theme_name) / "templates"
        if not theme_tpl.exists():
            raise FileNotFoundError(f"Theme '{self.config.theme_name}' not found at {theme_tpl}")
        loaders.append(FileSystemLoader(str(theme_tpl)))

        env = Environment(
            loader=ChoiceLoader(loaders),
            autoescape=select_autoescape(["html"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        env.globals["url"] = self._url_for
        return env

    def _url_for(self, path: str | None) -> str:
        """Prefix an absolute site path with `site.base_url`.

        Used by templates so a site deployed under a subpath (e.g. GitHub
        Pages project sites at `/<repo>/`) resolves static assets and
        internal links correctly. External URLs and relative paths pass
        through unchanged.
        """
        if not path:
            return ""
        if "://" in path or path.startswith("//") or path.startswith("mailto:"):
            return path
        if not path.startswith("/"):
            return path
        base = str(self.config.site.get("base_url") or "").rstrip("/")
        return base + path

    def _load_data(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if self.config.data_dir.exists():
            for f in sorted(self.config.data_dir.glob("*.yml")):
                with f.open() as fh:
                    data[f.stem.replace("-", "_")] = yaml.safe_load(fh) or {}
        return data

    def _load_meetings(self) -> list[dict[str, Any]]:
        meetings: list[dict[str, Any]] = []
        if not self.config.meetings_dir.exists():
            return meetings
        for path in sorted(self.config.meetings_dir.glob("*.md")):
            text = path.read_text()
            meta, body = split_frontmatter(text)
            sections: list[Section] = parse_sections(body)
            self._render_sections(sections)
            meta["slug"] = slug_from_path(path)
            meta["sections"] = sections
            meetings.append(meta)
        meetings.sort(key=lambda m: str(m.get("date", "")), reverse=True)
        return meetings

    def _render_sections(self, sections: list[Section]) -> None:
        for s in sections:
            for item in s.items:
                if item.body_md.strip():
                    md = self._md()
                    item.body_html = md.convert(item.body_md)

    def _load_policies(self) -> list[dict[str, Any]]:
        policies: list[dict[str, Any]] = []
        if not self.config.policies_dir.exists():
            return policies
        for path in sorted(self.config.policies_dir.glob("*.md")):
            text = path.read_text()
            meta, body = split_frontmatter(text)
            md = self._md()
            meta["body_html"] = md.convert(body.strip())
            meta["slug"] = slug_from_path(path)
            policies.append(meta)
        policies.sort(key=lambda p: str(p.get("code", "")))
        return policies

    def _copy_static(self, out: Path) -> None:
        """Copy theme static, then overlay overrides/static (later wins)."""
        out_static = out / "static"
        out_static.mkdir(exist_ok=True)

        theme_static = _theme_root(self.config.theme_name) / "static"
        if theme_static.exists():
            self._copy_tree(theme_static, out_static)
        overrides_static = self.config.overrides_dir / "static"
        if overrides_static.exists():
            self._copy_tree(overrides_static, out_static)

    @staticmethod
    def _copy_tree(src: Path, dst: Path) -> None:
        for p in src.rglob("*"):
            if p.is_file():
                target = dst / p.relative_to(src)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, target)
