# Create a GitHub Issue

Create a new GitHub issue using the appropriate issue template.

## Workflow Steps

1. **Determine issue type from context**
   - Infer which template to use based on the user's description:
     - Bug → `bug_report` (label: `bug`)
     - Feature/enhancement → `feature_request` (label: `feature`)
     - Refactoring → `refactor` (label: `refactor`)
     - Documentation → `documentation` (label: `docs`)
     - CI/Build change → `ci_build` (label: `ci`)
     - General work item → `task` (label: `task`)
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

- Use the correct repo labels (check `gh label list` if unsure). Known mappings: `feature` (not `enhancement`), `bug`, `docs`, `task`.
- Do not create the issue until the user has approved the draft.
- If the user wants to start working on it immediately, follow up with the [start-issue](start-issue.md) workflow.
