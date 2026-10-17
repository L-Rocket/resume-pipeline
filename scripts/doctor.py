"""Check that the local toolchain can build and verify the resume PDFs."""

from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_COMMANDS = {
    "git": ["git", "--version"],
    "make": ["make", "--version"],
    "tectonic": ["tectonic", "--version"],
    "pdfinfo": ["pdfinfo", "-v"],
}


def first_line(command: list[str]) -> str:
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    output = (result.stdout or result.stderr).strip().splitlines()
    return output[0] if output else "version unavailable"


def main() -> int:
    print(f"platform: {platform.system()} {platform.machine()}")
    print(f"python: {platform.python_version()}")
    if sys.version_info < (3, 9):
        print("error: Python 3.9 or newer is required", file=sys.stderr)
        return 1

    missing: list[str] = []
    for name, version_command in REQUIRED_COMMANDS.items():
        executable = shutil.which(name)
        if not executable:
            missing.append(name)
            print(f"missing: {name}")
            continue
        print(f"{name}: {first_line(version_command)}")

    if not (ROOT / ".git").is_dir():
        print("error: this directory is not a Git checkout", file=sys.stderr)
        return 1

    if missing:
        print("error: install the missing commands and rerun `make doctor`", file=sys.stderr)
        return 1

    print("environment doctor passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
