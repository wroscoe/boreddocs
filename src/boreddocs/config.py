"""boreddocs.yml loader — single dataclass, no schema validation library yet."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG_FILENAME = "boreddocs.yml"


@dataclass
class Config:
    project_dir: Path
    schema_version: int = 1
    site: dict[str, Any] = field(default_factory=dict)
    nav: list[dict[str, Any]] = field(default_factory=list)
    footer: dict[str, Any] = field(default_factory=dict)
    theme: dict[str, Any] = field(default_factory=lambda: {"name": "default"})
    content: dict[str, str] = field(
        default_factory=lambda: {
            "meetings_dir": "content/meetings",
            "policies_dir": "content/policies",
            "data_dir": "data",
        }
    )
    output_dir: str = "_site"

    @property
    def meetings_dir(self) -> Path:
        return self.project_dir / self.content.get("meetings_dir", "content/meetings")

    @property
    def policies_dir(self) -> Path:
        return self.project_dir / self.content.get("policies_dir", "content/policies")

    @property
    def data_dir(self) -> Path:
        return self.project_dir / self.content.get("data_dir", "data")

    @property
    def overrides_dir(self) -> Path:
        return self.project_dir / "overrides"

    @property
    def output_path(self) -> Path:
        return self.project_dir / self.output_dir

    @property
    def theme_name(self) -> str:
        return self.theme.get("name", "default")


def load_config(path: Path | str | None = None) -> Config:
    """Load `boreddocs.yml` from `path` (file or containing directory)."""
    if path is None:
        path = Path.cwd() / DEFAULT_CONFIG_FILENAME
    path = Path(path)
    if path.is_dir():
        path = path / DEFAULT_CONFIG_FILENAME
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with path.open() as fh:
        raw = yaml.safe_load(fh) or {}

    project_dir = path.parent.resolve()
    cfg = Config(project_dir=project_dir)
    if "schema_version" in raw:
        cfg.schema_version = int(raw["schema_version"])
    if cfg.schema_version != 1:
        raise ValueError(
            f"Unsupported schema_version {cfg.schema_version} (this boreddocs supports 1)"
        )
    if "site" in raw:
        cfg.site = raw["site"] or {}
    if "nav" in raw:
        cfg.nav = raw["nav"] or []
    if "footer" in raw:
        cfg.footer = raw["footer"] or {}
    if "theme" in raw:
        cfg.theme = {**cfg.theme, **(raw["theme"] or {})}
    if "content" in raw and isinstance(raw["content"], dict):
        cfg.content = {**cfg.content, **raw["content"]}
    if "output_dir" in raw:
        cfg.output_dir = raw["output_dir"]
    return cfg
