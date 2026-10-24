#!/usr/bin/env python3
"""revil_pyHUB - minimal terminal hub for Termux."""
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


def clear():
    os.system("clear")


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
    print(f"\n{'-' * 40}\nFinished. Press any key to return.")
    readchar.readkey()


def list_dir(path: Path):
    items = []
    try:
        for entry in sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
            items.append(entry)
    except PermissionError:
        pass
    return items


def render(cwd: Path, items, index):
    clear()
    print("revil_pyHUB")
    print(f"Path: {cwd}")
    print("-" * 40)
    if not items:
        print("(empty)")
    for i, item in enumerate(items):
        name = item.name if item.name else str(item)
        if item.is_dir():
            name += "/"
        marker = ">" if i == index else " "
        print(f"{marker} {name}")
    print("-" * 40)
    print("UP/DOWN: navigate | ENTER: open/run | U: update | Q: quit")


def main():
    cwd = Path.home()
    index = 0
    while True:
        raw = [Path("..")] + list_dir(cwd) if cwd != cwd.parent else list_dir(cwd)
        items = raw
        if index >= len(items):
            index = max(0, len(items) - 1)

        render(cwd, items, index)
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
                print("\nPress any key to return.")
                readchar.readkey()
        elif key in ("u", "U"):
            clear()
            print("Updating from git...")
            print(git_pull())
            print("\nPress any key to return.")
            readchar.readkey()
        elif key in ("q", "Q"):
            clear()
            print("Bye.")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBye.")
