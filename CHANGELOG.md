# Changelog

All notable changes to **boreddocs** are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
