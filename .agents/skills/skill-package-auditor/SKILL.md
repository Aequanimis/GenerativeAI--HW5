---
name: skill-package-auditor
description: Audits a local AI skill repository for reusable skill assignment requirements, including SKILL.md metadata, scripts folder, Python script presence, README video link, and folder naming. Use when the user asks to inspect, validate, or prepare a skill package before submission.
---

# Skill Package Auditor

## When To Use This Skill

Use this skill when the user wants to inspect a locally available repository for reusable AI skill assignment readiness. It is intended for checking whether a project follows the expected submission structure, including skill folder placement, `SKILL.md` metadata, bundled scripts, Python script presence, root `README.md`, and demo video link evidence.

Typical requests include:

- Validate a skill package before submission.
- Check whether a repository has the required reusable skill folder structure.
- Audit `.agents/skills/<skill-name>/` or `.claude/skills/<skill-name>/` folders.
- Produce a clear report of missing assignment requirements.
- Generate machine-readable audit output with JSON.

## When Not To Use This Skill

Do not use this skill for remote-only repositories. If the user gives a GitHub URL or another remote URL, ask them to clone the repository locally first, or audit an already cloned local path.

Do not use this skill as a deep security review, code-quality grade, plagiarism check, runtime behavior test, or complete assignment evaluation. The auditor checks structure and submission readiness only.

Do not use this skill to execute, import, or dynamically inspect unknown scripts inside the target repository. The audit must remain static.

## Expected Inputs

The primary input is a local repository path, such as:

```bash
python .agents/skills/skill-package-auditor/scripts/audit_skill_package.py .
```

The path may point to the current repository or to a local demo case:

```bash
python .agents/skills/skill-package-auditor/scripts/audit_skill_package.py demo_cases/good-skill-repo
```

For machine-readable output, pass `--json`:

```bash
python .agents/skills/skill-package-auditor/scripts/audit_skill_package.py . --json
```

## Instructions For The Agent

1. Confirm that the target is a local path. If the user provides a remote URL, explain that this skill only audits local repositories and ask for a cloned local path.
2. Locate the bundled audit script at `scripts/audit_skill_package.py` inside this skill folder.
3. Run the Python script against the target repository path for deterministic checks.
4. Use the default Markdown report for user-facing audits unless the user specifically asks for JSON.
5. Review the script output and exit code. Exit code `0` means there are no FAIL items. Exit code `1` means one or more FAIL items were found.
6. Summarize the report in plain language after running the script. Highlight the PASS/WARN/FAIL counts, detected skill folders, and the most important suggested fixes.
7. If the script reports a missing path, missing `SKILL.md`, missing metadata, missing `scripts/`, missing Python scripts, or missing README video URL, describe the fix concretely.
8. Keep the audit static. Do not run any scripts found inside the target repository other than this skill's own auditor script.

## Expected Output Format

For normal user-facing audits, provide:

- A short plain-language summary.
- The audited path.
- PASS/WARN/FAIL counts.
- Detected skill folders.
- The highest-priority suggested fixes.
- A note that the audit checks structure and submission readiness, not runtime correctness or grading quality.

When the user asks for JSON, return or summarize the JSON produced by the script. The JSON report includes:

- `audited_path`
- `summary`
- `skill_folders`
- `checks`
- `suggested_fixes`

## Important Limitations And Safety Checks

This skill audits repository structure only. It does not grade the quality of the skill instructions, verify whether a video is actually viewable, assess code security, or execute the submitted skill's scripts.

Never execute unknown scripts inside the target repository. The only script this skill should run is the bundled `audit_skill_package.py` checker.

Never audit a remote GitHub URL directly. The repository must exist on the local filesystem first.

Treat the audit result as a submission-readiness signal, not as final confirmation that an instructor will accept the assignment.
