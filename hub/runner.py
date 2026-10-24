"""Run python scripts with args, venv and history."""
import shlex
import subprocess
import sys
import time
from pathlib import Path

from .ui import clear, wait_key, MUTED, RESET
from . import config, history


def run_python(path: Path, args: str = "", python_bin: str = "", record: bool = True):
    cfg = config.load()
    py = python_bin or cfg.get("python_bin") or sys.executable
    active = cfg.get("active_venv") or ""
    if not python_bin and not cfg.get("python_bin") and active:
        candidate = Path(active) / "bin" / "python"
        if candidate.is_file():
            py = str(candidate)

    argv = [py, str(path)] + (shlex.split(args) if args.strip() else [])
    clear()
    print(f"{MUTED}interpreter: {py}{RESET}")
    print(f"{MUTED}running: {' '.join(argv)}{RESET}")
    print("-" * 46)

    started = time.time()
    exit_code = None
    try:
        proc = subprocess.run(argv, cwd=path.parent)
        exit_code = proc.returncode
    except KeyboardInterrupt:
        exit_code = -2
    except FileNotFoundError:
        print(f"interpreter not found: {py}")
        exit_code = -1

    duration = time.time() - started
    if record:
        history.add({
            "path": str(path),
            "args": args,
            "python": py,
            "venv": active,
            "cwd": str(path.parent),
            "exit": exit_code,
            "duration": round(duration, 2),
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        })

    print(f"\n{MUTED}exit: {exit_code}  duration: {duration:.2f}s{RESET}")
    wait_key("press any key to return")
