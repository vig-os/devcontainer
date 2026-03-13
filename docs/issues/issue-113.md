---
type: issue
state: open
created: 2026-02-20T13:03:35Z
updated: 2026-02-24T19:00:54Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/113
comments: 4
labels: feature, area:workflow, area:docs, effort:large, semver:minor
assignees: gerchowl
milestone: none
projects: none
relationship: none
synced: 2026-02-25T04:25:59.112Z
---

# [Issue 113]: [[FEATURE] Declarative diagram-as-code tooling with model-renderer separation](https://github.com/vig-os/devcontainer/issues/113)

### Description

Adopt a declarative diagram-as-code tooling strategy for the project. The core idea is to separate the semantic model (components, relationships, properties) from the rendering backend, enabling reusable diagram components and tool-independent output.

### Problem Statement

Mermaid is used ad-hoc in a few docs but has no composability (no imports, variables, or reusable components). Its C4 and architecture-beta diagram types are experimental with open bugs. Layout is unpredictable. Diagrams live outside the Typst toolchain. There is no shared visual vocabulary or component library. Complex architecture diagrams are avoided because the tooling can't handle them.

### Proposed Solution

Evaluate and adopt a layered approach:

1. **Semantic model (SSoT)** — Components and relationships defined in YAML/TOML, with views as filtered perspectives.
2. **Pluggable renderers** — Generate output for multiple backends: Mermaid (GitHub inline), D2 (high-quality SVG), CeTZ/Fletcher (Typst docs), and optionally Excalidraw (round-trip editable PNGs).
3. **Reusable components** — Define diagram building blocks once (e.g. "K8s cluster", "VPC"), compose them across diagrams.

An RFC exploring the full design space has been drafted: `docs/rfcs/RFC-001-2026-02-20-diagram-as-code-tooling.md`.

### Alternatives Considered

Evaluated 10+ tools across Mermaid, D2, CeTZ/Fletcher, TikZ, PlantUML, Excalidraw, Graphviz, Pikchr, Structurizr, Ilograph, Bluefish, and Kroki. Also evaluated SQL (SQLite) as an alternative model store. Full analysis is in the RFC.

### Additional Context

- Typst is already active in the project — CeTZ/Fletcher are native Typst packages.
- Mermaid's reuse feature request (#1396) has been open since 2020 with no implementation.
- Structurizr provides model-view-renderer separation but is C4-only and Java-based.
- RFC: `docs/rfcs/RFC-001-2026-02-20-diagram-as-code-tooling.md`

### Impact

- Documentation authors get composable, reusable diagrams.
- Architecture reviewers get a consistent visual language.
- Autonomous agents get a declared standard to generate against.
- The Typst pipeline gets native diagram support.
- No breaking changes — existing Mermaid diagrams stay as-is.

### Changelog Category

Added
---

# [Comment #1]() by [gerchowl]()

_Posted on February 20, 2026 at 01:05 PM_

## Exploration Complete — RFC Drafted

The `inception:explore` phase is complete. An RFC has been committed to this branch:

