# Editor Guide

This site is built with [Bored Docs](https://www.boreddocs.com) — all content is plain text Markdown stored on GitHub. No special software required to edit.

## What you'll need

A free [GitHub account](https://github.com/signup) and edit access to this repository (an existing maintainer can grant this).

## Files you can edit

- `content/meetings/*.md` — agendas and minutes.
- `content/policies/*.md` — board policies.
- `boreddocs.yml` — district name, nav, mission, vision, values.

## Adding a new agenda

1. Browse to `content/meetings/` on GitHub.
2. Click **Add file → Create new file**.
3. Name the file `YYYY-MM-DD-regular.md` (use the meeting date).
4. Copy the contents of an existing agenda as a starting point.
5. Edit the frontmatter (between the `---` lines): date, location.
6. Edit the section/sub-item titles.
7. Commit directly to `main`. The site rebuilds in ~1 minute.

## Adding minutes for a past meeting

1. Open the agenda for the meeting (e.g. `content/meetings/2025-09-10-regular.md`).
2. Click the pencil to edit.
3. Change `type: agenda` to `type: minutes`.
4. Add an `attendance:` block in the frontmatter.
5. Rename the file to add `-minutes` (e.g. `2025-09-10-regular-minutes.md`).
6. For each Action Item that was voted on, add a motion block under the heading:

   ```
   ::motion
   text: I move to approve...
   made_by: Sam Patel
   seconded_by: Jordan Kim
   result: Unanimously approved
   votes:
     - { vote: Yes, name: Alex Rivera }
   ::
   ```

7. Open a Pull Request. A reviewer will merge before the next agenda.

## Linking attachments

Big files (PDFs, presentations) live on Google Drive. Link to them inline:

```markdown
[September binder](https://drive.google.com/drive/folders/...)
```

## Tips

- **Quote anything with a `#`.** YAML treats `#` as a comment. Write `title: "Title #1"` not `title: Title #1`.
- **Preview** by clicking the **Preview** tab before committing.
- If something looks broken on the live site, check the **Actions** tab — a red ✗ means the build failed.
