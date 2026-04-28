"""Placeholder CSV row counter script for demo auditing."""

from pathlib import Path


def count_lines(path: Path) -> int:
    """Return the number of lines in a text file."""

    return len(path.read_text(encoding="utf-8").splitlines())
