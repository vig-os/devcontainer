# Write Implementation Plan

Break an approved design or issue into bite-sized implementation tasks.

## Workflow Steps

### 1. Read the source

- If a design doc exists in `docs/plans/`, read it.
- Otherwise, read the linked GitHub issue (acceptance criteria, implementation notes).
- Identify all deliverables, constraints, and test requirements.

### 2. Break into tasks

- Each task should be completable in 2-5 minutes.
- Each task must specify:
  - **What**: one sentence describing the change
  - **Files**: exact file paths to create or modify
  - **Verification**: how to confirm the task is done (e.g. `just test-image`, specific test passes)
- Order tasks by dependency — earlier tasks should not depend on later ones.

### 3. Identify test tasks

- For each functional task, include a corresponding test task (or note that the test is part of the same task).
- Follow TDD: test tasks come before or alongside implementation tasks, not after.

### 4. Present plan for approval

- Show the full task list to the user.
- Ask for confirmation or adjustments before proceeding.

### 5. Save plan

- Write to `docs/plans/YYYY-MM-DD-<name>-plan.md`.
- Commit the plan.

## Important Notes

- Do not start implementation until the user approves the plan.
- If a task is too large to describe in one sentence, split it.
- Reference specific `just` recipes for verification where applicable.
- The plan is the input for [execute-plan](execute-plan.md).
