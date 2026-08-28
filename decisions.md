# TroubleLog — Decisions Log

Ongoing record of *why* things were built or changed a certain way.
Paired with `CHANGELOG.md`, which tracks *what* changed and *when*.

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
