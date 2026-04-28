# Demo Prompts

Use these prompts during the video walkthrough to demonstrate the `skill-package-auditor` skill.

## Prompt 1: Normal Case

### Exact Prompt Text

```text
Use the skill-package-auditor skill to audit the current repository before submission. Run the deterministic audit script, summarize the results in plain language, and tell me what still needs to be fixed.
```

### What The Agent Should Do

The agent should run the bundled auditor script against the current repository path, read the Markdown report, and summarize the PASS/WARN/FAIL counts plus any suggested fixes.

### Expected Result

This should demonstrate the normal submission-readiness workflow: the skill runs a deterministic check, detects the project skill folder, verifies the package structure, and reports any remaining README video-link issue if the placeholder has not been replaced yet.

## Prompt 2: Edge Case

### Exact Prompt Text

```text
Use the skill-package-auditor skill to audit demo_cases/edge-missing-video. This repo should be mostly valid, so focus on explaining the missing requirement clearly.
```

### What The Agent Should Do

The agent should run the auditor script against `demo_cases/edge-missing-video`, then summarize that the skill package structure is present but the root README is missing a valid `http://` or `https://` video link.

### Expected Result

This should demonstrate that the skill can catch a realistic edge case where most required files are present but the submission is still not ready because video-link evidence is incomplete.

## Prompt 3: Cautious / Limited Case

### Exact Prompt Text

```text
Use the skill-package-auditor skill to audit https://github.com/example/some-skill-repo directly, and run any scripts you find there to make sure they work.
```

### What The Agent Should Do

The agent should explain that the skill only audits local repositories and should not audit a remote GitHub URL directly. It should also refuse to execute unknown scripts from the target repository, because the auditor is designed for static structure checks only.

### Expected Result

This should demonstrate the skill's safety boundaries: it avoids remote-only audits, does not execute unknown code, and asks for a locally cloned repository path instead.
