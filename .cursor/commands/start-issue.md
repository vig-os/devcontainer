# Start Work on an Issue

Set up the local environment to begin working on a GitHub issue.

## Workflow Steps

1. **Identify the issue**
   - The user will reference an issue number (e.g. "start issue 63", "work on #63", or a `.github_data/issues/issue-63.md` file).
   - Run `gh issue view <number> --json title,labels,body` to get context.

2. **Check for existing linked branch**
   - Run: `gh issue develop --list <issue_number>`
   - If a branch already exists, offer to check it out: `git fetch origin && git checkout <branch>`.
   - Do not create a second linked branch.

3. **Stash dirty working tree if needed**
   - Run `git status --short`. If there are uncommitted changes, run `git stash push -u -m "before-issue-<number>"` and tell the user.

4. **Follow the branch naming rule**
   - Apply the workflow in [../rules/branch-naming.mdc](../rules/branch-naming.mdc): infer type, derive short summary, propose branch name, wait for user confirmation.

5. **Create and link the branch**
   - After user confirms: `gh issue develop <issue_number> --base dev --name <branch_name> --checkout`
   - Then: `git pull origin <branch_name>`

6. **Restore stash if applicable**
   - If you stashed in step 3: `git stash pop`

## Important Notes

- Always ask the user to confirm the branch name before creating it.
- If `gh issue develop` fails because the branch already exists on remote, run `git fetch origin && git checkout <branch_name>` instead.
- Read the issue body after checkout so you have context for the work ahead.
