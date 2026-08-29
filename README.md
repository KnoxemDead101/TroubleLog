# TroubleLog

## Overview

TroubleLog is a lightweight Python command-line application designed to document and organize homelab maintenance, troubleshooting, and system administration tasks.

Originally developed as a learning project, TroubleLog has grown into a practical utility for recording service history across multiple computers and servers. It serves as both a documentation tool and a way to strengthen Python programming skills.

The primary goal of TroubleLog is to maintain a searchable history of system changes while reinforcing software development fundamentals such as file handling, modular programming, version control, and project organization.

---

## Project Goals

* Learn Python through a real-world application.
* Document Linux and Windows system administration tasks.
* Maintain organized service logs for multiple machines.
* Practice Git and professional software development workflows.
* Build a portfolio-quality command-line application.

---

## Current Features

* Create new service logs
* Read existing service logs
* Update existing service logs
* Multi-machine support
* Automatic machine directory creation
* Markdown-based service logs
* Simple command-line interface
* Accurate per-entry timestamps (read from file metadata, not a single
  program-start value)
* Escape hatch on the Read menu (blank input returns to main menu)
* Basic blank-field validation on Create/Update
* `HomelabLog` / `JobLog` data models with shared core fields, built and
  tested, not yet wired into the running app (see Planned Features, v0.3)

---

## Project Structure

```text
TroubleLog/
├── logs/
│   ├── friday/
│   ├── windows-pc/
│   └── macbook/
│
├── src/
│   ├── main.py           # CLI entry point / menu loop
│   ├── menu.py            # menu display + choice validation
│   ├── log_entry.py        # shared LogEntry base class + LogType/LogStatus enums
│   ├── homelab_log.py      # HomelabLog model (on-site tech tickets)
│   ├── job_log.py          # JobLog model (client/employer work)
│   └── check_models.py     # runnable sanity check for the three files above
│
├── README.md
├── CHANGELOG.md
├── decisions.md
└── .gitignore
```

---

## Service Log Format

Each service log is stored as a Markdown document.

Example:

```markdown
# Service Log 001

## Machine

Friday

## Title

Installed OpenSSH Server

## Status

Resolved

## Summary

Installed and configured OpenSSH Server for remote administration.
```

---

## Current Version

**v0.3-planning-2**

Current functionality includes:

* Create Service Log
* Read Service Log
* Update Service Log
* Multi-machine support
* Correct per-entry timestamps and basic input validation (v0.2 patches)
* `HomelabLog` and `JobLog` data models, tested and working via
  `check_models.py`, not yet connected to the running app

See `CHANGELOG.md` for the full version-by-version history and
`decisions.md` for the reasoning behind each design choice.

---

## Planned Features

### v0.3 (in progress)

* Log type selector (Homelab vs. Job) on log creation
* Job log format wired into storage: client/employer, category, time
  spent, fix, recommendation, tags
* Attachment folder convention adopted in storage layer
  (`logs/<type>/<name>/attachments/`, referenced via relative Markdown
  image links)
* Delete service logs
* Search logs

### v0.4

* Search/filter by tag, category, or client
* Basic report generation for job logs (hours by client, issues by category)
* Log statistics

### v1.0

* Unified library search across Homelab and Job logs
* Stable command-line release
* Complete documentation
* Cross-platform support
* Production-ready project structure

---

## Open Questions (unresolved)

Tracked in detail in `decisions.md`; summarized here for visibility:

1. Should client/employer names be anonymized/abbreviated for confidentiality (NDA jobs)?
2. Time tracking: plain text field for now, or eventually feed into totals/reports?
3. Tags: free-text or a controlled list?
4. Attachments: manual save, or should the app prompt/remind when a log references one?
5. Should Homelab logs also get a Category field eventually, or stay simpler on purpose?
6. Full list of valid Status values needs to be confirmed (Pending, Resolved, + others?)

---

## Technologies

* Python 3
* pathlib
* Markdown
* Git
* Visual Studio Code

---

## Purpose

TroubleLog is one component of the KTT Software Ecosystem.

It is intended to operate as a standalone application while serving as a learning platform for Python, Linux administration, and software engineering principles.

---

## Author

**Leighton Knox**

KTT Software Development

Built to document systems, strengthen programming skills, and support continuous learning through real-world projects.
