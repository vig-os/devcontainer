# Git Commit Workflow

Execute the commit workflow following the project's commit message conventions.

## Workflow Steps

1. **Get staged changes context** with this command:

   ```bash

git status && echo "=== STAGED CHANGES ===" && git diff --cached

   ```

2. **Analyze the output** to understand:
- What files are staged vs un-staged
- Change types and scope (additions/deletions)
- Which changes will actually be committed

3. **Write accurate commit message** based on staged changes only:
- Follow rules in [.commit-messages.mdc](../rules/commit-messages.mdc)
- Include details in list form if helpful for larger commits

4. **Execute git commit command** using run_terminal_cmd for user review

## Important Notes

- Generate minimum output; user only needs final commit command
- Do not read/summarize git command output after execution unless asked
- User can modify the commit command in shell before executing
- Your shell is already at the project root so you do not need `cd` or 'bash', just use `git ...`
