"""Verify that expected PDFs and Word documents exist and are one page."""

from __future__ import annotations

import re
import subprocess
import sys
import zipfile
from pathlib import Path


def pdf_pages(path: Path) -> int:
    result = subprocess.run(["pdfinfo", str(path)], check=True, capture_output=True, text=True)
    match = re.search(r"^Pages:\s+(\d+)$", result.stdout, re.MULTILINE)
    if not match:
        raise RuntimeError(f"Could not read page count from {path}")
    return int(match.group(1))


def check_docx(path: Path) -> None:
    with zipfile.ZipFile(path) as archive:
        required = {"[Content_Types].xml", "word/document.xml", "docProps/core.xml"}
        missing = required.difference(archive.namelist())
        if missing:
            raise RuntimeError(f"{path} is missing {sorted(missing)}")


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "build")
    pdfs = [
        root / "latex" / "resume_full_time.pdf",
        root / "latex" / "resume_coop.pdf",
        root / "latex" / "resume_cn.pdf",
        root / "word-pdf" / "resume_full_time.pdf",
        root / "word-pdf" / "resume_coop.pdf",
    ]
    docx_files = [root / "docx" / "resume_full_time.docx", root / "docx" / "resume_coop.docx"]
    for path in pdfs + docx_files:
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError(f"Missing output: {path}")
    for path in pdfs:
        pages = pdf_pages(path)
        if pages != 1:
            raise RuntimeError(f"Expected one page, found {pages}: {path}")
        print(f"one page: {path}")
    for path in docx_files:
        check_docx(path)
        print(f"valid package: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
