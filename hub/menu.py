"""Main menu - strict, flat, monochrome."""
from .ui import (
    clear, readchar, term_width, print_header,
    box_top, box_line, box_bottom,
    ACCENT, TEXT, MUTED, RESET, BOLD,
)
from .explorer import screen_explorer
from .screens import (
    screen_run, screen_settings, screen_update, screen_about,
    screen_envs, screen_history,
)
from .games import screen_games

MENU_ITEMS = [
    ("1", "file explorer"),
    ("2", "run python script"),
    ("3", "settings"),
    ("4", "update from git"),
    ("5", "environments"),
    ("6", "run history"),
    ("7", "games"),
    ("8", "about"),
    ("0", "exit"),
]


def render():
    clear()
    width = term_width()
    print_header()
    print(box_top(width=width))
    for key, label in MENU_ITEMS:
        line = f"{MUTED}[{key}]{RESET}  {TEXT}{label}{RESET}"
        print(box_line(line, width))
    print(box_bottom(width))
    print(f"{MUTED}press 0-8, q to quit{RESET}")


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
