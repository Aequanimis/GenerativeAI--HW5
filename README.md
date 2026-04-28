# Week 5 - Reusable AI Skill: Skill Package Auditor

This project contains a reusable AI skill named `skill-package-auditor`. The skill helps an agent audit whether a local repository follows the expected reusable AI skill assignment structure before submission.

Video walkthrough: https://youtu.be/-RgQ75ZWzNU

## What The Skill Does

`skill-package-auditor` checks a local repository for the main structural requirements of a reusable AI skill package:

- A skill folder under `.agents/skills/<skill-name>/` or `.claude/skills/<skill-name>/`
- A valid `SKILL.md` file with frontmatter
- Matching skill folder and frontmatter names
- A specific enough frontmatter description with an activation phrase
- A `scripts/` folder
- At least one Python script in `scripts/`
- A root `README.md`
- README evidence of a video walkthrough link

The skill produces a clear Markdown report by default and can also produce JSON for machine-readable output.

## Why I Chose This Skill

I chose this skill because reusable AI skill assignments have several structural requirements that are easy to miss when working quickly. A static auditor gives the agent a repeatable way to check the package before submission instead of relying only on manual review.

This also makes the skill useful beyond this one project. Any future skill package can be checked with the same script and report format.

## Why The Python Script Is Load-Bearing

The Python script is genuinely load-bearing because it performs deterministic checks that an agent might otherwise handle inconsistently. It walks the repository structure, parses simple `SKILL.md` frontmatter, validates naming rules, checks for required folders and Python scripts, verifies README video-link evidence, counts PASS/WARN/FAIL items, and sets the correct exit code.

Without the script, the skill would only be a set of instructions. With the script, the agent can run the same audit repeatedly and get consistent results across the good, edge, and limited demo cases.

## Folder Structure

```text
.
|-- .agents/
|   `-- skills/
|       `-- skill-package-auditor/
|           |-- SKILL.md
|           |-- references/
|           |   `-- audit-rules.md
|           `-- scripts/
|               `-- audit_skill_package.py
|-- demo_cases/
|   |-- good-skill-repo/
|   |   |-- README.md
|   |   `-- .agents/skills/csv-row-counter/
|   |       |-- SKILL.md
|   |       `-- scripts/count_rows.py
|   |-- edge-missing-video/
|   |   |-- README.md
|   |   `-- .agents/skills/csv-row-counter/
|   |       |-- SKILL.md
|   |       `-- scripts/count_rows.py
|   `-- limited-not-a-skill-repo/
|       `-- README.md
|-- demo-prompts.md
`-- README.md
```

## How To Use The Skill In An Agent

Ask the agent to use `skill-package-auditor` on a local repository path. The agent should run the bundled Python script, review the report, and summarize the results in plain language.

Example:

```text
Use the skill-package-auditor skill to audit this repository before I submit it.
```

The skill is designed for local repositories only. It should not audit remote GitHub URLs unless the repository has already been cloned locally.

## How To Run The Script Manually

From the repository root, run:

```bash
python .agents/skills/skill-package-auditor/scripts/audit_skill_package.py .
```

Run it on the included demo cases:

```bash
python .agents/skills/skill-package-auditor/scripts/audit_skill_package.py demo_cases/good-skill-repo
python .agents/skills/skill-package-auditor/scripts/audit_skill_package.py demo_cases/edge-missing-video
python .agents/skills/skill-package-auditor/scripts/audit_skill_package.py demo_cases/limited-not-a-skill-repo
```

For JSON output:

```bash
python .agents/skills/skill-package-auditor/scripts/audit_skill_package.py . --json
```

Exit code behavior:

- `0` means no FAIL items were found.
- `1` means one or more FAIL items were found.

## Demo Prompts

Normal case:

```text
Use skill-package-auditor to check demo_cases/good-skill-repo and summarize whether it is ready for submission.
```

Edge case:

```text
Use skill-package-auditor to check demo_cases/edge-missing-video and explain what is missing.
```

Cautious/limited case:

```text
Use skill-package-auditor to check demo_cases/limited-not-a-skill-repo and explain why the result is limited.
```

## What Worked Well

The script provides a stable checklist that is easy to run from an agent or manually from the command line. The Markdown report is readable for humans, while the JSON mode makes the same audit data available for automated workflows.

The demo cases also make the behavior easier to understand. One case passes, one shows a realistic missing-video-link issue, and one demonstrates what happens when the folder is not actually a skill package.

## Remaining Limitations

This auditor checks structure and submission readiness, not overall assignment quality. It does not run unknown scripts inside the target repository, grade the usefulness of the skill, perform security review, or verify that a video URL is reachable.

The frontmatter parser is intentionally simple and only supports straightforward `key: value` metadata lines. That keeps the script dependency-free, but it is not a full YAML parser.
