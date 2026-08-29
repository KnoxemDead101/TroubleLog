# ==========================================================
# TroubleLog — Shared Log Core
# KTT Homelab Project
# ==========================================================
#
# WHAT THIS FILE IS FOR:
# TroubleLog supports TWO kinds of logs — Homelab logs (the original
# JJ-laptop-style entries) and Job logs (client/employer work). This file
# defines the ONE shared base both types build on top of, so fields like
# title/status/summary/tags/timestamps only exist in one place.
#
# VERSION NOTE — READ THIS IF SOMETHING BREAKS ON YOUR DESKTOP:
# An earlier draft of this file used `@dataclass(kw_only=True)`, which
# ONLY works on Python 3.10 or newer. This version avoids that entirely
# and works on Python 3.7+, so it should run regardless of your desktop's
# Python version. If you ever see an error mentioning "kw_only" or
# "unexpected keyword argument," that means you're looking at the OLD
# version of this file by mistake — replace it with this one.
#
# HOW TO CHECK YOUR PYTHON VERSION LATER (for reference):
#   Run this in a terminal:  python3 --version
#   or from inside Python:   import sys; print(sys.version)

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import ClassVar, List, Optional


class LogType(str, Enum):
    """Which kind of log this is — used to tag entries and, later, to
    pick which menu fields to ask for and which storage folder to use."""
    HOMELAB = "Homelab"
    JOB = "Job"


class LogStatus(str, Enum):
    """
    Allowed status values, shared across both log types.

    OPEN QUESTION (see docs/roadmap.md, Open Question #6): this list is
    a working draft, not yet confirmed as final/complete. If you add or
    remove a value here, every log already saved with the old value will
    still load fine (it's just a string underneath) — but any VALIDATION
    code that checks "is this status allowed" will need this list to be
    accurate, so keep it in sync with docs/roadmap.md.
    """
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    FOLLOW_UP_NEEDED = "Follow-Up Needed"


@dataclass
class LogEntry:
    """
    The core fields every TroubleLog entry has, regardless of type.

    This class is NOT meant to be created directly in normal use — you
    should be creating HomelabLog or JobLog instances instead (see
    homelab_log.py / job_log.py), both of which inherit everything below
    automatically and add their own extra fields on top.

    ----------------------------------------------------------------
    WHY EVERY FIELD HERE HAS A DEFAULT, EVEN "REQUIRED" ONES
    ----------------------------------------------------------------
    Plain Python dataclasses enforce a strict rule: every field WITHOUT a
    default value must be listed before every field WITH a default
    value, across the ENTIRE class hierarchy (base class + all
    subclasses combined, as if they were one long list).

    That rule causes a real problem for this project's design: HomelabLog
    needs to add its OWN required fields (like `machine`) AFTER
    inheriting optional fields from this base class (like `status`,
    which already has a default). Python would refuse to run that combo
    with plain dataclasses.

    There are two ways to fix this:
      1. `@dataclass(kw_only=True)` — clean, but Python 3.10+ only.
      2. Give every field a default (usually None), and enforce
         "required" ourselves in code — works on Python 3.7+.

    This file uses option 2, for maximum compatibility with whatever
    Python version is already on your desktop/Replit. If you later
    confirm you're on 3.10+, option 1 is arguably cleaner — but this
    version will keep working either way, so there's no urgency to
    switch.
    """

    # ---- Core fields (all have defaults — see explanation above) ----
    log_number: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None

    status: LogStatus = LogStatus.PENDING
    tags: List[str] = field(default_factory=list)
    date_reported: datetime = field(default_factory=datetime.now)
    date_resolved: Optional[datetime] = None

    # ---- Class-level info, not per-instance data ----

    LOG_TYPE: ClassVar[LogType]
    # `ClassVar` means this belongs to the CLASS itself, not to each
    # individual object — every HomelabLog shares one LOG_TYPE value.
    # Because it's a ClassVar, dataclasses skip it when building
    # __init__, so it doesn't affect the required/optional field
    # ordering discussed above at all. Each subclass sets this to say
    # "I am a Homelab log" or "I am a Job log."

    REQUIRED_FIELDS: ClassVar[List[str]] = ["log_number", "title", "summary"]
    # THIS is where "required" actually lives now, since it can't live in
    # field ordering anymore. This is a list of FIELD NAMES (as strings)
    # that must not be left blank. Subclasses override this list to add
    # their own required field names on top of these three — see
    # HomelabLog.REQUIRED_FIELDS / JobLog.REQUIRED_FIELDS for examples.

    # ------------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------------

    def __post_init__(self):
        """
        Dataclasses automatically call this method (if defined) right
        after the auto-generated __init__ finishes setting every field.
        This is the standard place to put validation that needs to
        look at the object as a whole, after all fields already exist.

        IF YOU'RE DEBUGGING AN ERROR HERE:
        A ValueError raised from this method means required-field
        validation failed — read the error message, it names exactly
        which field(s) were left blank.
        """
        self._validate_required_fields()

    def _validate_required_fields(self) -> None:
        """
        Loop through self.REQUIRED_FIELDS and check that none of those
        named fields were left blank (None, or an empty string).

        IMPORTANT: `self.REQUIRED_FIELDS` — because this is looked up on
        the ACTUAL object at runtime, a HomelabLog instance automatically
        uses HomelabLog's longer list (not this base class's shorter
        one), even though this method itself is only written once, here,
        in LogEntry. This behavior — "the same inherited method acts
        differently depending on which subclass is using it" — is called
        polymorphism. If you're trying to reimplement or extend this
        later, this is the key mechanism to understand: don't hardcode
        field names in THIS method, always go through self.REQUIRED_FIELDS.
        """
        missing = [
            field_name
            for field_name in self.REQUIRED_FIELDS
            if not getattr(self, field_name)
        ]
        # `getattr(self, field_name)` fetches an attribute by NAME, as a
        # string — equivalent to `self.machine` but usable when the field
        # name itself is a variable, not something typed out literally.
        # This is what lets one loop check an arbitrary list of fields.

        if missing:
            raise ValueError(
                f"{self.__class__.__name__} is missing required field(s): "
                f"{', '.join(missing)}"
            )
            # `self.__class__.__name__` reports the REAL subclass name
            # ("HomelabLog" or "JobLog") in the error, even though this
            # raise statement is only written once, here in the base
            # class. Useful for debugging — the error tells you exactly
            # which type of log and which field(s) caused the problem.

    # ------------------------------------------------------------
    # SHARED BEHAVIOR
    # ------------------------------------------------------------

    def mark_resolved(self) -> None:
        """Set status to RESOLVED and stamp the resolution time, in one call."""
        self.status = LogStatus.RESOLVED
        self.date_resolved = datetime.now()

    def add_tag(self, tag: str) -> None:
        """Add a tag if it isn't already present (case-insensitive, avoids duplicates)."""
        normalized = tag.strip().lower()
        if normalized and normalized not in self.tags:
            self.tags.append(normalized)
