"""Fail when a public resume-template tree contains likely private material."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


SKIP_DIRECTORIES = {".git", "build", ".venv", "__pycache__", ".pytest_cache"}
BLOCKED_PARTS = {
    "application",
    "applications",
    "application_tracker.md",
    "info",
    "private",
    ".playwright-cli",
}
BLOCKED_EXTENSIONS = {".pdf", ".docx", ".doc", ".png", ".jpg", ".jpeg", ".heic"}
EMAIL = re.compile(r"(?<![\w.+-])([\w.+-]+@[\w.-]+\.[A-Za-z]{2,})(?![\w.-])")
PHONE = re.compile(r"(?:\+?1[\s.-]*)?\(?\d{3}\)?[\s.-]*\d{3}[\s.-]*\d{4}")
PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GitHub token": re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}\b"),
    "OpenAI-style key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "AWS access key": re.compile(r"\bAKIA[A-Z0-9]{16}\b"),
    "local macOS path": re.compile("/" + r"Users/[^/\s]+/"),
    "local Linux path": re.compile("/" + r"home/[^/\s]+/"),
}


def iter_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in SKIP_DIRECTORIES for part in relative.parts):
            continue
        yield path, relative


def scan(root: Path) -> list[str]:
    findings: list[str] = []
    for path, relative in iter_files(root):
        lowered_parts = {part.lower() for part in relative.parts}
        if lowered_parts & BLOCKED_PARTS:
            findings.append(f"blocked path: {relative}")
            continue
        lowered_name = relative.name.lower()
        if "transcript" in lowered_name or "photo" in lowered_name:
            findings.append(f"sensitive filename: {relative}")
            continue
        if relative.suffix.lower() in BLOCKED_EXTENSIONS:
            findings.append(f"binary document or image: {relative}")
            continue
        if relative.name.startswith(".env") and relative.name != ".env.example":
            findings.append(f"environment file: {relative}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            findings.append(f"unreviewed binary file: {relative}")
            continue
        for match in EMAIL.finditer(text):
            address = match.group(1).lower()
            allowed_addresses = {"git@github.com"}
            if address not in allowed_addresses and not address.endswith(
                ("@example.com", "@example.org", "@example.net")
            ):
                findings.append(f"non-example email in {relative}:{text.count(chr(10), 0, match.start()) + 1}")
        for match in PHONE.finditer(text):
            digits = re.sub(r"\D", "", match.group(0))
            national = digits[1:] if len(digits) == 11 and digits.startswith("1") else digits
            if len(national) == 10 and national[0:3] != "555" and national[3:6] != "555":
                findings.append(f"non-example phone in {relative}:{text.count(chr(10), 0, match.start()) + 1}")
        for label, pattern in PATTERNS.items():
            for match in pattern.finditer(text):
                findings.append(f"{label} in {relative}:{text.count(chr(10), 0, match.start()) + 1}")
    return sorted(set(findings))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".", type=Path)
    args = parser.parse_args()
    findings = scan(args.root.resolve())
    if findings:
        print("Privacy check failed:", file=sys.stderr)
        for finding in findings:
            print(f"- {finding}", file=sys.stderr)
        return 1
    print("Privacy check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
