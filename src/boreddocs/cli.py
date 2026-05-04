"""boreddocs command-line interface."""

import argparse
import sys
from pathlib import Path

from boreddocs import __version__
from boreddocs.builder import Builder
from boreddocs.config import load_config
from boreddocs.content import parse_sections, split_frontmatter
from boreddocs.scaffold import scaffold


def _add_config_arg(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "-c",
        "--config",
        default="boreddocs.yml",
        help="Path to boreddocs.yml (default: ./boreddocs.yml).",
    )


def cmd_build(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    if args.base_url is not None:
        cfg.site["base_url"] = args.base_url
    if args.site_url is not None:
        cfg.site["url"] = args.site_url
    counts = Builder(cfg).build()
    print(
        f"Built {counts['meetings']} meetings, {counts['policies']} policies → {cfg.output_path}"
    )
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    from boreddocs.server import serve

    cfg = load_config(args.config)
    serve(cfg, host=args.host, port=args.port)
    return 0


def cmd_new(args: argparse.Namespace) -> int:
    target = Path(args.directory)
    created = scaffold(target)
    print(f"Scaffolded new district repo at: {created}")
    print("Next steps:")
    print(f"  cd {target}")
    print("  pip install -r requirements.txt")
    print("  boreddocs serve")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    errors: list[str] = []

    for path in sorted(cfg.meetings_dir.glob("*.md")) if cfg.meetings_dir.exists() else []:
        meta, body = split_frontmatter(path.read_text())
        if not meta.get("title"):
            errors.append(f"{path}: missing title")
        if meta.get("type") not in {"agenda", "minutes", None}:
            errors.append(f"{path}: type must be 'agenda' or 'minutes' (got {meta.get('type')!r})")
        if not parse_sections(body):
            errors.append(f"{path}: no `# 1. ...` sections found")

    for path in sorted(cfg.policies_dir.glob("*.md")) if cfg.policies_dir.exists() else []:
        meta, _ = split_frontmatter(path.read_text())
        if not meta.get("code"):
            errors.append(f"{path}: missing 'code' in frontmatter")
        if not meta.get("title"):
            errors.append(f"{path}: missing 'title' in frontmatter")

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        print(f"\n{len(errors)} problem(s) found.", file=sys.stderr)
        return 1
    print("All content files passed checks.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="boreddocs",
        description="Free, open static-site renderer for school board documents.",
    )
    parser.add_argument(
        "--version", action="version", version=f"boreddocs {__version__}"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_build = sub.add_parser("build", help="Render the site to _site/.")
    _add_config_arg(p_build)
    p_build.add_argument(
        "--base-url",
        default=None,
        help="Override site.base_url from config (e.g. /<repo> for GitHub Pages project sites).",
    )
    p_build.add_argument(
        "--site-url",
        default=None,
        help="Override site.url from config (canonical origin used in sitemap.xml).",
    )
    p_build.set_defaults(func=cmd_build)

    p_serve = sub.add_parser("serve", help="Build and serve with auto-rebuild.")
    _add_config_arg(p_serve)
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8000)
    p_serve.set_defaults(func=cmd_serve)

    p_new = sub.add_parser("new", help="Scaffold a new district repo.")
    p_new.add_argument("directory", help="Target directory.")
    p_new.set_defaults(func=cmd_new)

    p_check = sub.add_parser("check", help="Validate frontmatter in content files.")
    _add_config_arg(p_check)
    p_check.set_defaults(func=cmd_check)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
