# Changelog

All notable changes to **Bored Docs** (the `boreddocs` package) are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.3] - 2026-05-03

### Added
- **`sitemap.xml` and `robots.txt`** are emitted automatically alongside
  every build. The sitemap lists the home page, both listings, and every
  meeting and policy page. Set `site.url` in `boreddocs.yml` (e.g.
  `https://www.example.org`) to get absolute URLs in the sitemap; without
  it, paths are emitted relative.

## [0.1.2] - 2026-05-03

### Added
- Per-page **"View source"** and **"Edit this page on GitHub"** links in the
  default theme footer. Each meeting and policy page links directly to its
  source `.md` on GitHub (`<edit_base_url>/<source_path>` for the editable
  view, with `/edit/` swapped to `/blob/` for the read-only view).
- `source_path` is now exposed in the template context for theme authors.
- Listing pages and the home page (which have no single source file) fall
  back to a "View source repo" link to `site.repo_url`.

## [0.1.1] - 2026-05-03

### Fixed
- **Subpath deployments now work** (e.g. GitHub Pages project sites at
  `https://<user>.github.io/<repo>/`). The default theme's templates now
  prefix every internal link and static asset with `site.base_url`. Set
  `site.base_url: /<repo>` in `boreddocs.yml` when deploying to a subpath.
  Empty `base_url` (the default) preserves the previous root-relative
  behavior. Templates expose a `url()` Jinja global for theme authors.

## [0.1.0] - 2026-05-03

### Added
- Initial release.
- `boreddocs build` — render a static site from a content directory.
- `boreddocs serve` — local preview HTTP server.
- `boreddocs new <dir>` — scaffold a new district repo from `examples/sample-district/`.
- `boreddocs check` — validate frontmatter against schemas.
- Default theme matching the typical board-portal look (orange-bar numbered sections, blue-bar lettered sub-items, collapsible outline).
- `::motion` Markdown directive for voting blocks in meeting minutes.
- Theme override mechanism — `overrides/templates/` and `overrides/static/` in a consumer repo shadow the default theme.
- Frontmatter contract for meetings and policies (`schema_version: 1`).
