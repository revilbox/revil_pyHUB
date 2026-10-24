#!/usr/bin/env python3
"""revil_pyHUB - terminal hub for Termux."""
import os
import subprocess
import sys
from pathlib import Path

try:
    import readchar
except ImportError:
    print("Missing dependency. Run: pip install readchar")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent

LOGO = r"""
  ____            _ _    ____       _   _ _   _ ____
 |  _ \ _____   _(_) |  |  _ \_   _| | | | | | | __ )
 | |_) / _ \ \ / / | |  | |_) | | | | |_| | | |  _ \
 |  _ <  __/\ V /| | |  |  __/| |_| |  _  | |_| |_) |
 |_| \_\___| \_/ |_|_|  |_|    \__, |_| |_|\___/|____/
                               |___/
"""

MENU_ITEMS = [
    ("1", "File explorer"),
    ("2", "Run Python script"),
    ("3", "Settings"),
    ("4", "Update from git"),
    ("5", "About"),
    ("0", "Exit"),
]


def clear():
    os.system("clear")


def wait_key(msg="Press any key to return."):
    print(f"\n{msg}")
    readchar.readkey()


def git_pull():
    if not (REPO_ROOT / ".git").exists():
        return "Not a git repository."
    try:
        r = subprocess.run(
            ["git", "pull", "--ff-only"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return (r.stdout + r.stderr).strip() or "Already up to date."
    except Exception as e:
        return f"Update failed: {e}"


def run_python(path: Path):
    clear()
    print(f"Running: {path}\n{'-' * 40}")
    try:
        subprocess.run([sys.executable, str(path)], cwd=path.parent)
    except KeyboardInterrupt:
        pass
    wait_key("Finished. Press any key to return.")


def list_dir(path: Path):
    items = []
    try:
        for entry in sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
            items.append(entry)
    except PermissionError:
        pass
    return items


# ---------- Main menu ----------

def screen_menu():
    clear()
    print(LOGO)
    print("  revil_pyHUB / main menu")
    print("  " + "-" * 46)
    for key, label in MENU_ITEMS:
        print(f"  [{key}] {label}")
    print("  " + "-" * 46)
    print("  Press a number to select, Q to quit.")


def main_menu():
    while True:
        screen_menu()
        key = readchar.readkey()
        if key in ("q", "Q", "0"):
            return "exit"
        elif key == "1":
            screen_explorer()
        elif key == "2":
            screen_run_script()
        elif key == "3":
            screen_settings()
        elif key == "4":
            screen_update()
        elif key == "5":
            screen_about()


# ---------- Explorer ----------

def render_explorer(cwd: Path, items, index):
    clear()
    print("revil_pyHUB / file explorer")
    print(f"Path: {cwd}")
    print("-" * 46)
    if not items:
        print("(empty)")
    for i, item in enumerate(items):
        name = item.name if item.name else str(item)
        if item.is_dir():
            name += "/"
        marker = ">" if i == index else " "
        print(f"{marker} {name}")
    print("-" * 46)
    print("UP/DOWN: navigate | ENTER: open/run | B: back to menu | U: update | Q: quit")


def screen_explorer():
    cwd = Path.home()
    index = 0
    while True:
        raw = [Path("..")] + list_dir(cwd) if cwd != cwd.parent else list_dir(cwd)
        items = raw
        if not items:
            index = 0
        elif index >= len(items):
            index = len(items) - 1

        render_explorer(cwd, items, index)
        key = readchar.readkey()

        if key == readchar.key.UP:
            index = max(0, index - 1)
        elif key == readchar.key.DOWN:
            index = min(len(items) - 1, index + 1)
        elif key in ("\r", "\n"):
            if not items:
                continue
            target = items[index]
            if target.name == "..":
                cwd = cwd.parent
                index = 0
            elif target.is_dir():
                cwd = target
                index = 0
            elif target.suffix == ".py":
                run_python(target)
            else:
                clear()
                print(f"{target}")
                try:
                    print(target.read_text()[:2000])
                except Exception as e:
                    print(f"Cannot read: {e}")
                wait_key()
        elif key in ("b", "B"):
            return
        elif key in ("u", "U"):
            clear()
            print("Updating from git...")
            print(git_pull())
            wait_key()
        elif key in ("q", "Q"):
            return


# ---------- Other screens (placeholders for now) ----------

def screen_run_script():
    clear()
    print("revil_pyHUB / run python script")
    print("-" * 46)
    print("Enter path to .py file (or leave empty to cancel):")
    print()
    path_str = input("> ").strip()
    if not path_str:
        return
    p = Path(path_str).expanduser()
    if not p.is_file():
        print(f"Not a file: {p}")
        wait_key()
        return
    if p.suffix != ".py":
        print("Not a .py file.")
        wait_key()
        return
    run_python(p)


def screen_settings():
    clear()
    print("revil_pyHUB / settings")
    print("-" * 46)
    print("(placeholder - settings will be added later)")
    wait_key()


def screen_update():
    clear()
    print("revil_pyHUB / update from git")
    print("-" * 46)
    print("Running: git pull --ff-only")
    print()
    print(git_pull())
    wait_key()


def screen_about():
    clear()
    print("revil_pyHUB / about")
    print("-" * 46)
    print("revil_pyHUB - terminal hub for Python on Termux.")
    print("Designed for beginners and power users alike.")
    print("Repo: (add your github link here later)")
    print(f"Repo root: {REPO_ROOT}")
    print(f"Python: {sys.version.split()[0]}")
    wait_key()


# ---------- Entry ----------

def main():
    try:
        result = main_menu()
    except KeyboardInterrupt:
        result = "exit"
    clear()
    if result == "exit":
        print("Bye.")


if __name__ == "__main__":
    main()
