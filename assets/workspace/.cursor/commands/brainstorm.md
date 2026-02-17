# Brainstorm

Explore requirements and design before writing any code. This command activates before creative work — features, components, behavior changes.

**Rule: no code until the user approves a design.**

## Workflow Steps

### 1. Explore project context

- Read relevant files, docs, recent commits to understand current state.
- Identify constraints, existing patterns, and related code.

### 2. Ask clarifying questions

- One question at a time. Do not overwhelm.
- Prefer multiple choice when possible; open-ended is fine when needed.
- Focus on: purpose, constraints, success criteria, edge cases.
- Continue until you understand the full scope.

### 3. Propose approaches

- Present 2-3 approaches with trade-offs.
- Lead with your recommended option and explain why.
- Apply YAGNI — cut anything speculative.

### 4. Present design for approval

- Present the design in sections, scaled to complexity.
- After each section, ask: "Does this look right so far?"
- Cover: architecture, components, data flow, error handling, testing strategy.
- Revise if the user pushes back. Go back to questions if something is unclear.

### 5. Save design document

- Write the validated design to `docs/plans/YYYY-MM-DD-<name>-design.md`.
- Commit the design doc.

### 6. Transition to planning

- Hand off to the [plan](plan.md) command to break the design into implementation tasks.

## Important Notes

- Every project goes through this, regardless of perceived simplicity. The design can be short (a few sentences) for truly simple tasks, but it must exist and be approved.
- Do not invoke any implementation command or write any code until design is approved.
- If the user says "just do it" or "skip design", push back once explaining why, then comply if they insist.
