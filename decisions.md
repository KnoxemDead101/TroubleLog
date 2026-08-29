# TroubleLog — Decisions Log

Ongoing record of *why* things were built or changed a certain way.
Paired with `CHANGELOG.md`, which tracks *what* changed and *when*.

---

## 2026-08-29 — Job logs wired into main.py

### Decision: folder keyed on name, not on log type
Confirmed directly: the logs/ folder structure is keyed on WHO/WHAT the
log is about (machine name for Homelab, client/employer name for Job),
not on log type. A Job log for Highway85 lives in logs/highway85/,
sitting alongside logs/friday/ (Homelab) at the same directory level —
one shared convention, not a split structure. This directly resolves
the ambiguity that existed between this and the earlier-drafted
Attachments Convention note (which had sketched a logs/jobs/<client>/
path) — logs/<name>/ is the actual, confirmed convention going forward;
the attachments sub-path should be read as logs/<name>/attachments/ to
match.

### Decision: Homelab CREATE flow left untouched in this pass
Only the Job log path was wired to use the full model + validation +
choose_enum() pattern. Homelab CREATE still uses its original simple
4-field flow.

Why: friday and other machines already have real logs written in the
original simple format. Changing the Homelab CREATE flow in the same
pass as introducing Job logs would mean touching two risky things at
once. Job logs had no existing real app-generated data to protect, so
they were the safer place to prove out the model+validation+enum
pattern first. Upgrading Homelab CREATE to the same pattern is a
reasonable next step, but deliberately deferred to its own pass.

### Decision: enums enforced via a picker, not just declared
Declaring OperatingSystem/DeviceType/JobCategory/LogStatus as Enums
(done in an earlier pass) only prevents typos if the CODE asking for
input actually restricts choices to those values. Added choose_enum()
in main.py as the actual enforcement point for Job logs — a numbered
list the user picks from, rather than free text matched against the
enum after the fact. This is the first real, running instance of the
"stronger input verification" goal from the original brainstorm being
enforced in the live app, not just designed on paper.

### Verified before handoff
Ran a full Create -> Read -> Update cycle on a real Job log through the
actual main.py, and separately re-ran the original Homelab Create flow
to confirm its output is unchanged. Both confirmed working.

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
Per Open Question #5 in `decisions.md` (Roadmap & Open Questions section), Homelab logs do not get a
`Recommendation` field yet, even though it might seem generically useful.
Left as Job-only until there's a real Homelab-side example (like the
Highway85 Wi-Fi case) confirming it's actually needed there too, rather
than adding it speculatively.

### Not yet done
- `HomelabLog`/`JobLog` are still schema-only — not wired into `main.py`,
  no storage logic, no log-type selector in the menu. This is the
  v0.3 roadmap item (see `decisions.md` (Roadmap & Open Questions section)).
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

---

## Roadmap & Open Questions

*(Merged in here since this project keeps a single root-level `decisions.md`
rather than a separate `docs/` folder — this section was originally
drafted as a standalone `roadmap.md` and is consolidated here to match
the actual project layout.)*

### Log Types
TroubleLog supports two log types sharing one core (`log_entry.py`):
- **Homelab log** (`homelab_log.py`) — on-site tech tickets, e.g. the JJ
  laptop-fan example. Keyed on `machine`.
- **Job log** (`job_log.py`) — client/employer work, e.g. the Highway85
  A/V and Wi-Fi jobs. Keyed on `client_employer`.

Shared fields (in `LogEntry`): log_number, title, status, summary, tags,
date_reported, date_resolved.

### Job Log Format
New fields on top of the shared core: Client/Employer (replaces
"Machine"), Category, Time Spent, Fix (isolated from Summary),
Recommendation (optional — for jobs resolved on the core issue but with
pending follow-up outside the fix's scope), Tags (inherited from the
shared core).

### Status Field
Decision: `Status` describes the primary issue only. Pending follow-up
work lives in `Recommendation`, not in a compound status value.

### Attachments Convention
Markdown can't hold files directly. Convention: store in a sibling
`attachments/` folder per client (e.g.
`logs/jobs/highway85/attachments/job-002-wifi-speedtest.png`), reference
via relative Markdown image links, filenames tied to job log number.
Not yet implemented in code.

### Roadmap
**v0.3:** log type selector on creation, job log format wired into
storage, attachment folder convention adopted.
**v0.4:** search/filter by tag/category/client, basic report generation.
**v1.0:** unified library search across both log types.

### Open Questions (unresolved)
1. Should client/employer names be anonymized/abbreviated for confidentiality (NDA jobs)?
2. Time tracking: plain text for now, or eventually structured for reports?
3. Tags: free-text or a controlled list?
4. Attachments: manual save, or should the app prompt/remind?
5. Should Homelab logs also get a Category field eventually?
6. Full list of valid Status values needs to be confirmed.
