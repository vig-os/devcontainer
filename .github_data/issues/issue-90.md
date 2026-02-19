---
type: issue
state: open
created: 2026-02-19T14:06:03Z
updated: 2026-02-19T14:06:03Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/90
comments: 0
labels: feature, area:workflow
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-19T14:06:20.285Z
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
