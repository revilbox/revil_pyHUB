"""Run, settings, update, about, envs, history - strict."""
import sys
from pathlib import Path

from .ui import (
    clear, wait_key, readchar, term_width, print_header,
    box_top, box_line, box_sep, box_bottom, fit,
    ACCENT, TEXT, MUTED, RESET, BOLD,
    SUCCESS, ERROR, WARN,
)
from .runner import run_python
from .git_ops import git_pull
from .ui import REPO_ROOT
from . import config, history, envs, __version__


def _screen(title: str, lines: list[str], hint: str = ""):
    clear()
    width = term_width()
    print_header(title)
    print(box_top(width=width))
    for ln in lines:
        print(box_line(ln, width))
    if hint:
        print(box_sep(width))
        print(box_line(f"{MUTED}{hint}{RESET}", width))
    print(box_bottom(width))


# ---------- run ----------

def screen_run():
    cfg = config.load()
    clear()
    print_header("RUN PYTHON SCRIPT")
    print(box_top())
    print(box_line(f"{MUTED}path to .py (empty to cancel){RESET}"))
    print(box_bottom())
    path_str = input(f"{ACCENT}> {RESET}").strip()
    if not path_str:
        return
    p = Path(path_str).expanduser()
    if not p.is_file() or p.suffix != ".py":
        print(f"{ERROR}not a valid .py: {p}{RESET}")
        wait_key()
        return
    print(f"{MUTED}args (empty for none){RESET}")
    args = input(f"{ACCENT}> {RESET}").strip()
    run_python(p, args=args, python_bin=cfg["python_bin"])


# ---------- settings ----------

def screen_settings():
    cfg = config.load()
    while True:
        lines = [
            f"{ACCENT}[1]{RESET} start_dir    {MUTED}={RESET} {cfg['start_dir']}",
            f"{ACCENT}[2]{RESET} auto_update  {MUTED}={RESET} {cfg['auto_update']}",
            f"{ACCENT}[3]{RESET} editor       {MUTED}={RESET} {cfg['editor']}",
            f"{ACCENT}[4]{RESET} python_bin   {MUTED}={RESET} {cfg['python_bin'] or '(auto)'}",
            f"{ACCENT}[5]{RESET} active_venv  {MUTED}={RESET} {cfg['active_venv'] or '(none)'}",
            f"{MUTED}[9]{RESET} {MUTED}clear active venv{RESET}",
        ]
        _screen("SETTINGS", lines, hint="1-5 change  9 clear venv  b back  q quit")
        key = readchar.readkey()
        if key in ("b", "B", "q", "Q"):
            config.save(cfg); return
        elif key == "1":
            clear(); print("start_dir:")
            v = input("> ").strip()
            if v: cfg["start_dir"] = v; config.save(cfg)
        elif key == "2":
            cfg["auto_update"] = not cfg["auto_update"]; config.save(cfg)
        elif key == "3":
            clear(); print("editor:")
            v = input("> ").strip()
            if v: cfg["editor"] = v; config.save(cfg)
        elif key == "4":
            clear(); print("python_bin (empty for auto):")
            cfg["python_bin"] = input("> ").strip(); config.save(cfg)
        elif key == "5":
            clear(); print("active_venv (empty to unset):")
            cfg["active_venv"] = input("> ").strip(); config.save(cfg)
        elif key == "9":
            cfg["active_venv"] = ""; config.save(cfg)


# ---------- update ----------

def screen_update():
    out = git_pull(REPO_ROOT).splitlines() or ["(no output)"]
    _screen("UPDATE FROM GIT", [f"{MUTED}git pull --ff-only{RESET}", ""] + out)
    wait_key()


# ---------- about ----------

def screen_about():
    lines = [
        f"{BOLD}revil_pyHUB{RESET} {MUTED}terminal hub for python on termux{RESET}",
        "",
        f"version     {MUTED}={RESET} {__version__}",
        f"repo root   {MUTED}={RESET} {REPO_ROOT}",
        f"python      {MUTED}={RESET} {sys.version.split()[0]}",
        f"executable  {MUTED}={RESET} {sys.executable}",
    ]
    _screen("ABOUT", lines)
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

        lines = [
            f"{MUTED}root:{RESET} {root}",
            f"{MUTED}active:{RESET} {cfg.get('active_venv') or '(none)'}",
        ]
        if not found:
            lines.append(f"{MUTED}(no venv found){RESET}")
        else:
            for i, v in enumerate(found):
                mark = f"{ACCENT}>{RESET}" if i == index else " "
                star = f"{SUCCESS}*{RESET}" if str(v) == cfg.get("active_venv") else " "
                lines.append(f"{mark} {star} {v}")
        _screen("ENVIRONMENTS", lines, hint="ENTER activate  c create  d delete  b back")

        key = readchar.readkey()
        if key in ("b", "B", "q", "Q"):
            return
        elif key == readchar.key.UP:
            index = max(0, index - 1)
        elif key == readchar.key.DOWN:
            index = min(len(found) - 1, index + 1)
        elif key in ("\r", "\n"):
            if found:
                cfg["active_venv"] = str(found[index]); config.save(cfg)
                clear(); print(f"{SUCCESS}activated: {found[index]}{RESET}"); wait_key()
        elif key in ("c", "C"):
            clear()
            print(f"create venv at (example {root}/.venv):")
            p = input("> ").strip()
            if p:
                target = Path(p).expanduser()
                ok, msg = envs.create_venv(target)
                clear()
                print((SUCCESS if ok else ERROR) + msg + RESET)
                if ok:
                    cfg["active_venv"] = str(target.resolve()); config.save(cfg)
                wait_key()
        elif key in ("d", "D"):
            if found:
                target = found[index]
                clear()
                print(f"{ERROR}delete venv '{target}'? y/N{RESET}")
                if readchar.readkey().lower() == "y":
                    ok, msg = envs.remove_venv(target)
                    if ok and cfg.get("active_venv") == str(target):
                        cfg["active_venv"] = ""; config.save(cfg)
                    clear(); print((SUCCESS if ok else ERROR) + msg + RESET); wait_key()


# ---------- history ----------

def screen_history():
    index = 0
    while True:
        items = history.load()
        if not items:
            index = 0
        elif index >= len(items):
            index = len(items) - 1

        lines = []
        if not items:
            lines.append(f"{MUTED}(empty){RESET}")
        else:
            for i, e in enumerate(items):
                mark = f"{ACCENT}>{RESET}" if i == index else " "
                path = Path(e.get("path", "?")).name
                ts = e.get("ts", "?")
                code = e.get("exit", "?")
                color = SUCCESS if code == 0 else ERROR
                lines.append(f"{mark} {MUTED}{ts}{RESET}  {color}{path}{RESET}  {MUTED}exit={code}{RESET}")
        _screen("RUN HISTORY", lines, hint="ENTER rerun  c clear  b back")

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
                    clear(); print(f"{ERROR}missing file: {p}{RESET}"); wait_key()
        elif key in ("c", "C"):
            clear()
            print(f"{WARN}clear all history? y/N{RESET}")
            if readchar.readkey().lower() == "y":
                history.clear()
