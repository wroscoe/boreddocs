# Sample School District — Board Documents

Public agendas, minutes, and policies for the Sample School District. Built with [boreddocs](https://github.com/wroscoe/boreddocs).

## For board staff (editors)

See [CONTRIBUTING.md](./CONTRIBUTING.md). No software install required — all editing happens in the GitHub web UI.

## For developers

```bash
pip install -r requirements.txt
boreddocs serve              # http://localhost:8000
boreddocs build              # → _site/
```

## Layout

- `content/meetings/` — one Markdown file per meeting (agenda or minutes).
- `content/policies/` — one Markdown file per board policy.
- `data/policy-categories.yml` — the A–L category index used by the policies sidebar.
- `boreddocs.yml` — site config (district name, nav, footer, theme).
- `overrides/` — optional theme/asset overrides (e.g. district logo).

The site rebuilds and republishes via GitHub Actions on every push to `main`.
