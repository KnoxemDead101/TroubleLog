# TroubleLog — Changelog

## v0.2-patch1 — 2026-08-28
### Fixed
- Timestamps ("Created" / "Last Updated") were captured once at program
  start and reused everywhere, causing every log created or updated in a
  single session to show identical, incorrect times. Now read from actual
  file metadata (`file_times()`) or generated fresh at the moment of the
  action (`now_str()`).
- A correctly-computed per-entry timestamp existed in the CREATE branch
  but was never inserted into the saved log content. Now used.
- READ menu (`choice == "2"`) had no way to return to the main menu short
  of finding a valid log. Pressing Enter at the machine-name prompt now
  exits back to the menu.

### Added
- Basic blank-field validation on CREATE (machine, log number, title,
  status, summary) and UPDATE (status, notes). Rejects empty submissions
  instead of silently writing them.

### Reviewed, unchanged
- `menu.py` — no issues found.

### Known gaps (carried forward, see `docs/decisions.md`)
- Schema does not yet include requested_by, OS, device type, symptoms,
  diagnosis, root cause, fix applied, tools used, or tags.
- No cross-log listing/search.
- Storage format (flat `.md` files vs. SQLite) not yet decided.

---

## v0.2 — prior to this session
- Original CRUD-style menu (Create / Read / Update / Exit) for service
  logs stored as markdown files under `logs/<machine>/`.
