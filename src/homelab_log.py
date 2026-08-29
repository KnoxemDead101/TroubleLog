# ==========================================================
# TroubleLog — Homelab Log Type
# KTT Homelab Project
# ==========================================================
#
# WHAT THIS FILE IS FOR:
# The original TroubleLog use case — homelab/on-site tech tickets like
# the JJ laptop-fan example. Was previously its own standalone class
# (`ServiceLog`); now renamed `HomelabLog` and rebuilt to inherit shared
# fields from LogEntry (see log_entry.py) instead of duplicating them.
#
# If you're reimplementing this file or debugging errors, read
# log_entry.py first — the REQUIRED_FIELDS / __post_init__ pattern used
# there is what makes the "required" fields below actually get enforced.

from dataclasses import dataclass, field
from enum import Enum
from typing import ClassVar, List, Optional

from .log_entry import LogEntry, LogType
# The leading dot means "import from log_entry.py in this SAME folder."
# This only works because src/models/ has an __init__.py file in it
# (even though that file is empty) — that's what makes Python treat this
# folder as an importable "package" rather than just a folder of loose
# scripts. IF THIS IMPORT FAILS ON YOUR DESKTOP: check that
# src/models/__init__.py and src/__init__.py both exist, and that you're
# running the program from the project's root folder (not from inside
# src/models/ itself).


class OperatingSystem(str, Enum):
    WINDOWS = "Windows"
    MACOS = "macOS"
    LINUX = "Linux"
    CHROMEOS = "ChromeOS"
    OTHER = "Other"


class DeviceType(str, Enum):
    LAPTOP = "Laptop"
    DESKTOP = "Desktop"
    TABLET = "Tablet"
    SERVER = "Server"
    NETWORK_DEVICE = "Network Device"
    OTHER = "Other"


@dataclass
class HomelabLog(LogEntry):
    # Inheriting from LogEntry means every field and method LogEntry
    # already defines (log_number, title, summary, status, tags,
    # date_reported, date_resolved, mark_resolved(), add_tag(),
    # __post_init__ validation) comes along automatically. This class
    # only needs to define what makes a Homelab log DIFFERENT.

    LOG_TYPE: ClassVar[LogType] = LogType.HOMELAB
    # Overrides LogEntry's placeholder — every HomelabLog now correctly
    # reports itself as a Homelab-type log.

    REQUIRED_FIELDS: ClassVar[List[str]] = LogEntry.REQUIRED_FIELDS + [
        "machine",
        "requested_by",
        "reported_symptoms",
    ]
    # NEW CONCEPT: extending an inherited list instead of retyping it
    # `LogEntry.REQUIRED_FIELDS` is ["log_number", "title", "summary"].
    # Using `+` here builds a NEW list that's the base list plus this
    # class's own required fields, so we never have to retype or risk
    # forgetting the base three. If LogEntry's required list ever
    # changes, this line picks up that change automatically next time
    # the code runs.

    # ---- Fields specific to Homelab logs (all default to None/empty,
    #      per the pattern explained in log_entry.py) ----
    machine: Optional[str] = None
    requested_by: Optional[str] = None
    reported_symptoms: Optional[str] = None

    operating_system: OperatingSystem = OperatingSystem.OTHER
    device_type: DeviceType = DeviceType.OTHER
    location: Optional[str] = None
    program_context: Optional[str] = None
    diagnosis: Optional[str] = None
    root_cause: Optional[str] = None
    fix_applied: Optional[str] = None
    tools_used: List[str] = field(default_factory=list)
