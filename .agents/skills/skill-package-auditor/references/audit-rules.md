# Skill Package Audit Rules

This reference documents the deterministic checks performed by `scripts/audit_skill_package.py`. The auditor is a static structure checker for reusable AI skill assignment readiness.

## Required Repository Structure

The audited path must be an existing local directory. The auditor searches for skill folders in these locations:

- `.agents/skills/*`
- `.claude/skills/*`

At least one skill folder must be detected. Each direct child folder under those paths is treated as one skill package.

## Required SKILL.md Checks

For each detected skill folder, the auditor checks that:

- The folder name is lowercase and hyphenated, such as `skill-package-auditor`.
- `SKILL.md` exists at the root of the skill folder.
- `SKILL.md` starts with YAML-style frontmatter bounded by `---`.
- The frontmatter includes `name:`.
- The frontmatter includes `description:`.
- The `name:` value exactly matches the skill folder name.
- The `description:` value is at least 60 characters long.
- The `description:` includes an activation phrase: `Use when`, `Use this skill`, or `when the user`.

## Required Scripts Folder Checks

For each detected skill folder, the auditor checks that:

- A `scripts/` directory exists inside the skill folder.
- The `scripts/` directory contains at least one file ending in `.py`.

The auditor only checks file presence. It does not import, run, lint, or grade scripts found in the audited repository.

## README And Video Link Checks

At the repository root, the auditor checks that:

- `README.md` exists.
- `README.md` includes the word `video`, case-insensitively.
- `README.md` includes at least one URL beginning with `http://` or `https://`.

The auditor does not verify whether the URL is reachable, public, or actually points to a video. It only checks that video evidence is represented in the README.

## Warning Vs Failure Logic

The current audit rules use `PASS` and `FAIL` statuses. `WARN` is included in the report format for future expansion, but no current rule emits warnings.

The CLI exits with:

- `0` when there are no `FAIL` items.
- `1` when one or more `FAIL` items exist.

Missing required structure, metadata, scripts, or README video URL evidence is treated as a failure because these items affect submission readiness.

## What The Auditor Intentionally Does Not Check

The auditor does not perform deep review or runtime validation. It intentionally does not check:

- Remote GitHub repositories that have not been cloned locally.
- Whether discovered scripts execute successfully.
- Whether scripts are secure, correct, or well designed.
- Whether the skill instructions are high quality beyond the deterministic metadata rules.
- Whether a README video link is reachable or viewable.
- Whether the assignment receives full credit from an instructor.
- Plagiarism, licensing, dependency safety, or repository history.

The auditor is best understood as a fast, deterministic submission-readiness checklist.
