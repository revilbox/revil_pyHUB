"""venv discovery / creation / removal."""
import shutil
import subprocess
import sys
from pathlib import Path


def find_venvs(root: Path) -> list[Path]:
    """Look for .venv / venv in root and one level down."""
    found = []
    candidates = [root, root / ".venv", root / "venv"]
    try:
        for sub in root.iterdir():
            if sub.is_dir():
                candidates.append(sub / ".venv")
                candidates.append(sub / "venv")
    except PermissionError:
        pass
    seen = set()
    for c in candidates:
        try:
            py = c / "bin" / "python"
            if py.is_file() and c.resolve() not in seen:
                seen.add(c.resolve())
                found.append(c.resolve())
        except Exception:
            pass
    return found


def create_venv(target: Path) -> tuple[bool, str]:
    try:
        r = subprocess.run(
            [sys.executable, "-m", "venv", str(target)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if r.returncode == 0:
            return True, f"Created {target}"
        return False, (r.stderr or r.stdout).strip() or "venv creation failed"
    except Exception as e:
        return False, f"venv failed: {e}"


def remove_venv(target: Path) -> tuple[bool, str]:
    try:
        shutil.rmtree(target)
        return True, f"Removed {target}"
    except Exception as e:
        return False, f"Remove failed: {e}"


def venv_python(venv: Path) -> str:
    return str(venv / "bin" / "python")
