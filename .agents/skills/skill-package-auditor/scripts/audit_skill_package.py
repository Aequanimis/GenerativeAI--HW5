"""Static auditor for reusable AI skill package repositories.

This CLI inspects repository files only. It never imports or executes code from
the audited repository, including scripts it discovers during the audit.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PASS = "PASS"
WARN = "WARN"
FAIL = "FAIL"

SKILL_SEARCH_DIRS = (Path(".agents") / "skills", Path(".claude") / "skills")
ACTIVATION_PHRASES = ("use when", "use this skill", "when the user")
SKILL_FOLDER_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
URL_RE = re.compile(r"https?://\S+")


@dataclass(frozen=True)
class CheckResult:
    """One auditable finding in a repository."""

    status: str
    check: str
    target: str
    details: str
    suggestion: str = ""

    def to_dict(self) -> dict[str, str]:
        """Convert the finding to a JSON-serializable dictionary."""

        return {
            "status": self.status,
            "check": self.check,
            "target": self.target,
            "details": self.details,
            "suggestion": self.suggestion,
        }


@dataclass(frozen=True)
class SkillFolder:
    """A discovered skill folder and its repository-relative path."""

    name: str
    path: Path
    relative_path: str

    def to_dict(self) -> dict[str, str]:
        """Convert the skill folder to a JSON-serializable dictionary."""

        return {"name": self.name, "path": self.relative_path}


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description="Audit a local repository for reusable AI skill structure."
    )
    parser.add_argument("path", help="Path to the local repository to audit.")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output a machine-readable JSON report instead of Markdown.",
    )
    return parser.parse_args(argv)


def read_text(path: Path) -> str:
    """Read text with a forgiving encoding strategy for repository files."""

    return path.read_text(encoding="utf-8", errors="replace")


def relative_to_root(path: Path, root: Path) -> str:
    """Return a stable POSIX-style path relative to the audited root."""

    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def discover_skill_folders(root: Path) -> list[SkillFolder]:
    """Find skill folders under the supported reusable-skill directories."""

    skill_folders: list[SkillFolder] = []
    for search_dir in SKILL_SEARCH_DIRS:
        absolute_search_dir = root / search_dir
        if not absolute_search_dir.is_dir():
            continue

        for child in sorted(absolute_search_dir.iterdir(), key=lambda item: item.name):
            if child.is_dir():
                skill_folders.append(
                    SkillFolder(
                        name=child.name,
                        path=child,
                        relative_path=relative_to_root(child, root),
                    )
                )
    return skill_folders


def extract_frontmatter(content: str) -> tuple[dict[str, str], bool]:
    """Extract simple YAML-style frontmatter fields from SKILL.md content.

    The parser intentionally supports only straightforward ``key: value`` lines,
    which is enough for this assignment audit and avoids adding dependencies.
    """

    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, False

    closing_index: int | None = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            closing_index = index
            break

    if closing_index is None:
        return {}, False

    fields: dict[str, str] = {}
    for line in lines[1:closing_index]:
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip("\"'")

    return fields, True


def has_activation_phrase(description: str) -> bool:
    """Return whether the description contains an expected activation phrase."""

    normalized = description.casefold()
    return any(phrase in normalized for phrase in ACTIVATION_PHRASES)


def audit_skill_folder(skill: SkillFolder) -> list[CheckResult]:
    """Audit one discovered skill folder."""

    results: list[CheckResult] = []
    target = skill.relative_path

    if SKILL_FOLDER_RE.fullmatch(skill.name):
        results.append(
            CheckResult(PASS, "Skill folder name", target, "Folder name is lowercase and hyphenated.")
        )
    else:
        results.append(
            CheckResult(
                FAIL,
                "Skill folder name",
                target,
                "Folder name is not lowercase hyphenated form.",
                "Rename the folder using lowercase words separated by hyphens, e.g. skill-package-auditor.",
            )
        )

    skill_md = skill.path / "SKILL.md"
    frontmatter: dict[str, str] = {}
    has_frontmatter = False

    if skill_md.is_file():
        results.append(CheckResult(PASS, "SKILL.md exists", target, "SKILL.md was found."))
        content = read_text(skill_md)
        frontmatter, has_frontmatter = extract_frontmatter(content)
    else:
        results.append(
            CheckResult(
                FAIL,
                "SKILL.md exists",
                target,
                "SKILL.md was not found.",
                "Create SKILL.md at the root of the skill folder.",
            )
        )

    if has_frontmatter:
        results.append(
            CheckResult(
                PASS,
                "SKILL.md frontmatter",
                target,
                "YAML-style frontmatter bounded by --- was found.",
            )
        )
    else:
        results.append(
            CheckResult(
                FAIL,
                "SKILL.md frontmatter",
                target,
                "YAML-style frontmatter bounded by --- was not found.",
                "Start SKILL.md with --- frontmatter containing name and description.",
            )
        )

    name = frontmatter.get("name", "")
    if name:
        results.append(
            CheckResult(PASS, "Frontmatter name", target, f"name is set to {name!r}.")
        )
    else:
        results.append(
            CheckResult(
                FAIL,
                "Frontmatter name",
                target,
                "name: is missing from frontmatter.",
                "Add name: with the exact skill folder name.",
            )
        )

    description = frontmatter.get("description", "")
    if description:
        results.append(
            CheckResult(PASS, "Frontmatter description", target, "description is present.")
        )
    else:
        results.append(
            CheckResult(
                FAIL,
                "Frontmatter description",
                target,
                "description: is missing from frontmatter.",
                "Add a specific description that explains when the skill should be used.",
            )
        )

    if name and name == skill.name:
        results.append(
            CheckResult(PASS, "Name matches folder", target, "Frontmatter name matches folder name.")
        )
    else:
        results.append(
            CheckResult(
                FAIL,
                "Name matches folder",
                target,
                f"Frontmatter name {name!r} does not match folder name {skill.name!r}.",
                "Set frontmatter name to the exact folder name.",
            )
        )

    if len(description) >= 60:
        results.append(
            CheckResult(
                PASS,
                "Description length",
                target,
                f"description is {len(description)} characters.",
            )
        )
    else:
        results.append(
            CheckResult(
                FAIL,
                "Description length",
                target,
                f"description is {len(description)} characters; expected at least 60.",
                "Write a more specific description of at least 60 characters.",
            )
        )

    if description and has_activation_phrase(description):
        results.append(
            CheckResult(
                PASS,
                "Description activation phrase",
                target,
                "description includes an expected activation phrase.",
            )
        )
    else:
        results.append(
            CheckResult(
                FAIL,
                "Description activation phrase",
                target,
                "description does not include an activation phrase.",
                'Include a phrase such as "Use when", "Use this skill", or "when the user".',
            )
        )

    scripts_dir = skill.path / "scripts"
    if scripts_dir.is_dir():
        results.append(CheckResult(PASS, "scripts/ exists", target, "scripts/ directory was found."))
        python_scripts = sorted(
            item.name for item in scripts_dir.iterdir() if item.is_file() and item.suffix == ".py"
        )
        if python_scripts:
            results.append(
                CheckResult(
                    PASS,
                    "Python script exists",
                    target,
                    "Found Python script(s): " + ", ".join(python_scripts),
                )
            )
        else:
            results.append(
                CheckResult(
                    FAIL,
                    "Python script exists",
                    target,
                    "scripts/ does not contain any .py files.",
                    "Add at least one Python script under scripts/.",
                )
            )
    else:
        results.append(
            CheckResult(
                FAIL,
                "scripts/ exists",
                target,
                "scripts/ directory was not found.",
                "Create scripts/ inside the skill folder.",
            )
        )
        results.append(
            CheckResult(
                FAIL,
                "Python script exists",
                target,
                "Cannot find Python scripts because scripts/ is missing.",
                "Add scripts/ with at least one .py file.",
            )
        )

    return results


def audit_readme(root: Path) -> list[CheckResult]:
    """Audit the repository root README.md for video evidence."""

    target = "README.md"
    readme = root / "README.md"
    if not readme.is_file():
        return [
            CheckResult(
                FAIL,
                "Root README.md exists",
                target,
                "Root README.md was not found.",
                "Create README.md at the repository root.",
            ),
            CheckResult(
                FAIL,
                "README mentions video",
                target,
                "Cannot check video wording because README.md is missing.",
                "Add a video section to README.md.",
            ),
            CheckResult(
                FAIL,
                "README includes URL",
                target,
                "Cannot check URL because README.md is missing.",
                "Add a video URL beginning with http:// or https://.",
            ),
        ]

    content = read_text(readme)
    results = [
        CheckResult(PASS, "Root README.md exists", target, "Root README.md was found.")
    ]

    if "video" in content.casefold():
        results.append(
            CheckResult(PASS, "README mentions video", target, 'README.md includes the word "video".')
        )
    else:
        results.append(
            CheckResult(
                FAIL,
                "README mentions video",
                target,
                'README.md does not include the word "video".',
                "Add a short demo video section.",
            )
        )

    if URL_RE.search(content):
        results.append(
            CheckResult(PASS, "README includes URL", target, "README.md includes an http(s) URL.")
        )
    else:
        results.append(
            CheckResult(
                FAIL,
                "README includes URL",
                target,
                "README.md does not include a URL beginning with http:// or https://.",
                "Add the demo video link or another relevant project URL.",
            )
        )

    return results


def audit_repository(root: Path) -> dict[str, Any]:
    """Audit a repository path and return a structured report."""

    resolved_root = root.resolve()
    skill_folders = discover_skill_folders(resolved_root)
    results: list[CheckResult] = []

    if skill_folders:
        results.append(
            CheckResult(
                PASS,
                "Skill folder discovery",
                ".agents/skills or .claude/skills",
                f"Detected {len(skill_folders)} skill folder(s).",
            )
        )
    else:
        results.append(
            CheckResult(
                FAIL,
                "Skill folder discovery",
                ".agents/skills or .claude/skills",
                "No skill folders were found.",
                "Create at least one skill folder under .agents/skills/ or .claude/skills/.",
            )
        )

    for skill in skill_folders:
        results.extend(audit_skill_folder(skill))

    results.extend(audit_readme(resolved_root))
    counts = count_statuses(results)

    return {
        "audited_path": str(resolved_root),
        "summary": counts,
        "skill_folders": [skill.to_dict() for skill in skill_folders],
        "checks": [result.to_dict() for result in results],
        "suggested_fixes": suggested_fixes(results),
    }


def count_statuses(results: list[CheckResult]) -> dict[str, int]:
    """Count PASS, WARN, and FAIL statuses."""

    return {
        PASS: sum(result.status == PASS for result in results),
        WARN: sum(result.status == WARN for result in results),
        FAIL: sum(result.status == FAIL for result in results),
    }


def suggested_fixes(results: list[CheckResult]) -> list[str]:
    """Collect unique suggestions for failed or warning checks."""

    fixes: list[str] = []
    seen: set[str] = set()
    for result in results:
        if result.status == PASS or not result.suggestion or result.suggestion in seen:
            continue
        seen.add(result.suggestion)
        fixes.append(result.suggestion)
    return fixes


def markdown_table_row(values: list[str]) -> str:
    """Format a Markdown table row with pipe escaping."""

    escaped = [value.replace("|", "\\|").replace("\n", " ") for value in values]
    return "| " + " | ".join(escaped) + " |"


def render_markdown(report: dict[str, Any]) -> str:
    """Render the structured report as Markdown."""

    lines = [
        "# Skill Package Audit Report",
        "",
        f"**Audited path:** `{report['audited_path']}`",
        "",
        "## Summary",
        "",
        markdown_table_row(["PASS", "WARN", "FAIL"]),
        markdown_table_row(["---:", "---:", "---:"]),
        markdown_table_row(
            [
                str(report["summary"][PASS]),
                str(report["summary"][WARN]),
                str(report["summary"][FAIL]),
            ]
        ),
        "",
        "## Checklist",
        "",
        markdown_table_row(["Status", "Check", "Target", "Details"]),
        markdown_table_row(["---", "---", "---", "---"]),
    ]

    for check in report["checks"]:
        lines.append(
            markdown_table_row(
                [check["status"], check["check"], check["target"], check["details"]]
            )
        )

    lines.extend(["", "## Detected Skill Folders", ""])
    if report["skill_folders"]:
        for skill in report["skill_folders"]:
            lines.append(f"- `{skill['path']}`")
    else:
        lines.append("- None detected.")

    lines.extend(["", "## Suggested Fixes", ""])
    if report["suggested_fixes"]:
        for fix in report["suggested_fixes"]:
            lines.append(f"- {fix}")
    else:
        lines.append("- No fixes needed.")

    return "\n".join(lines)


def render_json(report: dict[str, Any]) -> str:
    """Render the structured report as pretty JSON."""

    return json.dumps(report, indent=2, sort_keys=True)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = parse_args(sys.argv[1:] if argv is None else argv)
    root = Path(args.path)

    if not root.exists():
        message = f"Path does not exist: {root}"
        if args.json:
            print(json.dumps({"error": message}, indent=2))
        else:
            print(f"Error: {message}", file=sys.stderr)
        return 1

    if not root.is_dir():
        message = f"Path is not a directory: {root}"
        if args.json:
            print(json.dumps({"error": message}, indent=2))
        else:
            print(f"Error: {message}", file=sys.stderr)
        return 1

    report = audit_repository(root)
    if args.json:
        print(render_json(report))
    else:
        print(render_markdown(report))

    return 1 if report["summary"][FAIL] else 0


if __name__ == "__main__":
    raise SystemExit(main())
