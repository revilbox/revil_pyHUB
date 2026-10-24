"""Git helpers."""
import subprocess
from pathlib import Path


def git_pull(repo: Path) -> str:
    if not (repo / ".git").exists():
        return "Not a git repository."
    try:
        r = subprocess.run(
            ["git", "pull", "--ff-only"],
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return (r.stdout + r.stderr).strip() or "Already up to date."
    except Exception as e:
        return f"Update failed: {e}"
