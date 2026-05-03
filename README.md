# boreddocs

A free, fast, SEO- and AI-friendly static site for school board documents — agendas, minutes, and policies authored in Markdown. Modeled after [`mkdocs`](https://www.mkdocs.org/), but specialized for the way school boards actually publish information.

`boreddocs` exists because the dominant paid board-portal product is expensive, hostile to search engines, and unfriendly to AI assistants. School board agendas are public records — they should look, feel, and read like the open web.

## Quickstart

```bash
pip install boreddocs
boreddocs new my-district
cd my-district
boreddocs serve              # preview at http://localhost:8000
```

When you're ready to publish, push the repo to GitHub and the bundled GitHub Actions workflow deploys to GitHub Pages.

## Repo layout (consumer side)

```
my-district/
├── boreddocs.yml              # site config
├── content/
│   ├── meetings/
│   │   └── 2026-04-15-regular.md
│   └── policies/
│       └── AA-school-district-legal-status.md
├── data/
│   └── policy-categories.yml
├── overrides/                 # optional: shadow the default theme
│   ├── static/img/logo.svg
│   └── templates/partials/header.html
├── requirements.txt           # boreddocs>=0.1,<0.2
└── .github/workflows/deploy.yml
```

A complete working example lives at [`examples/sample-district/`](./examples/sample-district/).

## What `boreddocs build` does

1. Reads `boreddocs.yml` and validates it.
2. Walks `content/meetings/*.md` and `content/policies/*.md`. Each file has YAML frontmatter (metadata) followed by Markdown body.
3. Parses meeting bodies into a structured outline using heading conventions: `# 1. Section` → numbered section, `## A. Item` → lettered sub-item.
4. Renders each item's body through `python-markdown` with a custom `::motion` extension that turns voting blocks into styled aside elements.
5. Renders each page through Jinja2 templates from the active theme. If `overrides/templates/<path>` exists, it shadows the default.
6. Copies `static/` from the theme (and any `overrides/static/`) into `_site/static/`.
7. Output lands in `_site/` — fully pre-rendered HTML, ready for GitHub Pages.

## The `::motion` directive

Used inside meeting minutes:

```markdown
## A. Approval of the April 15, 2026 Regular Meeting agenda

::motion
text: I move to approve the April 15, 2026 regular meeting agenda as presented.
made_by: Stephan Abrams
seconded_by: Bill Scarlett IV
result: Unanimously approved
votes:
  - { vote: Yes, name: Betsy Carlin }
  - { vote: Yes, name: Stephan Abrams }
::
```

Renders as a styled voting block.

## CLI

| Command | What it does |
| --- | --- |
| `boreddocs build` | Render the site to `_site/`. |
| `boreddocs serve` | Build, then serve `_site/` on localhost with auto-rebuild on file changes. |
| `boreddocs new <dir>` | Scaffold a new district repo. |
| `boreddocs check` | Validate every content file's frontmatter; non-zero exit on any error. |

All commands accept `--config <path>` (defaults to `./boreddocs.yml`).

## Why a separate package

- **Independent versioning** — districts pin to a major version; renderer changes don't accidentally break their site.
- **Single editor mental model** — a district's repo is just markdown + a config file. No Python, no templates.
- **Reusability** — every other district can adopt it for free.
- **Themability** — districts can shadow individual partial templates without forking the package.

## Status

Pre-1.0. Schema is stable for the duration of `0.x` (breakage requires major bump + a documented `schema_version` migration).

## License

MIT — see [LICENSE](./LICENSE).
