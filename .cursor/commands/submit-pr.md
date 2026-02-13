# Submit Pull Request

Prepare and submit a pull request for **feature or bugfix work**.

> **Note:** This workflow is for regular development PRs (feature/bugfix branches to `dev`).
> For **release PRs**, see [../docs/RELEASE_CYCLE.md](../docs/RELEASE_CYCLE.md) — releases are automated via `prepare-release.sh`.

## Workflow Steps

### 1. Ensure Git is up to date

- Run `git status` and `git fetch origin`. If the current branch has a remote tracking branch, run `git pull --rebase origin <current-branch>` (or `git pull` if the user prefers merge) so the branch is up to date with the remote.
- If there are uncommitted changes, list them and ask the user to commit or stash before submitting the PR. Do not prepare the PR until the working tree is clean (or the user explicitly says to proceed with uncommitted changes).

### 2. Verify target branch

- Confirm the **base (target) branch** for the PR (e.g. `dev`, `feature/37-automate-standardize-repository-setup`). If the user did not specify it, infer from context (e.g. "into 37" → branch for issue 37) or ask. Use `gh issue develop --list <issue>` if needed to resolve a branch name from an issue number.

### 3. Ensure CHANGELOG has been updated

- Compare the list of commits (and/or files changed) on the current branch vs the base branch to the **Unreleased** section of `CHANGELOG.md`.
- Every user-facing or notable change in the PR must be documented under Unreleased (Added, Changed, Fixed, etc.). If something is missing, add the corresponding bullet(s) to `CHANGELOG.md` and tell the user what you added, or prompt the user to update the CHANGELOG before submitting.

### 4. Prepare PR text following template

- Use the structure of [.github/pull_request_template.md](.github/pull_request_template.md).
- Populate **Description**, **Related Issue(s)** (e.g. Closes #NN), **Type of Change**, **Changes Made** (from `git log base..HEAD` and `git diff --stat base...HEAD`), **Testing**, and **Checklist** from the current branch and your knowledge of the changes.
- Write the body to a file (e.g. `.github/pr-draft-<issue>-into-<base>.md` or similar) so the user can edit it if needed.

### 5. Ask user to review and choose assignee and reviewers

- Show the user the **title** you will use (e.g. `feat: short description (#NN)`) and the **PR body** (full markdown).
- Ask the user to confirm or edit the text.
- Ask the user to specify **assignee** and **reviewers** (e.g. "assign to me, no reviewers" or "assign @c-vigo, reviewers @foo"). Do not run `gh pr create` until the user approves and provides assignee/reviewers.

### 6. Submit PR

- Run:

  ```bash
  gh pr create --base <target-branch> --title "<title>" --body-file <path-to-draft> [--assignee <login>] [--reviewer <login> ...]
  ```

- Use the approved title and body file. Add `--assignee` and `--reviewer` only as specified by the user.
- After the PR is created, tell the user the PR URL and that they can delete the draft body file if they want.

## Important Notes

- Default branch for "into 37" is `feature/37-automate-standardize-repository-setup` (or the result of `gh issue develop --list 37`). Confirm with the user when ambiguous.
- If CHANGELOG is missing entries, add them in the same style as existing Unreleased items; do not leave the PR without CHANGELOG updates for new changes.
- Never submit the PR (step 6) until the user has approved the text and provided assignee/reviewers preferences.
