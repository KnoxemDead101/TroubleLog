# ==========================================================
# TroubleLog — Manual Model Check
# KTT Homelab Project
# ==========================================================
#
# WHAT THIS FILE IS FOR:
# A quick, runnable sanity check for the model files in src/models/.
# Not a "real" automated test suite (that would use a tool like pytest)
# — just a plain script you can run directly to confirm the models
# import correctly and behave as expected on YOUR desktop's Python
# install, before building anything else on top of them.
#
# HOW TO RUN THIS:
#   This file lives in src/, alongside main.py, homelab_log.py, etc.
#   From inside the src/ folder, run:
#       python3 check_models.py
#
# WHAT SUCCESS LOOKS LIKE:
#   You'll see two log summaries printed, each ending in "OK" — no
#   error/traceback text (typically red, or ending in "Error: ...").
#
# WHAT A FAILURE LOOKS LIKE, AND WHAT IT PROBABLY MEANS:
#   - "ModuleNotFoundError: No module named 'homelab_log'" (or similar)
#       -> You're not running this from inside the src/ folder, or one
#          of homelab_log.py/job_log.py/log_entry.py is missing from it.
#   - "ValueError: HomelabLog is missing required field(s): ..."
#       -> A required field wasn't filled in below — this one is
#          EXPECTED to happen in the "should fail" section further down,
#          proving the validation actually works.

from homelab_log import HomelabLog, OperatingSystem, DeviceType
from job_log import JobLog, JobCategory
from log_entry import LogStatus
# Plain imports, matching the flat src/ layout — see the same note in
# homelab_log.py / job_log.py.


def check_homelab_log() -> None:
    """Build a HomelabLog matching the real JJ laptop-fan example, and
    confirm the fields come back out the way they went in."""

    entry = HomelabLog(
        log_number="001",
        title="Laptop overheating — fan replacement",
        summary="JJ reported overheating with visible plastic debris.",
        machine="jj-laptop",
        requested_by="JJ",
        reported_symptoms="Laptop overheating, small plastic chips falling out.",
        operating_system=OperatingSystem.WINDOWS,
        device_type=DeviceType.LAPTOP,
        diagnosis="One fan warped from heat, one fan's blades chipped, third fan fine.",
        root_cause="Thermal stress on fan housing/blades.",
        fix_applied="Replaced all three laptop fans.",
    )

    entry.add_tag("overheating")
    entry.add_tag("fans")
    entry.add_tag("hardware")
    entry.mark_resolved()

    assert entry.LOG_TYPE.value == "Homelab"
    assert entry.status == LogStatus.RESOLVED
    assert entry.date_resolved is not None
    assert "overheating" in entry.tags
    # NEW CONCEPT: `assert`
    # This immediately raises an error and stops the script if the
    # condition after it is False. It's a lightweight way to say "if this
    # ISN'T true, something is broken — stop here" without writing a full
    # if/else block.

    print(f"[HomelabLog] {entry.machine} — {entry.title} — status: {entry.status.value} — OK")


def check_job_log() -> None:
    """Build a JobLog matching the real Highway85 A/V example, and
    confirm the fields come back out the way they went in."""

    entry = JobLog(
        log_number="001",
        title="A/V Equipment Setup — Mixer, Speakers, Wireless Mic System",
        summary="Set up mixer, speakers, and wireless mic system for Highway85.",
        client_employer="Highway85",
        category=JobCategory.AV,
        fix="Configured and tested full A/V signal chain.",
        recommendation=None,
    )

    entry.add_tag("av")
    entry.add_tag("mixer")
    entry.add_tag("xlr")
    entry.add_tag("wireless-mic")
    entry.mark_resolved()

    assert entry.LOG_TYPE.value == "Job"
    assert entry.status == LogStatus.RESOLVED
    assert "wireless-mic" in entry.tags

    print(f"[JobLog] {entry.client_employer} — {entry.title} — status: {entry.status.value} — OK")


def check_required_field_validation() -> None:
    """
    Confirm that leaving out a required field actually raises an error,
    instead of silently creating a broken/incomplete log. This SHOULD
    print an error message below — that's success, not failure, for this
    specific check.
    """
    try:
        HomelabLog(log_number="002", title="Missing summary and machine")
        # No summary, no machine, no requested_by, no reported_symptoms —
        # this should be rejected by LogEntry's required-field check.
        print("[Validation check] FAILED — expected a ValueError, but none was raised.")
    except ValueError as error:
        print(f"[Validation check] Correctly rejected incomplete log — OK\n  ({error})")


if __name__ == "__main__":
    # NEW CONCEPT: `if __name__ == "__main__":`
    # This block only runs when the file is executed DIRECTLY (e.g.
    # `python3 check_models.py`), not when it's imported by some other
    # file. Standard Python convention for "the actual entry point of
    # this script."
    check_homelab_log()
    check_job_log()
    check_required_field_validation()
    print("\nAll checks completed.")
