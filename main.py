#!/usr/bin/env python3
"""revil_pyHUB - terminal hub for Python on Termux. Single-file build."""
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

try:
    import readchar
except ImportError:
    print("Missing dependency. Run: pip install readchar")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent
VERSION = "0.2.0"

CONFIG_DIR = Path.home() / ".config" / "revil_pyhub"
CONFIG_FILE = CONFIG_DIR / "config.json"
DEFAULTS = {
    "start_dir": str(Path.home()),
    "auto_update": False,
    "editor": "nano",
    "python_bin": "",
}

LOGO = r"""
 ____            _ _   ____       _   _ _   _ ____
|  _ \ _____   _(_) | |  _ \_   _| | | | | | | __ )
| |_) / _ \ \ / / | | | |_) | | | | |_| | | |  _ \
|  _ <  __/\ V /| | | |  __/| |_| |  _  | |_| |_) |
|_| \_\___| \_/ |_|_| |_|    \__, |_| |_|\___/|____/
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


# ---------- common ----------

def clear():
    os.system("clear")


def wait_key(msg="Press any key to return."):
    print(f"\n{msg}")
    readchar.readkey()


def print_logo():
    print(LOGO)
    print("  revil_pyHUB")
    print("  " + "-" * 46)


# ---------- config ----------

def config_load() -> dict:
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text())
            merged = dict(DEFAULTS)
            merged.update({k: v for k, v in data.items() if k in DEFAULTS})
            return merged
        except Exception:
            pass
    return dict(DEFAULTS)


def config_save(cfg: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))


# ---------- git ----------

def git_pull() -> str:
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


# ---------- runner ----------

def run_python(path: Path, args: str = "", python_bin: str = ""):
    clear()
    py = python_bin or sys.executable
    argv = [py, str(path)] + (shlex.split(args) if args.strip() else [])
    print(f"Running: {' '.join(argv)}")
    print("-" * 46)
    try:
        subprocess.run(argv, cwd=path.parent)
    except KeyboardInterrupt:
        pass
    except FileNotFoundError:
        print(f"Interpreter not found: {py}")
    wait_key("Finished. Press any key to return.")


# ---------- screens ----------

def screen_explorer():
    cfg = config_load()
    cwd = Path(cfg["start_dir"]).expanduser()
    if not cwd.is_dir():
        cwd = Path.home()
    index = 0

    def list_dir(path: Path):
        items = []
        try:
            for entry in sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
                items.append(entry)
        except PermissionError:
            pass
        return items

    def preview(path: Path) -> str:
        try:
            if path.is_dir():
                return f"<directory>\n{path}"
            size = path.stat().st_size
            if path.suffix == ".py":
                return path.read_text(errors="replace")[:3000]
            if size > 200_000:
                return f"<binary or large file> {size} bytes"
            return path.read_text(errors="replace")[:3000]
        except Exception as e:
            return f"<cannot read: {e}>"

    while True:
        items = ([Path("..")] + list_dir(cwd)) if cwd != cwd.parent else list_dir(cwd)
        if not items:
            index = 0
        elif index >= len(items):
            index = len(items) - 1

        clear()
        print("revil_pyHUB / file explorer")
        print(f"Path: {cwd}")
        print("=" * 70)
        prev = preview(items[index]) if items else ""
        prev_lines = prev.splitlines()[:20]
        width_left = 34
        for i in range(max(len(items), len(prev_lines))):
            left = ""
            if i < len(items):
                item = items[i]
                name = item.name or str(item)
                if item.is_dir():
                    name += "/"
                marker = ">" if i == index else " "
                left = f"{marker} {name}"
                if len(left) > width_left:
                    left = left[: width_left - 1] + "~"
            right = prev_lines[i] if i < len(prev_lines) else ""
            print(left.ljust(width_left) + " | " + right)
        print("=" * 70)
        print("UP/DOWN navigate | ENTER open/run | E edit | B back | U update | Q quit")

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
                run_python(target, python_bin=cfg["python_bin"])
            else:
                clear()
                print(preview(target))
                wait_key()
        elif key in ("e", "E"):
            if items and items[index].is_file():
                target = items[index]
                editor = cfg["editor"]
                clear()
                print(f"Opening {target} in {editor}...")
                try:
                    subprocess.run([editor, str(target)])
                except FileNotFoundError:
                    print(f"Editor not found: {editor}")
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


def screen_run():
    cfg = config_load()
    clear()
    print("revil_pyHUB / run python script")
    print("-" * 46)
    print("Path to .py file (empty to cancel):")
    path_str = input("> ").strip()
    if not path_str:
        return
    p = Path(path_str).expanduser()
    if not p.is_file() or p.suffix != ".py":
        print(f"Not a valid .py file: {p}")
        wait_key()
        return
    print("Arguments (empty for none):")
    args = input("> ").strip()
    py = cfg["python_bin"]
    if py:
        print(f"Using python_bin: {py}")
    run_python(p, args=args, python_bin=py)


def screen_settings():
    cfg = config_load()
    while True:
        clear()
        print("revil_pyHUB / settings")
        print("-" * 46)
        print(f"  [1] start_dir    = {cfg['start_dir']}")
        print(f"  [2] auto_update  = {cfg['auto_update']}")
        print(f"  [3] editor       = {cfg['editor']}")
        print(f"  [4] python_bin   = {cfg['python_bin'] or '(auto: system python)'}")
        print("-" * 46)
        print("  Press 1-4 to change, B to go back.")
        print(f"  Config file: {CONFIG_FILE}")

        key = readchar.readkey()
        if key in ("b", "B", "q", "Q"):
            config_save(cfg)
            return
        elif key == "1":
            clear()
            print("start_dir (expanded with ~):")
            v = input("> ").strip()
            if v:
                cfg["start_dir"] = v
                config_save(cfg)
        elif key == "2":
            cfg["auto_update"] = not cfg["auto_update"]
            config_save(cfg)
        elif key == "3":
            clear()
            print("editor (e.g. nano, vim, micro):")
            v = input("> ").strip()
            if v:
                cfg["editor"] = v
                config_save(cfg)
        elif key == "4":
            clear()
            print("python_bin (full path, empty for auto):")
            v = input("> ").strip()
            cfg["python_bin"] = v
            config_save(cfg)


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
    print()
    print(f"Version:    {VERSION}")
    print(f"Repo root:  {REPO_ROOT}")
    print(f"Python:     {sys.version.split()[0]}")
    print(f"Executable: {sys.executable}")
    wait_key()


# ---------- main menu ----------

def render_menu():
    clear()
    print_logo()
    print("  main menu")
    print("  " + "-" * 46)
    for key, label in MENU_ITEMS:
        print(f"  [{key}] {label}")
    print("  " + "-" * 46)
    print("  Press a number, Q to quit.")


def main_menu() -> str:
    while True:
        render_menu()
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
