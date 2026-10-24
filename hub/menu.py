"""Main menu."""
from .ui import clear, print_logo, readchar, term_width, DIM, RESET
from .explorer import screen_explorer
from .screens import screen_run, screen_settings, screen_update, screen_about

MENU_ITEMS = [
    ("1", "File explorer"),
    ("2", "Run Python script"),
    ("3", "Settings"),
    ("4", "Update from git"),
    ("5", "About"),
    ("0", "Exit"),
]


def render():
    clear()
    print_logo()
    print("  main menu")
    print("  " + "-" * min(term_width(), 46))
    for key, label in MENU_ITEMS:
        print(f"  [{key}] {label}")
    print("  " + "-" * min(term_width(), 46))
    print(f"  {DIM}Press a number, Q to quit.{RESET}")


def main_menu() -> str:
    while True:
        render()
        key = readchar.readkey()
        if key in ("q", "Q", "0"):
            return "exit"
        elif key == "1":
            screen_explorer()
        elif key == "2":
            screen_run()
        elif key == "3":
            screen_settings()
        elif key == "4":
            screen_update()
        elif key == "5":
            screen_about()
