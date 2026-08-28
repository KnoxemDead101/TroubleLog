from pathlib import Path


def display_menu():
    print("Welcome to the Menu!")
    print("1. Create Service Log")
    print("2. Read Service Log")
    print("3. Update Service Log")
    print("4. Exit")


def get_user_choice():
    choice = input("\nSelect an option: ").strip()
    while True:
        if choice in ["1", "2", "3", "4"]:
            break
        else:
            print("Invalid choice. Please select a valid option.")
            choice = input("\nSelect an option: ").strip()
    return choice
