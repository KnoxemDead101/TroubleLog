from pathlib import Path
from menu import display_menu, get_user_choice
from datetime import datetime

# ==========================================================
# TroubleLog v0.2
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


directory_info()
print(f"TroubleLog started at {now_str()}")

while True:

    display_menu()
    choice = get_user_choice()

    # ======================================================
    # CREATE SERVICE LOG
    # ======================================================

    if choice == "1":

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

            log_number = input("Enter Service Log Number: ").strip()

            machine_folder = LOGS_DIRECTORY / machine
            filename = f"service-log-{log_number}.md"
            file_path = machine_folder / filename

            if file_path.exists():

                with open(file_path, "r", encoding="utf-8") as log_file:
                    contents = log_file.read()

                print("\n===================================")
                print(contents)
                print("===================================")

                break  # Exit the loop after successfully reading the log

            else:

                print(
                    f"\nService Log {log_number} was not found for machine {machine}."
                    f"\nPlease check the machine name and log number, and try again, "
                    f"or press Enter at the machine prompt to return to the menu."
                )

    # ======================================================
    # UPDATE SERVICE LOG
    # ======================================================

    elif choice == "3":

        machine = input("Enter Machine Name: ").strip().lower()
        log_number = input("Enter Service Log Number: ").strip()

        machine_folder = LOGS_DIRECTORY / machine
        filename = f"service-log-{log_number}.md"
        file_path = machine_folder / filename

        if file_path.exists():

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
                f"\nService Log {log_number} updated successfully "
                f"for machine {machine} on {update_timestamp}."
            )

        else:

            print(
                f"\nService Log {log_number} was not found for machine {machine}. "
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
