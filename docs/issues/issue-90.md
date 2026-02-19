---
type: issue
state: open
created: 2026-02-19T14:06:03Z
updated: 2026-02-19T14:35:42Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/90
comments: 2
labels: feature, area:workflow
assignees: gerchowl
milestone: none
projects: none
relationship: none
synced: 2026-02-19T15:36:54.767Z
---

# [Issue 90]: [[FEATURE] Add inception:* skill family for pre-development product thinking](https://github.com/vig-os/devcontainer/issues/90)

## Description

Add a new `inception:*` skill namespace that covers the product-thinking phase **before** development starts — from a vague signal (idea, problem, feedback, research finding) to well-scoped, actionable GitHub issues with architecture decisions documented.

The current skill pipeline begins at `issue:create` / `design:brainstorm`, which assumes the problem is already well-understood. `inception:*` fills the gap between "I have an idea" and "I have issues ready for design."

## Problem Statement

The existing skill pipeline covers the full development lifecycle:

```
issue:* → design:* → code:* → git:* → ci:* → pr:*
```

But nothing covers what happens **before** issues exist:
- Problem framing (articulating what's actually wrong)
- Prior art research (what exists already)
- Scoping (in/out, MVP vs full vision)
- Architecture evaluation (what pattern fits, validated against known designs)
- Decomposition into actionable work

This phase currently happens ad-hoc — in someone's head, in conversations, or not at all — leading to issues that are too vague or too solution-oriented without the problem being properly understood.

## Proposed Solution

### Four-phase inception pipeline

```
Signal ──→ inception:explore ──→ inception:scope ──→ inception:architect ──→ inception:plan ──→ design:brainstorm
              (diverge)           (converge)           (evaluate)             (decompose)         (existing)
```

### Phase 1: `inception:explore` — Diverge

**Purpose:** Understand the problem space. Go wide before going narrow.

**Activities:**
- Problem framing — articulate what's wrong / missing / possible
- Stakeholder mapping — who cares, who decides, who's affected
- Prior art / research — what exists (open-source, competitors, papers, standards)
- Assumptions surfacing — what are we assuming that might be wrong
- Risk identification — regulatory, technical, resource, dependency risks

**Output:** Problem Brief (early sections of RFC document).

**Interaction model:** Guided / interactive. Agent asks probing questions, pushes back on premature solutions.

### Phase 2: `inception:scope` — Converge

**Purpose:** Define what to build and what not to build.

**Activities:**
- Solution ideation — generate possible approaches (informed by prior art)
- Scoping — in/out decisions, MVP vs full vision
- Tooling & infra assessment — build vs buy
- Feasibility checks — resources, skills, time
- Success criteria — how do we know it worked, what metrics
- Phasing — sequence of deliverables if large

**Output:** Complete RFC / ADR document.

**Interaction model:** Draft & review for clear ideas; guided/interactive for ambiguous ones.

### Phase 3: `inception:architect` — Evaluate

**Purpose:** Define the system's structural shape. Validate against established patterns.

**Activities:**
- Pattern discovery — search certified system-design repos + web for relevant patterns
- Pattern matching — map the problem to known architecture archetypes
- Comparison matrix — present relevant patterns with trade-offs for specific constraints
- Component topology — define major components and their relationships (mermaid diagrams)
- Tech stack evaluation — build vs buy, framework/platform choices
- Blind spot check — "systems like this typically need X, Y, Z — have you considered these?"
- Deviation justification — document why the chosen design deviates from standard patterns

**Certified reference repos** (embedded in SKILL.md, checked first):
- ByteByteGoHq/system-design-101
- donnemartin/system-design-primer
- karanpratapsingh/system-design
- binhnguyennus/awesome-scalability
- mehdihadeli/awesome-software-architecture

Plus web search for domain-specific references the certified list doesn't cover.

**Output:** System Design Document.

**Interaction model:** Research-driven, presents comparisons.

### Phase 4: `inception:plan` — Decompose

**Purpose:** Turn the scoped solution into actionable work items.

**Activities:**
- Decomposition — break solution into independent deliverables / work streams
- Issue creation — parent issue + sub-issues on GitHub, labeled and linked
- Milestone assignment — assign work to milestones/versions
- Dependency mapping — ordering constraints between pieces
- Effort estimation — rough sizing (maps to effort:small/medium/large labels)
- Spike identification — flag unknowns needing proof-of-concept

**Output:** GitHub parent issue with sub-issues, milestone assignments, spike issues.

**Interaction model:** Draft & review.

### Artifact naming and location

- **RFCs:** `docs/rfcs/RFC-NNN-YYYY-MM-DD-short-title.md`
- **Designs:** `docs/designs/DES-NNN-YYYY-MM-DD-short-title.md`
- **Issues:** GitHub (parent + sub-issues, referencing RFC and Design docs)

### Scaling by idea size

| Idea size | explore | scope | architect | plan |
|---|---|---|---|---|
| **Small** (one issue) | Quick / skip | Quick / skip | Skip | 1 issue |
| **Medium** (few issues) | Guided | Draft & review | Light comparison | Parent + sub-issues |
| **Large** (multi-milestone) | Deep guided | Interactive | Full pattern eval | Parent + sub-issues + milestones |

Agent detects size from conversation and suggests skipping phases when appropriate.

### Key properties

- **No branch required.** Inception happens before issues exist.
- **Phases are skippable.** Agent suggests skipping for small ideas.
- **Artifacts are durable.** RFCs and designs in repo; issues on GitHub; linked together.
- **Spikes loop back.** Critical unknowns spawn spike issues that feed findings back.
- **Handoff is human "go."** No formal approval gates, just human review between phases.

## Alternatives Considered

- **Extend `design:brainstorm`** — doesn't work because brainstorm requires an issue branch and focuses on implementation design, not problem/product thinking.
- **Single monolithic `inception` skill** — too large; the phases have distinct thinking modes (divergent vs convergent vs evaluative vs analytical) that benefit from separate skills.
- **External tools (Notion, Miro)** — breaks the "everything in the repo" principle; artifacts wouldn't be version-controlled alongside code.

## Additional Context

- Extends the skill namespace pattern established in #63 (agent-driven development workflows)
- The `inception:architect` phase's certified reference list is embedded in SKILL.md for simplicity (no extra config files)
- `inception:plan` hands off directly to existing `design:brainstorm` per-issue — no gap between inception and development

## Impact

- **Beneficiaries:** Anyone starting new projects, features, or major changes using the devcontainer template
- **Compatibility:** Additive — new skills, new doc directories, no changes to existing skills
- No breaking changes

## Changelog Category

Added
---

# [Comment #1]() by [gerchowl]()

_Posted on February 19, 2026 at 02:34 PM_

## Design

### Overview

Extend the skill pipeline with a new `inception:*` namespace that covers the pre-development product-thinking phase. This fills the gap between "I have an idea" and "I have issues ready for design."

### Architecture

**Four-phase pipeline:**

```
Signal → inception:explore → inception:scope → inception:architect → inception:plan → design:brainstorm
         (diverge)           (converge)       (evaluate)            (decompose)      (existing)
```

Each phase is a separate skill in `.cursor/skills/inception:*/`.

### Components

#### 1. `inception:explore` (Phase 1 - Diverge)

**Purpose:** Understand the problem space before jumping to solutions.

**Activities:**
- Problem framing
- Stakeholder mapping
- Prior art / research
- Assumptions surfacing
- Risk identification

**Output:** Problem Brief (early sections of RFC document in `docs/rfcs/RFC-NNN-YYYY-MM-DD-short-title.md`)

**Interaction:** Guided/interactive — agent asks probing questions, pushes back on premature solutions.

#### 2. `inception:scope` (Phase 2 - Converge)

**Purpose:** Define what to build and what not to build.

**Activities:**
- Solution ideation
- In/out decisions (MVP vs full vision)
- Tooling \u0026 infra assessment (build vs buy)
- Feasibility checks
- Success criteria
- Phasing

**Output:** Complete RFC / ADR document

**Interaction:** Draft \u0026 review for clear ideas; guided/interactive for ambiguous ones.

#### 3. `inception:architect` (Phase 3 - Evaluate)

**Purpose:** Define system structure and validate against established patterns.

**Activities:**
- Pattern discovery from certified repos (embedded list in SKILL.md)
- Pattern matching to known architecture archetypes
- Comparison matrix (patterns × trade-offs × constraints)
- Component topology (mermaid diagrams)
- Tech stack evaluation
- Blind spot check
- Deviation justification

**Certified reference repos** (embedded in `inception:architect/skill.md`):
- ByteByteGoHq/system-design-101
- donnemartin/system-design-primer
- karanpratapsingh/system-design
- binhnguyennus/awesome-scalability
- mehdihadeli/awesome-software-architecture

Plus web search for domain-specific patterns.

**Output:** System Design Document in `docs/designs/DES-NNN-YYYY-MM-DD-short-title.md`

**Interaction:** Research-driven, presents comparisons.

#### 4. `inception:plan` (Phase 4 - Decompose)

**Purpose:** Turn scoped solution into actionable GitHub issues.

**Activities:**
- Decomposition into independent deliverables
- Issue creation (parent + sub-issues)
- Milestone assignment
- Dependency mapping
- Effort estimation (maps to `effort:small/medium/large` labels)
- Spike identification

**Output:** GitHub parent issue with sub-issues, milestone assignments, spike issues.

**Interaction:** Draft \u0026 review.

### Scaling by Idea Size

| Size | explore | scope | architect | plan |
|------|---------|-------|-----------|------|
| **Small** (one issue) | Quick/skip | Quick/skip | Skip | 1 issue |
| **Medium** (few issues) | Guided | Draft \u0026 review | Light comparison | Parent + sub-issues |
| **Large** (multi-milestone) | Deep guided | Interactive | Full pattern eval | Parent + sub + milestones |

Agent detects size from conversation and suggests skipping phases when appropriate.

### Key Properties

- **No branch required** — inception happens before issues exist
- **Phases are skippable** — agent suggests skipping for small ideas
- **Artifacts are durable** — RFCs and designs in repo, issues on GitHub, linked together
- **Spikes loop back** — critical unknowns spawn spike issues that feed findings back
- **Handoff is human "go"** — no formal approval gates, just human review between phases

### Data Flow

1. User signals an idea to an inception skill
2. Agent produces artifact (RFC, design doc, issues)
3. Agent posts artifact to appropriate location (docs/, GitHub)
4. Agent proceeds to next phase or hands off to existing `design:brainstorm`
5. Spikes (if created) loop back to earlier phases when complete

### Error Handling

- If agent cannot make a reasonable decision → use existing `worktree:ask` pattern to post question on issue
- If phase is inappropriate for idea size → agent suggests skipping
- If certified repos are unavailable → fall back to web search only

### Testing Strategy

- Integration tests: invoke each skill with sample inputs, verify outputs (RFC files, design docs, GitHub issues created)
- End-to-end test: run full pipeline from `inception:explore` through `inception:plan`, verify handoff to `design:brainstorm`
- Test scaling behavior: small/medium/large idea sizes produce appropriate outputs

### Implementation Notes

- Each skill is a separate directory: `.cursor/skills/inception:{explore,scope,architect,plan}/`
- Skills follow existing skill structure: `skill.md` with YAML frontmatter
- Artifact templates: provide RFC and design doc templates in `docs/templates/`
- Certified repo list: embedded directly in `inception:architect/skill.md` (no external config)
- Document directories: create `docs/rfcs/` and `docs/designs/` if they don't exist

---

# [Comment #2]() by [gerchowl]()

_Posted on February 19, 2026 at 02:35 PM_

## Implementation Plan

Issue: #90
Branch: worktree/90

### Overview

Implementing the `inception:*` skill family requires creating 4 new skills, document templates, and integration tests. Following TDD: write tests first, then implementation.

### Tasks

#### Phase 1: Directory Structure and Templates

- [ ] **Create document directories** — `docs/rfcs/` and `docs/designs/` — verify: `ls -d docs/rfcs docs/designs`
- [ ] **Create RFC template** — `docs/templates/RFC.md` with frontmatter (number, date, title, status, authors) and sections (Problem, Proposal, Alternatives, Impact) — verify: `cat docs/templates/RFC.md`
- [ ] **Create Design template** — `docs/templates/DESIGN.md` with frontmatter and sections (Overview, Architecture, Components, Data Flow, Testing) — verify: `cat docs/templates/DESIGN.md`

#### Phase 2: inception:explore Skill (TDD)

- [ ] **Write failing test for inception:explore** — `tests/test_inception_explore.py` with fixtures for user input and expected RFC structure — verify: `just test-pytest tests/test_inception_explore.py` (fails)
- [ ] **Create inception:explore skill** — `.cursor/skills/inception:explore/SKILL.md` with guided/interactive prompts for problem framing — verify: skill file exists
- [ ] **Make test pass** — implement skill logic — verify: `just test-pytest tests/test_inception_explore.py` (passes)

#### Phase 3: inception:scope Skill (TDD)

- [ ] **Write failing test for inception:scope** — `tests/test_inception_scope.py` testing RFC completion and scoping decisions — verify: test fails
- [ ] **Create inception:scope skill** — `.cursor/skills/inception:scope/SKILL.md` for scoping and feasibility — verify: skill file exists
- [ ] **Make test pass** — implement scoping logic — verify: `just test-pytest tests/test_inception_scope.py` (passes)

#### Phase 4: inception:architect Skill (TDD)

- [ ] **Write failing test for inception:architect** — `tests/test_inception_architect.py` including pattern discovery mock, design doc generation — verify: test fails
- [ ] **Create inception:architect skill** — `.cursor/skills/inception:architect/SKILL.md` with embedded certified repo list (ByteByteGoHq/system-design-101, donnemartin/system-design-primer, karanpratapsingh/system-design, binhnguyennus/awesome-scalability, mehdihadeli/awesome-software-architecture) — verify: skill file exists
- [ ] **Make test pass** — implement pattern matching and design doc generation — verify: `just test-pytest tests/test_inception_architect.py` (passes)

#### Phase 5: inception:plan Skill (TDD)

- [ ] **Write failing test for inception:plan** — `tests/test_inception_plan.py` testing GitHub issue creation, milestone assignment, parent/sub-issue linking — verify: test fails
- [ ] **Create inception:plan skill** — `.cursor/skills/inception:plan/SKILL.md` for decomposition and issue creation — verify: skill file exists
- [ ] **Make test pass** — implement issue creation via GitHub API — verify: `just test-pytest tests/test_inception_plan.py` (passes)

#### Phase 6: Integration and End-to-End Testing

- [ ] **Write integration test** — `tests/test_inception_integration.py` running full pipeline explore→scope→architect→plan — verify: test fails initially
- [ ] **Fix integration issues** — ensure handoffs work between phases — verify: `just test-pytest tests/test_inception_integration.py` (passes)
- [ ] **Update CLAUDE.md** — add inception:* skills to custom commands table — verify: `rg "inception:" CLAUDE.md`

#### Phase 7: Documentation

- [ ] **Update CHANGELOG.md** — add entry under `## Unreleased` / `### Added` — verify: `rg "inception" CHANGELOG.md`
- [ ] **Create skill README** — `.cursor/skills/inception:explore/README.md` (or combined inception README) explaining when/how to use each phase — verify: file exists

### Verification Strategy

Each task includes inline verification commands. Final verification:
- `just test` — all tests pass
- `just lint` — no style violations
- Manual smoke test: invoke each skill with sample inputs

### Dependencies

- Tasks within each phase must be sequential (test → skill → pass test)
- Phases 2-5 can be parallelized after Phase 1 completes
- Phase 6 depends on Phases 2-5
- Phase 7 can start after Phase 6

