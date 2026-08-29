from pathlib import Path
from menu import display_menu, get_user_choice
from datetime import datetime

from job_log import JobLog, JobCategory
from log_entry import LogStatus
# ^ NEW: pulling in the Job log model and its supporting enums, so the
# CREATE flow can build a real, validated JobLog object instead of just
# writing raw strings to a file. `LogStatus` is imported so Job logs can
# offer a controlled list of statuses to choose from (Pending, In
# Progress, Resolved, Follow-Up Needed) instead of free text.
#
# NOTE: HomelabLog is intentionally NOT imported here. The existing
# Homelab CREATE flow below is left exactly as it was — untouched — so
# real logs like `friday`'s aren't put at any risk. Wiring HomelabLog
# into this same validated pattern is future work, tracked in
# decisions.md, not done in this pass.

# ==========================================================
# TroubleLog v0.3 (Job Log type added)
# KTT Homelab Project
# ==========================================================

SOURCE_DIRECTORY = Path(__file__).resolve().parent
PROJECT_DIRECTORY = SOURCE_DIRECTORY.parent
LOGS_DIRECTORY = PROJECT_DIRECTORY / "logs"

TIMESTAMP_FORMAT = "%Y-%m-%d %I:%M:%S %p"


def now_str():
    """Current timestamp, formatted consistently across the app."""
    return datetime.now().strftime(TIMESTAMP_FORMAT)


def file_times(file_path):
    """Read actual created/modified times from the file itself,
    instead of relying on a timestamp captured at program start."""
    stat = file_path.stat()
    created = datetime.fromtimestamp(stat.st_ctime).strftime(TIMESTAMP_FORMAT)
    updated = datetime.fromtimestamp(stat.st_mtime).strftime(TIMESTAMP_FORMAT)
    return created, updated


def directory_info():
    print(f"Source Directory: {SOURCE_DIRECTORY}")
    print(f"Project Directory: {PROJECT_DIRECTORY}")
    print(f"Logs Directory: {LOGS_DIRECTORY}")


def choose_enum(prompt_label, enum_cls):
    """
    Show a numbered list of every option in an Enum class, and keep
    asking until the user picks a valid number — then return the actual
    Enum member (not just the number or text they typed).

    WHY THIS EXISTS:
    JobCategory and LogStatus are Enums specifically to close off free-
    text typos ("Networking" vs "networking" vs "Netwrking"). But an
    Enum only protects you if the CODE asking for input restricts the
    choices too — if we just called input() and stuffed whatever the
    user typed into JobCategory, a typo would still be possible. This
    function is the actual enforcement point: the user can ONLY pick
    from what's listed.

    NEW CONCEPT: `enumerate(options, start=1)`
    `enumerate()` pairs each item in a list with a number, so instead of
    manually tracking a counter yourself, you get (1, first_item),
    (2, second_item), etc. `start=1` means numbering begins at 1 instead
    of Python's normal default of 0, matching how humans expect to count
    menu options.
    """
    options = list(enum_cls)
    # `list(enum_cls)` turns an Enum class into a plain list of its
    # members, in the order they were defined — e.g. list(JobCategory)
    # gives [JobCategory.NETWORKING, JobCategory.HARDWARE, ...].

    print(f"\n{prompt_label}:")
    for index, member in enumerate(options, start=1):
        print(f"  {index}. {member.value}")

    while True:
        choice = input("Select a number: ").strip()

        if choice.isdigit() and 1 <= int(choice) <= len(options):
            # NEW CONCEPT: `.isdigit()`
            # Checks whether a string contains ONLY digit characters
            # (e.g. "3" -> True, "3.5" -> False, "three" -> False). This
            # has to be checked BEFORE calling int(choice), because
            # int("three") would crash the program with an exception —
            # this guards against that before it can happen.
            return options[int(choice) - 1]
            # Subtracting 1 converts from human-friendly numbering
            # (starting at 1) back to Python's actual list indexing
            # (starting at 0).

        print("Invalid selection. Please enter one of the listed numbers.")


