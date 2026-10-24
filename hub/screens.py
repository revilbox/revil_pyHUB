"""Run, settings, update, about, envs, history screens."""
import sys
from pathlib import Path

from .ui import (
    clear, wait_key, readchar, term_width, hr,
    BOLD, DIM, RESET, CYAN, GREEN, YELLOW, RED,
)
from .runner import run_python
from .git_ops import git_pull
from .ui import REPO_ROOT
from . import config, history, envs, __version__


# ---------- run ----------

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


# ---------- settings ----------

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
        print(f"  [5] active_venv  = {cfg['active_venv'] or '(none)'}")
        hr("-")
        print(f"  {DIM}Press 1-5 to change, 9 to clear venv, B to go back.{RESET}")
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
        elif key == "5":
            clear()
            print("active_venv (full path, empty to unset):")
            v = input("> ").strip()
            cfg["active_venv"] = v
            config.save(cfg)
        elif key == "9":
            cfg["active_venv"] = ""
            config.save(cfg)


# ---------- update ----------

def screen_update():
    clear()
    print("revil_pyHUB / update from git")
    hr("-")
    print("Running: git pull --ff-only")
    print()
    print(git_pull(REPO_ROOT))
    wait_key()


# ---------- about ----------

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


# ---------- envs ----------

def screen_envs():
    cfg = config.load()
    root = Path(cfg["start_dir"]).expanduser()
    if not root.is_dir():
        root = Path.home()
    index = 0

    while True:
        found = envs.find_venvs(root)
        if not found:
            index = 0
        elif index >= len(found):
            index = len(found) - 1

        clear()
        print("revil_pyHUB / environments (venv)")
        hr("-")
        print(f"Root: {root}")
        print(f"Active: {cfg.get('active_venv') or '(none)'}")
        hr("-")
        if not found:
            print("(no venv found)")
        else:
            for i, v in enumerate(found):
                marker = ">" if i == index else " "
                tag = "*" if str(v) == cfg.get("active_venv") else " "
                print(f"{marker} {tag} {v}")
        hr("-")
        print(f"  {DIM}UP/DOWN navigate | ENTER activate | C create | D delete | B back{RESET}")

        key = readchar.readkey()
        if key in ("b", "B", "q", "Q"):
            return
        elif key == readchar.key.UP:
            index = max(0, index - 1)
        elif key == readchar.key.DOWN:
            index = min(len(found) - 1, index + 1)
        elif key in ("\r", "\n"):
            if found:
                cfg["active_venv"] = str(found[index])
                config.save(cfg)
                clear()
                print(f"Activated: {found[index]}")
                wait_key()
        elif key in ("c", "C"):
            clear()
            print("Create venv at path (empty to cancel):")
            print(f"  example: {root}/.venv")
            p = input("> ").strip()
            if p:
                target = Path(p).expanduser()
                ok, msg = envs.create_venv(target)
                clear()
                print(msg)
                if ok:
                    cfg["active_venv"] = str(target.resolve())
                    config.save(cfg)
                    print(f"Activated: {target}")
                wait_key()
        elif key in ("d", "D"):
            if found:
                target = found[index]
                clear()
                print(f"{RED}Delete venv '{target}'? y/N{RESET}")
                if readchar.readkey().lower() == "y":
                    ok, msg = envs.remove_venv(target)
                    if ok and cfg.get("active_venv") == str(target):
                        cfg["active_venv"] = ""
                        config.save(cfg)
                    clear()
                    print(msg)
                    wait_key()


# ---------- history ----------

def screen_history():
    index = 0
    while True:
        items = history.load()
        if not items:
            index = 0
        elif index >= len(items):
            index = len(items) - 1

        clear()
        print("revil_pyHUB / run history")
        hr("-")
        if not items:
            print("(empty)")
        else:
            for i, e in enumerate(items):
                marker = ">" if i == index else " "
                path = Path(e.get("path", "?")).name
                ts = e.get("ts", "?")
                code = e.get("exit", "?")
                color = GREEN if code == 0 else RED
                print(f"{marker} [{ts}] {color}{path}{RESET} exit={code} args={e.get('args','')!r}")
        hr("-")
        print(f"  {DIM}UP/DOWN navigate | ENTER rerun | C clear history | B back{RESET}")

        key = readchar.readkey()
        if key in ("b", "B", "q", "Q"):
            return
        elif key == readchar.key.UP:
            index = max(0, index - 1)
        elif key == readchar.key.DOWN:
            index = min(len(items) - 1, index + 1)
        elif key in ("\r", "\n"):
            if items:
                e = items[index]
                p = Path(e.get("path", ""))
                if p.is_file():
                    run_python(p, args=e.get("args", ""), python_bin=e.get("python", ""))
                else:
                    clear()
                    print(f"Missing file: {p}")
                    wait_key()
        elif key in ("c", "C"):
            clear()
            print(f"{YELLOW}Clear all history? y/N{RESET}")
            if readchar.readkey().lower() == "y":
                history.clear()
