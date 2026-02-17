# After PR merge: cleanup and switch branch

When the user asks to clean up after a PR merge (or to "delete PR text, checkout base, update, delete branch locally"), follow these steps.

## Context

After opening a PR from a feature branch (e.g. `feature/34-...`) into a base branch (e.g. `feature/37-...`) and the PR is merged, the user may want to:
- Remove the local PR draft file
- Switch to the base branch and update it
- Delete the feature branch locally

## Steps

1. **Delete the PR text file**
   If the user created a draft at `.github/pr-<issue>-into-<base>.md` (e.g. `.github/pr-34-into-37.md`), delete that file.

2. **Checkout the base branch**
   Check out the branch that was the PR base (e.g. `feature/37-automate-standardize-repository-setup`).
   Infer the branch name from the user’s wording (e.g. "branch 37" → `feature/37-automate-standardize-repository-setup`; use `gh issue develop --list <issue>` if needed to resolve the branch name).

3. **Update the base branch**
   Run:
   `git pull origin <base-branch>`

4. **Delete the feature branch locally**
   Delete the branch that was merged (e.g. `feature/34-rename-venv-container-creation`).
   Run:
   `git branch -d <feature-branch>`
   Use the branch name the user indicates (e.g. "branch 34" → `feature/34-...`; list with `git branch` if needed).

## Notes

- Confirm which PR file, base branch, and feature branch to use from the user’s message or ask if ambiguous.
- If the user says "delete branch 34 locally", the feature branch is the one for issue 34 (e.g. `feature/34-rename-venv-container-creation`).
- This workflow applies to both feature branches (to `dev`) and fix branches (to `release/X.Y.Z`). For the full release workflow, see [../docs/RELEASE_CYCLE.md](../docs/RELEASE_CYCLE.md).