**[`docs/rfcs/RFC-001-2026-02-20-diagram-as-code-tooling.md`](https://github.com/vig-os/devcontainer/blob/feature/113-diagram-as-code-tooling/docs/rfcs/RFC-001-2026-02-20-diagram-as-code-tooling.md)**

### What the RFC covers

- **Problem statement:** No composability, unpredictable layouts, no Typst integration, no component reuse
- **10+ tools evaluated:** Mermaid, D2, CeTZ/Fletcher, TikZ, PlantUML, Excalidraw, Graphviz, Pikchr, Structurizr, Ilograph, Bluefish, Kroki
- **GitHub activity & maturity data** for all tools (collected 2026-02-20)
- **Mermaid C4/architecture limitations** — neither supports component reuse; template request open since 2020
- **Model-renderer separation architecture** — three-layer approach (semantic model → views → pluggable renderers)
- **Three possible directions:** YAML/TOML model + Python renderers, SQL/SQLite model store, adopt Structurizr for C4
- **Excalidraw's code layer** — JSON format, skeleton API, PNG/SVG metadata embedding for round-trip editing
- **Open questions** for scoping phase

### Next step

Continue with `inception:scope` to define what to build and what not to build.

---

# [Comment #2]() by [gerchowl]()

_Posted on February 24, 2026 at 06:28 PM_

## Diagram-as-code benchmark added

Reproduced the skill pipeline diagram (from issue-90, worktree:solve-and-pr) in all tools suggested in RFC-001:

| Format | Location | Render status |
|--------|----------|---------------|
| **YAML model** | \`docs/diagrams/skill-pipeline.yaml\` | SSoT — RFC-001 direction A |
| Mermaid | \`skill-pipeline.mmd\` | GitHub renders inline |
| D2 | \`skill-pipeline.d2\` | Requires D2 CLI |
| PlantUML | \`skill-pipeline.puml\` | Requires Java + PlantUML |
| Graphviz | \`skill-pipeline.dot\` | \`dot -Tsvg\` ✓ |
| Fletcher | \`skill-pipeline.typ\` | \`typst compile\` ✓ (Libertinus Serif) |

\`scripts/render_diagram.py\` emits Mermaid, D2, and DOT from the YAML model. See \`docs/diagrams/README.md\` for rendering commands and evaluation notes.

---

# [Comment #3]() by [gerchowl]()

_Posted on February 24, 2026 at 06:55 PM_

## Diagram-as-code benchmark added

Reproduced the skill pipeline diagram (from issue-90, worktree:solve-and-pr) in **all 9 tools** evaluated in RFC-001:

| Format | Location | Render status |
|--------|----------|---------------|
| **YAML model** | `docs/diagrams/skill-pipeline.yaml` | SSoT — RFC-001 direction A |
| Mermaid | `skill-pipeline.mmd` | `mmdc` ✓ |
| D2 | `skill-pipeline.d2` | `d2` CLI ✓ |
| PlantUML | `skill-pipeline.puml` | `plantuml` (Java) ✓ |
| Graphviz | `skill-pipeline.dot` | `dot -Tsvg` ✓ |
| Fletcher | `skill-pipeline.typ` | `typst compile` ✓ (Libertinus Serif) |
| TikZ | `skill-pipeline.tex` | `lualatex` + `pdf2svg` ✓ |
| Pikchr | `skill-pipeline.pikchr` | Kroki API ✓ |
| Structurizr | `skill-pipeline.dsl` | `structurizr-cli export` → Mermaid → SVG ✓ |
| Excalidraw | `skill-pipeline.excalidraw` | JSON — open in excalidraw.com ✓ |

`scripts/render_diagram.py` emits Mermaid, D2, and DOT from the YAML model. See `docs/diagrams/README.md` for rendering commands and evaluation notes.

---

# [Comment #4]() by [gerchowl]()

_Posted on February 24, 2026 at 07:00 PM_

## Next: try alternative layouts

The current benchmark renders the pipeline as a **left-to-right linear chain** — this works for showing the overall flow but hides the real structure. Each skill namespace actually contains **parallel sub-skills** that fan out:

```
inception:*          issue:*          design:*       code:*           ci:*          pr:*         git:*
├─ explore           ├─ claim         ├─ brainstorm  ├─ tdd           ├─ check      ├─ create    └─ commit
├─ scope             ├─ create        └─ plan        ├─ execute       └─ fix        └─ post-merge
├─ architect         └─ triage                       ├─ review
└─ plan                                              ├─ verify
                                                     └─ debug
```

Plus the `worktree:*` namespace runs as an autonomous **parallel track** that wraps the interactive skills:

```
worktree:solve-and-pr → worktree:brainstorm → worktree:plan → worktree:execute → worktree:verify → worktree:pr
                                                                   ↕                    ↕
                                                          worktree:ci-check      worktree:ci-fix
                                                          worktree:ask
```

### Suggested follow-up layouts to benchmark

1. **Top-to-bottom flowchart with parallel lanes** — each namespace as a vertical swim lane, sub-skills as parallel nodes within each lane, flow going top-to-bottom across lanes
2. **Two-track diagram** — interactive (top) vs. autonomous/worktree (bottom) tracks sharing the same phase columns
3. **Nested groups with fan-out** — each `*:namespace` box expands to show its individual skills, edges connect at the group level

These layouts would stress-test each tool's **grouping**, **parallel node placement**, and **cross-group edge routing** — the exact capabilities where the tools diverge most. The current linear chain is the easy case every tool handles well.

### Which tools to re-test first

- **D2**: Has `grid-rows`/`grid-columns` for swim lanes — should handle layout 1 natively
- **Fletcher/Typst**: Full manual control via coordinate grid — can do any layout but requires more authoring effort
- **Mermaid**: Subgraphs support parallel nodes but layout is unpredictable — this is where it should struggle most
- **Structurizr**: Model-view separation means the same model can emit different view layouts — test multiple views from one `.dsl`

Refs: #113