def resolve_log_file(folder, log_number):
    """
    Given a folder and a log number, figure out which actual file exists
    — since a folder can now contain EITHER a Homelab log
    ("service-log-N.md") OR a Job log ("job-log-N.md"), and Read/Update
    need to work regardless of which type is sitting there.

    Returns the matching Path if found, or None if neither exists.
    """
    candidates = [
        folder / f"service-log-{log_number}.md",
        folder / f"job-log-{log_number}.md",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


directory_info()
print(f"TroubleLog started at {now_str()}")

while True:

    display_menu()
    choice = get_user_choice()

    # ======================================================
    # CREATE SERVICE LOG
    # ======================================================

    if choice == "1":

        log_type_choice = input(
            "\nLog Type — 1) Homelab   2) Job\nSelect: "
        ).strip()

        # ==================================================
        # CREATE JOB LOG
        # ==================================================
        if log_type_choice == "2":

            client_employer = input("Enter Client / Employer Name: ").strip().lower()
            log_number = input("Enter Job Log Number: ").strip()

            if not client_employer or not log_number:
                print("\nClient/Employer name and log number cannot be blank. Please try again.")
                continue

            client_folder = LOGS_DIRECTORY / client_employer
            # Same folder convention as Homelab logs — a folder named
            # after the client/employer (e.g. "highway85"), sitting
            # alongside machine folders like "friday" in the same
            # top-level logs/ directory. This was the specific design
            # point being confirmed: one shared folder-per-name pattern,
            # not a separate structure per log type.
            client_folder.mkdir(parents=True, exist_ok=True)

            filename = f"job-log-{log_number}.md"
            file_path = client_folder / filename

            if file_path.exists():
                created, updated = file_times(file_path)
                print(
                    f"\nJob Log {log_number} already exists for {client_employer} "
                    f"(created {created}, last updated {updated}). "
                    f"Please choose a different log number."
                )
                continue

            title = input("Title: ").strip()
            summary = input("Summary: ").strip()
            fix = input("Fix (leave blank if not yet resolved): ").strip()
            recommendation = input(
                "Recommendation (optional — leave blank if none): "
            ).strip()
            time_spent = input("Time Spent (e.g. '2 hours', or leave blank): ").strip()
            tags_input = input("Tags (comma-separated, e.g. av, mixer, xlr): ").strip()

            status = choose_enum("Status", LogStatus)
            category = choose_enum("Category", JobCategory)

            try:
                job = JobLog(
                    log_number=log_number,
                    title=title,
                    summary=summary,
                    client_employer=client_employer,
                    category=category,
                    status=status,
                    time_spent=time_spent or None,
                    fix=fix or None,
                    recommendation=recommendation or None,
                )
                # NEW CONCEPT: `value or None`
                # Empty strings ("") are "falsy" in Python. `time_spent or
                # None` means: if time_spent is a non-empty string, use
                # it; if it's empty, use None instead. This matters here
                # because JobLog's Optional fields are meant to represent
                # "genuinely not provided," and storing "" instead of
                # None would be a less accurate way to say that.
            except ValueError as error:
                # This is where LogEntry's required-field validation
                # (from log_entry.py) actually gets used for the first
                # time in the running app. If log_number, title, or
                # summary were left blank, JobLog's __post_init__ raises
                # ValueError, and we catch it here instead of letting the
                # whole program crash.
                print(f"\nJob Log was not created: {error}")
                continue

            for raw_tag in tags_input.split(","):
                # `.split(",")` breaks "av, mixer, xlr" into
                # ["av", " mixer", " xlr"] — note the leading spaces on
                # later items, which is exactly why add_tag() (in
                # log_entry.py) calls .strip() on each tag internally.
                if raw_tag.strip():
                    job.add_tag(raw_tag)

            if job.status == LogStatus.RESOLVED:
                job.mark_resolved()
                # Keeps date_resolved consistent with a RESOLVED status
                # chosen at creation time, rather than leaving it None
                # until a separate Update happens later.

            recommendation_section = ""
            if job.recommendation:
                recommendation_section = f"""
## Recommendation (optional)

{job.recommendation}
"""
                # Only included when actually provided — an empty
                # "## Recommendation (optional)" header with nothing
                # under it would be noise in a log meant to be read
                # later, per the field's own "optional" design intent.

            tags_line = ", ".join(job.tags) if job.tags else "none"

            log_content = f"""# Job Log {job.log_number}

## Client / Employer

{job.client_employer}

## Category

{job.category.value}

## Title

{job.title}

## Status

{job.status.value}

## Time Spent

{job.time_spent or "TBD"}

## Summary

{job.summary}

## Fix

{job.fix or "Not yet resolved."}
{recommendation_section}
## Tags

{tags_line}

## Created
{now_str()}

## Last Updated
{now_str()}

"""

            with open(file_path, "w", encoding="utf-8") as log_file:
                log_file.write(log_content)

            print(
                f"\nJob Log {log_number} created successfully "
                f"for {client_employer}."
            )

            continue
            # Skip straight back to the top of the menu loop — everything
            # below this point in choice "1" is the ORIGINAL Homelab
            # flow, which a Job log entry has no business running through.

        # ==================================================
        # CREATE HOMELAB LOG (UNCHANGED FROM BEFORE)
        # ==================================================

        machine = input("Enter Machine Name: ").strip().lower()
        log_number = input("Enter Service Log Number: ").strip()

        if not machine or not log_number:
            print("\nMachine name and log number cannot be blank. Please try again.")
            continue

        machine_folder = LOGS_DIRECTORY / machine
        machine_folder.mkdir(parents=True, exist_ok=True)

        filename = f"service-log-{log_number}.md"
        file_path = machine_folder / filename

        if file_path.exists():

            created, updated = file_times(file_path)
            print(
                f"\nService Log {log_number} already exists for machine {machine} "
                f"(created {created}, last updated {updated}). "
                f"Please choose a different log number."
            )

        else:

            title = input("Title: ").strip()
            status = input("Status: ").strip()
            summary = input("Summary: ").strip()

            if not title or not status or not summary:
                print("\nTitle, status, and summary cannot be blank. Log was not created.")
                continue

            entry_timestamp = now_str()
            log_content = f"""# Service Log {log_number}

## Machine

{machine}

## Title

{title}

## Created
{entry_timestamp}

## Status

{status}

## Summary

{summary}

## Last Updated
{entry_timestamp}

"""

            with open(file_path, "w", encoding="utf-8") as log_file:
                log_file.write(log_content)

            print(
                f"\nService Log {log_number} created successfully "
                f"for machine {machine} on {entry_timestamp}."
            )

    # ======================================================
    # READ SERVICE LOG
    # ======================================================

    elif choice == "2":

        while True:
            machine = input(
                "Enter Machine Name (or press Enter to return to menu): "
            ).strip().lower()

            if machine == "":
                break

            log_number = input("Enter Log Number: ").strip()

            machine_folder = LOGS_DIRECTORY / machine
            file_path = resolve_log_file(machine_folder, log_number)
            # Checks for EITHER "service-log-{n}.md" (Homelab) OR
            # "job-log-{n}.md" (Job) inside this folder — the person
            # reading a log shouldn't have to remember which type it was
            # just to look it up.

            if file_path is not None:

                with open(file_path, "r", encoding="utf-8") as log_file:
                    contents = log_file.read()

                print("\n===================================")
                print(contents)
                print("===================================")

                break  # Exit the loop after successfully reading the log

            else:

                print(
                    f"\nLog {log_number} was not found for {machine}."
                    f"\nPlease check the name and log number, and try again, "
                    f"or press Enter at the name prompt to return to the menu."
                )

    # ======================================================
    # UPDATE SERVICE LOG
    # ======================================================

    elif choice == "3":

        machine = input("Enter Machine/Client Name: ").strip().lower()
        log_number = input("Enter Log Number: ").strip()

        machine_folder = LOGS_DIRECTORY / machine
        file_path = resolve_log_file(machine_folder, log_number)
        # Same folder-agnostic lookup as the Read branch above — Update
        # shouldn't care whether this was originally a Homelab or Job log.

        if file_path is not None:

            update_status = input("Updated Status: ").strip()
            update_notes = input("Update Notes: ").strip()

            if not update_status or not update_notes:
                print("\nUpdated status and notes cannot be blank. Update was not saved.")
                continue

            update_timestamp = now_str()
            update_content = f"""

----------------------------------------

## Service Log Update

**Updated Status**

{update_status}

**Time Updated Last**
{update_timestamp}

### Notes

{update_notes}

"""

            with open(file_path, "a", encoding="utf-8") as log_file:
                log_file.write(update_content)

            print(
                f"\nLog {log_number} updated successfully "
                f"for {machine} on {update_timestamp}."
            )

        else:

            print(
                f"\nLog {log_number} was not found for {machine}. "
                f"Nothing to update."
            )

    # ======================================================
    # EXIT
    # ======================================================

    elif choice == "4":

        print("\nClosing TroubleLog...")
        print(f"TroubleLog closed at {now_str()}.")
        break

    # ======================================================
    # INVALID MENU CHOICE
    # ======================================================

    else:

        print(
            "\nInvalid menu selection. "
            "Please choose an option from 1-4."
        )
