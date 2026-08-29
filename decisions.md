# TroubleLog — Decisions Log

Ongoing record of *why* things were built or changed a certain way.
Paired with `CHANGELOG.md`, which tracks *what* changed and *when*.

---

## 2026-08-28 — Compatibility fix: dropped kw_only for portability

### Problem
The first version of the shared-base design used
`@dataclass(kw_only=True)`, which requires Python 3.10+. You were on
mobile and couldn't check your desktop/Replit Python version, so relying
on 3.10+ risked the code simply failing to run with a confusing error.

### Decision: enforce required fields with `__post_init__` instead of kw_only
Every field in `LogEntry`, `HomelabLog`, and `JobLog` now has a default
value (usually `None`), removing the field-ordering conflict entirely.
Each class defines a `REQUIRED_FIELDS` list (a `ClassVar`), and
`LogEntry.__post_init__` checks that list against the actual field
values right after an object is created, raising `ValueError` if
anything required was left blank.

**Why:** This pattern works on Python 3.7+, which should cover any
realistic desktop or Replit environment without needing to verify a
version number first. `kw_only=True` is arguably cleaner code, but
compatibility risk outweighed that for now.

**Trade-off accepted:** "Required" is now enforced at *runtime* (when an
object is created) rather than *before* the code even runs (a type
checker/IDE won't flag a missing required field the way it might with
kw_only + no defaults). For a project this size, catching it at runtime
via a clear `ValueError` is an acceptable trade — the error message
names exactly which fields were missing and on which log type.

### Added: `check_models.py`
A runnable, non-pytest sanity check at the project root. Builds one
HomelabLog and one JobLog using the real JJ and Highway85 A/V examples,
confirms tags/status/resolution work, and confirms that leaving out
required fields correctly raises an error rather than silently creating
a broken log. Meant to be run directly (`python3 check_models.py`) the
first time this code lands on your desktop, to confirm everything works
in that environment before building further on top of it.

---

### Decision: extend TroubleLog, not a separate app
Job tracking (client/employer work) is built into TroubleLog as a second
log type, not a new standalone application. Both types will eventually
share the same menu, storage location structure, and (per v1.0 roadmap)
the same search.

### Decision: shared core via inheritance, not duplicated fields
`src/models/log_entry.py` now holds a `LogEntry` base class with the
fields both log types share (log_number, title, status, summary, tags,
date_reported, date_resolved). `HomelabLog` and `JobLog` each inherit
from it and add only their own type-specific fields.

**Why:** The alternative — copying shared fields into two separate
classes — means every future change to a shared field (e.g. adding a
new Status value, or changing how tags work) has to be made twice and
kept in sync by hand. Inheritance makes the "shared core" a real,
enforced fact in the code, not just a documentation note.

**Trade-off / new complexity accepted:** dataclass inheritance normally
requires all fields-without-defaults to come before fields-with-defaults
across the *entire* class hierarchy. Since both `HomelabLog.machine` and
`JobLog.client_employer` are required fields being added *after* the
base class's optional fields (`status`, `tags`, etc.), this doesn't work
with plain dataclasses. Solved by using `@dataclass(kw_only=True)` on
every class in the hierarchy — this requires Python 3.10+, worth
confirming your Replit/local environment matches before running this.

### Decision: renamed `ServiceLog` → `HomelabLog`, split into its own file
The original `src/models/service_log.py` (`ServiceLog` class) has been
replaced by `src/models/homelab_log.py` (`HomelabLog` class), and a new
`src/models/job_log.py` (`JobLog` class) sits alongside it.

**Why:** "ServiceLog" was a fine name when there was only one log type,
but it no longer describes what makes this type distinct now that Job
logs exist too. **Note for your git commit:** since this is a rename,
not an edit, your version control tooling may show this as a deleted
file (`service_log.py`) plus a new file (`homelab_log.py`) rather than a
tracked rename, depending on how you stage it. Either is fine
functionally — just don't be alarmed seeing a deletion in the diff.

### Decision: `Recommendation` field is Job-only for now
Per Open Question #5 in `docs/roadmap.md`, Homelab logs do not get a
`Recommendation` field yet, even though it might seem generically useful.
Left as Job-only until there's a real Homelab-side example (like the
Highway85 Wi-Fi case) confirming it's actually needed there too, rather
than adding it speculatively.

