"""Main menu."""
from .ui import (
    clear, print_logo, readchar, term_width, print_header,
    box_top, box_mid, box_sep, box_bottom, pad_ansi,
    ACCENT, ACCENT2, BOLD, DIM, MUTED, RESET, V,
)
from .explorer import screen_explorer
from .screens import (
    screen_run, screen_settings, screen_update, screen_about,
    screen_envs, screen_history,
)
from .games import screen_games

MENU_ITEMS = [
    ("1", "File explorer", "browse and run files"),
    ("2", "Run Python script", "with args and venv"),
    ("3", "Settings", "editor, paths, venv"),
    ("4", "Update from git", "pull latest version"),
    ("5", "Environments", "manage venv"),
    ("6", "Run history", "recent executions"),
    ("7", "Games", "small breaks"),
    ("8", "About", "info"),
    ("0", "Exit", ""),
]


def render():
    clear()
    print_logo()
    print(f"{MUTED}  terminal hub for python on termux{RESET}")
    print()

    width = term_width()
    print(box_top(" MAIN MENU "))
    for key, label, desc in MENU_ITEMS:
        line = (
            f"{ACCENT}[{key}]{RESET} {BOLD}{label}{RESET}"
            + (f"  {DIM}{desc}{RESET}" if desc else "")
        )
        print(ACCENT + V + RESET + " " + pad_ansi(line, width - 4) + " " + ACCENT + V + RESET)
    print(box_bottom())
    print(f"{MUTED}  press a number, Q to quit{RESET}")


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
            screen_envs()
        elif key == "6":
            screen_history()
        elif key == "7":
            screen_games()
        elif key == "8":
            screen_about()
