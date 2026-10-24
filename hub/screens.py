"""Run, settings, update, about screens."""
import subprocess
import sys
from pathlib import Path

from .ui import (
    clear, wait_key, readchar, term_width, hr,
    BOLD, DIM, RESET, CYAN,
)
from .runner import run_python
from .git_ops import git_pull
from .ui import REPO_ROOT
from . import config, __version__


def screen_run():
    cfg = config.load()
    clear()
    print("revil_pyHUB / run python script")
    hr("-")
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
    run_python(p, args=args, python_bin=cfg["python_bin"])


def screen_settings():
    cfg = config.load()
    while True:
        clear()
        print("revil_pyHUB / settings")
        hr("-")
        print(f"  [1] start_dir    = {cfg['start_dir']}")
        print(f"  [2] auto_update  = {cfg['auto_update']}")
        print(f"  [3] editor       = {cfg['editor']}")
        print(f"  [4] python_bin   = {cfg['python_bin'] or '(auto: system python)'}")
        hr("-")
        print(f"  {DIM}Press 1-4 to change, B to go back.{RESET}")
        print(f"  {DIM}Config file: {config.CONFIG_FILE}{RESET}")

        key = readchar.readkey()
        if key in ("b", "B", "q", "Q"):
            config.save(cfg)
            return
        elif key == "1":
            clear()
            print("start_dir (expanded with ~):")
            v = input("> ").strip()
            if v:
                cfg["start_dir"] = v
                config.save(cfg)
        elif key == "2":
            cfg["auto_update"] = not cfg["auto_update"]
            config.save(cfg)
        elif key == "3":
            clear()
            print("editor (e.g. nano, vim, micro):")
            v = input("> ").strip()
            if v:
                cfg["editor"] = v
                config.save(cfg)
        elif key == "4":
            clear()
            print("python_bin (full path, empty for auto):")
            v = input("> ").strip()
            cfg["python_bin"] = v
            config.save(cfg)


def screen_update():
    clear()
    print("revil_pyHUB / update from git")
    hr("-")
    print("Running: git pull --ff-only")
    print()
    print(git_pull(REPO_ROOT))
    wait_key()


def screen_about():
    clear()
    print("revil_pyHUB / about")
    hr("-")
    print("revil_pyHUB - terminal hub for Python on Termux.")
    print("Designed for beginners and power users alike.")
    print()
    print(f"Version:    {__version__}")
    print(f"Repo root:  {REPO_ROOT}")
    print(f"Python:     {sys.version.split()[0]}")
    print(f"Executable: {sys.executable}")
    wait_key()