### Not yet done
- `HomelabLog`/`JobLog` are still schema-only — not wired into `main.py`,
  no storage logic, no log-type selector in the menu. This is the
  v0.3 roadmap item (see `docs/roadmap.md`).
- `LogStatus` values are a working draft, not confirmed final (Open
  Question #6).
- Attachments convention is documented but has no code behind it yet.

---

## 2026-08-28 — Teaching-style comments across all files

### Decision
Every file in the project gets comments that explain the underlying
Python concept the first time it appears, not just what a given line
does. New vocabulary (dataclasses, Enums, context managers, type hints,
truthiness, `continue`/`break`, etc.) is called out explicitly.

**Why:** You're using this project to learn, not just to have a working
tool. Comments that only restate "this creates a folder" don't teach
anything you didn't already know from reading the code. Comments that
name the underlying concept and explain *why* it's the right tool for
the job build a vocabulary you can carry into other projects.

**Trade-off accepted:** These files are now much longer and more
verbose than a "production" version would be — a working professional
codebase would not carry this much inline explanation. That's
intentional for now. Once concepts become familiar, it's reasonable to
trim comments back down to the more standard "explain the non-obvious
parts only" style. Revisit this decision once you're comfortable with
the concepts currently being explained in full.

### Decision: `ServiceLog` model built as schema-only, not yet wired in
`src/models/service_log.py` defines the fuller data shape (matching the
JJ laptop-fan example) but is intentionally NOT connected to `main.py`
yet. It doesn't save to disk, and the CREATE menu option still uses the
old, smaller field set (machine, title, status, summary).

**Why:** Keeping model definition and integration as separate steps
means each change is small enough to fully understand before moving to
the next. Wiring the model into `main.py` and deciding on storage
(markdown vs. SQLite) are both still open — see "Still open / deferred"
below.

---

## 2026-08-28 — v0.2 patch: timestamp bugs + basic validation

### Problem
`main.py` computed `created_timestamp` and `last_updated_timestamp` once,
at program start, in global scope. Every log created or updated during a
single run of the program showed the same "Created"/"Last Updated" value
— the moment the script launched, not the moment the action happened.
A correctly-computed per-entry `timestamp` variable existed in the CREATE
branch but was never actually used in the template.

### Decision: read timestamps from the filesystem, not from globals
Instead of tracking created/updated times in Python variables, `file_times()`
now reads `st_ctime` / `st_mtime` directly off the `.md` file on disk.

**Why:** The file itself is the source of truth. If we keep tracking time
in variables, every new feature (multi-session use, re-opening the app
later, editing logs outside the app) risks reintroducing the same class of
bug. Reading from the file's actual metadata means "last updated" is
correct by construction, not by discipline.

**Trade-off accepted:** `st_ctime` on some systems reflects "metadata
change time" rather than true creation time. For a single-writer, local
tool like this, that distinction doesn't matter yet. Worth revisiting if
TroubleLog ever moves to a real database (see Storage section below).

### Decision: minimal input validation now, full validation layer later
Added blank-field checks (machine name, log number, title, status,
summary, update status, update notes) directly in `main.py` for this
patch, rather than building the dedicated validation module discussed in
the brainstorm phase.

**Why:** You called out stronger input verification as a v1 priority, but
the current architecture (one flat script) doesn't have a natural home
for a validation layer yet. Rather than block this patch on a restructure,
we're closing the most obvious hole (empty submissions) now and revisiting
proper validation (enums for OS/device type, duplicate detection, date
logic) once the project moves toward the `src/models` structure discussed
earlier.

### Decision: added an escape hatch to the READ loop
Choice `2`'s `while True` loop previously had no way out except finding a
log that exists. Pressing Enter at the machine-name prompt now returns to
the main menu.

**Why:** A troubleshooting tool that traps the user because they forgot an
exact log number defeats its own purpose.

### Not changed
`menu.py` was reviewed and left as-is — no bugs found.

### Still open / deferred
- Fuller schema (requested_by, OS, device type, symptoms, diagnosis, root
  cause, fix applied, tools used, tags) from the JJ laptop-fan example is
  not yet reflected in the CREATE fields. Current schema: machine, title,
  status, summary.
- No listing/browsing across logs (e.g., "all logs for this machine," "all
  logs tagged overheating").
- No duplicate-detection beyond exact log-number collision (e.g., `"1"` vs
  `"01"` currently create separate files).
- Storage is flat markdown files per log. SQLite vs. file-based storage
  decision is still open — flagged in brainstorm, not yet decided.
