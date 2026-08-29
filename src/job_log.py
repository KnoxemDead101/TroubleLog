# ==========================================================
# TroubleLog — Job Log Type
# KTT Homelab Project
# ==========================================================
#
# WHAT THIS FILE IS FOR:
# The job-tracking extension — client/employer work like the real
# Highway85 A/V setup and Wi-Fi jobs. Built the same way as HomelabLog:
# inherits the shared core from LogEntry, adds only what's specific to a
# job. Read log_entry.py first if you're unsure how REQUIRED_FIELDS or
# __post_init__ work — this file relies on both.

from dataclasses import dataclass
from enum import Enum
from typing import ClassVar, List, Optional

from .log_entry import LogEntry, LogType


class JobCategory(str, Enum):
    """
    Job type categories — a controlled vocabulary instead of free text,
    same reasoning as OperatingSystem/DeviceType in homelab_log.py. Keeps
    future filtering/reporting (docs/roadmap.md v0.4) from breaking on
    inconsistent spelling or casing (e.g. "networking" vs "Networking").
    """
    NETWORKING = "Networking"
    HARDWARE = "Hardware"
    AV = "Audio/Visual"
    SOFTWARE = "Software"
    SECURITY = "Security"
    OTHER = "Other"


@dataclass
class JobLog(LogEntry):
    LOG_TYPE: ClassVar[LogType] = LogType.JOB

    REQUIRED_FIELDS: ClassVar[List[str]] = LogEntry.REQUIRED_FIELDS + [
        "client_employer",
    ]
    # Only ONE extra required field for Job logs, unlike HomelabLog's
    # three. `category`, `time_spent`, `fix`, and `recommendation` are
    # all intentionally optional (see comments on each field below for
    # why).

    # ---- Fields specific to Job logs ----

    client_employer: Optional[str] = None
    # Replaces "Machine" from the Homelab format — same "who/what this
    # entry is about" role, different meaning for this log type.

    category: JobCategory = JobCategory.OTHER

    time_spent: Optional[str] = None
    # OPEN QUESTION (docs/roadmap.md, Open Question #2): kept as free
    # text for now. IF YOU LATER BUILD HOURS-BY-CLIENT REPORTING (v0.4
    # roadmap item), this field will likely need to change from free
    # text (e.g. "about 2 hours") to a structured numeric value (e.g.
    # minutes as an int), since you can't reliably do math on arbitrary
    # text. Flagging here so future-you isn't surprised by that refactor.

    fix: Optional[str] = None
    # Deliberately kept separate from `summary` (inherited from
    # LogEntry) — isolates the actual resolution from the general
    # narrative, per your decision.

    recommendation: Optional[str] = None
    # Optional by design — only filled in when the core issue is
    # resolved but separate follow-up work remains outside the fix's
    # scope (the real Highway85 Wi-Fi extender case). Per the Status
    # Field decision (docs/roadmap.md), `status` should describe the
    # PRIMARY issue only — this field is what carries pending follow-up,
    # instead of inventing compound status values like
    # "Resolved / Pending."
