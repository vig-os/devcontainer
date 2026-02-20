---
name: issue_create
description: Creates a new GitHub issue using the appropriate issue template.
disable-model-invocation: true
---

# Create a GitHub Issue

Create a new GitHub issue using the appropriate issue template.

## Workflow Steps

1. **Determine issue type from context**
   - Infer which template to use based on the user's description:
     - Bug → `bug` (label: `bug`)
     - Feature/enhancement → `feature` (label: `feature`)
     - Refactoring → `refactor` (label: `refactor`)
     - Documentation → `docs` (label: `docs`)
     - CI/Build change, general task, maintenance → `chore` (label: `chore`)
   - Canonical labels are defined in `.github/label-taxonomy.toml` (single source of truth).
   - Ask the user if ambiguous.

2. **Populate fields from conversation context**
   - Draft a title following the template's prefix (e.g. `[FEATURE] ...`, `[BUG] ...`).
   - Draft the body with all required fields from the chosen template.
   - Include a Changelog Category value based on the issue type.

3. **Show draft and ask for confirmation**
   - Present the title, labels, and body to the user.
   - Wait for approval or edits before proceeding.

4. **Create the issue**

   ```bash
   gh issue create --title "<title>" --label "<label>" --body "<body>"
   ```

5. **Report the issue URL**
   - Show the user the created issue URL and number.

## Important Notes

- Canonical labels are defined in `.github/label-taxonomy.toml`. When unsure, check `gh label list` or read the taxonomy file.
- Do not create the issue until the user has approved the draft.
- If the user wants to start working on it immediately, follow up with the [issue:claim](../issue_claim/SKILL.md) workflow.
