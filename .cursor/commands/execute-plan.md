# Execute Plan

Work through an implementation plan in batches with human checkpoints.

## Workflow Steps

### 1. Load the plan

- Read the plan from `docs/plans/` or from the conversation context.
- List all tasks with their status (pending, in progress, done).

### 2. Execute in batches

- Work through tasks sequentially, 2-3 tasks per batch.
- For each task:
  1. Announce which task you're starting.
  2. Implement the change (following [coding-principles](../rules/coding-principles.mdc) and TDD).
  3. Run the task's verification step.
  4. Report result (pass/fail with evidence).

### 3. Checkpoint after each batch

- After completing a batch, stop and show the user:
  - Tasks completed in this batch
  - Verification results
  - Tasks remaining
- Wait for the user to say "continue" before starting the next batch.

### 4. Handle failures

- If a verification step fails, stop the batch.
- Diagnose using [debug](debug.md) principles if needed.
- Fix the issue before continuing to the next task.
- Do not skip failing tasks.

### 5. Wrap up

- After all tasks are done, run the full test suite: `just test`
- Report final status.
- Suggest committing and proceeding to [submit-pr](submit-pr.md).

## Important Notes

- Never skip a checkpoint. The user must approve each batch.
- Each task should result in a working, testable state.
- If the plan needs adjustment mid-execution, update it and get user approval before continuing.
