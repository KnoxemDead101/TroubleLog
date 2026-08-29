# TroubleLog — Changelog

## v0.3-planning-2 — 2026-08-28
### Fixed (compatibility)
- Replaced `@dataclass(kw_only=True)` (Python 3.10+ only) with a
  portable pattern that works on Python 3.7+: every field now has a
  default value, and each class defines a `REQUIRED_FIELDS` list that
  `LogEntry.__post_init__` validates at creation time, raising
  `ValueError` if anything required is missing. Applied to
  `log_entry.py`, `homelab_log.py`, and `job_log.py`.

### Added
- `check_models.py` — runnable sanity check at the project root. Builds
  a HomelabLog and a JobLog from the real JJ and Highway85 A/V examples,
  confirms core behavior (tags, resolution, status), and confirms
  required-field validation actually rejects incomplete logs. Run with
  `python3 check_models.py` from the project root. Verified working in
  this session's environment before being handed off.

## v0.3-planning — 2026-08-28
### Added
- `src/models/log_entry.py`: new `LogEntry` base class holding fields
  shared by every log type (log_number, title, status, summary, tags,
  date_reported, date_resolved), plus `LogType` and `LogStatus` enums.
- `src/models/homelab_log.py`: `HomelabLog` class (formerly `ServiceLog`,
  now renamed and rebuilt to inherit from `LogEntry`). Same fields as
  before (machine, requested_by, operating_system, device_type,
  location, program_context, reported_symptoms, diagnosis, root_cause,
  fix_applied, tools_used).
- `src/models/job_log.py`: new `JobLog` class for client/employer work —
  client_employer, category (new `JobCategory` enum), time_spent, fix,
  recommendation (optional).
- `docs/roadmap.md`: new file capturing the job log format, status field
  decision, attachments convention, versioned roadmap (v0.3/v0.4/v1.0),
  and the full list of currently open/unresolved questions.
- `src/__init__.py`, `src/models/__init__.py`: empty package markers,
  required for the relative imports used between the new model files.

### Changed
- `src/models/service_log.py` removed; superseded by
  `src/models/homelab_log.py`. See `docs/decisions.md` for git-diff note.

### Still schema-only (not yet wired to app)
- No log-type selector in `main.py` yet.
- No storage logic for either log type yet.
- `LogStatus` values are a working draft (see Open Question #6 in
  `docs/roadmap.md`).

## v0.2-patch2 — 2026-08-28
### Changed
- Added extensive teaching-style comments throughout `main.py` and
  `menu.py`, explaining not just what each line does but the underlying
  Python concept (pathlib, f-strings, context managers, `continue` vs
  `break`, truthiness, docstrings, etc.). No functional/behavioral
  changes in this pass — same logic as v0.2-patch1, purely documentation.
- Added `src/models/service_log.py`: a `ServiceLog` dataclass defining
  the fuller schema (requested_by, operating_system, device_type,
  program_context, reported_symptoms, diagnosis, root_cause, fix_applied,
  tools_used, tags, status, date_reported, date_resolved), using Enums
  for OS/device_type/status to close off free-text typos. Also heavily
  commented, introducing dataclasses, Enum, type hints, and the
  `default_factory` pattern for mutable defaults. Not yet wired into
  `main.py` — this is schema-only, no storage or menu integration yet.

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
