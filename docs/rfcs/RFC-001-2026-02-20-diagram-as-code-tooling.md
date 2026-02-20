---
rfc: 001
date: 2026-02-20
title: Diagram-as-code tooling for the project
status: draft
authors:
  - Lars Gerchow (@gerchowl)
---

# RFC-001: Diagram-as-code tooling for the project

## Problem Statement

### Current situation

Mermaid is used ad-hoc in a handful of docs (`docs/RELEASE_CYCLE.md`, design templates, `inception:architect` skill). There is no deliberate choice about which diagramming tool(s) to use, when to use them, or how to make diagrams reusable across documents.

### Pain points

1. **No composability.** Mermaid has no imports, variables, or reusable components. Every diagram is a standalone block. Common visual patterns (node styles, color schemes, component shapes) are copy-pasted.
2. **Layout unpredictability.** Mermaid's automatic layout is fragile — small syntax changes can drastically alter the visual output. The ELK engine (better layouts) is unavailable on GitHub.
3. **No Typst integration.** The project already uses Typst, but diagrams live outside the Typst toolchain. This means separate rendering pipelines and no access to Typst's module system, fonts (Libertinus Serif), or styling.
4. **No manual editing path.** When auto-layout produces a poor result, there's no way to manually adjust node positions in Mermaid or PlantUML.
5. **No component library.** Skills, workflows, and architecture patterns are documented in multiple places but share no visual vocabulary.

### Who is affected

- **Documentation authors** — can't build on previous diagrams; start from scratch each time.
- **Architecture reviewers** — no consistent visual language across design documents.
- **Autonomous agents** — skills like `inception:architect` and `design:brainstorm` generate diagrams without a composable toolkit.

### What happens if we do nothing

Mermaid continues to be used sporadically. Diagram quality stays low. Complex architecture diagrams are avoided because the tooling can't handle them. When Typst adoption deepens, diagrams become the odd component that lives outside the Typst pipeline.

## Proposed Solution

<!-- To be filled during inception:scope -->

## Alternatives Considered

### Tools evaluated

#### Tier 1 — Strong fit

| Tool | Strengths | Weaknesses |
|---|---|---|
| **CeTZ + Fletcher** (Typst-native) | Native Typst integration, full composability via Typst's module system (imports, functions, packages), live preview, CLI renders to SVG/PNG, MIT/LGPL license, Fletcher abstracts node-and-edge diagrams | Pre-1.0 maturity, smaller ecosystem than Mermaid, no GitHub-native rendering |
| **D2** | Clean declarative syntax, imports/variables/composition, bidirectional Studio editor, multiple layout engines, Go binary (lightweight CI), MPL 2.0 | No GitHub-native rendering, TALA engine is commercial, smaller ecosystem |
| **Mermaid** | GitHub-native rendering (issues, PRs, wikis, markdown), zero tooling, broadest ecosystem, MIT license | No composability (no imports, no variables, no reusable components), unpredictable layouts, no manual editing |

#### Tier 2 — Niche fit

| Tool | Use case | Why not primary |
|---|---|---|
| **Kroki** | Unified rendering API for 30+ diagram formats, self-hostable | Meta-tool, not a language — doesn't address composability |
| **Structurizr DSL** | C4 architecture diagrams, model-view separation | Too narrow for general use, Java-based |

#### Tier 3 — Weak fit

| Tool | Why not |
|---|---|
| **TikZ** | LaTeX dependency when Typst is already in use; massive learning curve; slow compilation. CeTZ covers the same space natively. |
| **PlantUML** | GPL-3.0 license; Java runtime dependency; poor layout control; D2 covers the same space with lighter toolchain. |
| **Excalidraw** | Visual-first but exposes diagrams as code (JSON format, `ExcalidrawElementSkeleton` API, `mermaid-to-excalidraw` bridge). Scene data embeds in PNG/SVG metadata for round-trip editing. However: JSON coordinate diffs are noisy for code review, Mermaid bridge limited to flowcharts, and no native declarative *authoring* syntax — you either draw visually or generate JSON programmatically. |
| **Graphviz/DOT** | No reusable components; aging layout engine; D2 supersedes it. |
| **Pikchr** | Ultra-lightweight but no composability; too simple for architecture diagrams. |

### Tool maturity and GitHub activity

Data collected 2026-02-20.

| Tool | Version | Created | Last commit | Last release | Stars | Contributors | License |
|---|---|---|---|---|---|---|---|
| **Mermaid** | 11.12.3 | 2014-11 | 2026-02-16 | 2026-02-17 | 86.2k | 748 | MIT |
| **D2** | 0.7.1 | 2022-09 | 2025-10-14 | 2025-08-19 | 23.1k | 67 | MPL-2.0 |
| **Excalidraw** | 0.18.0 | 2020-01 | 2026-02-19 | 2025-03-11 | 117k | — | MIT |
| **PlantUML** | 1.2026.1 | 2010-11 | 2026-02-19 | 2026-01-18 | 12.7k | — | GPL-3.0 |
| **CeTZ** | 0.4.2 | 2023-04 | 2026-01-27 | 2025-09-07 | 1.6k | 46 | LGPL-3.0 |
| **Fletcher** | 0.5.8 | 2023-11 | 2025-08-03 | 2025-08 (tag) | 922 | 11 | MIT |
| **Kroki** | 0.30.0 | 2019-01 | 2026-02-19 | 2026-02-19 | 4.0k | — | MIT |
| **Pikchr** | — | — | — | — | — | — | BSD-like |

**Observations:**

- **Mermaid** is the most mature and actively maintained by a wide margin (1,700+ commits/year, 748 contributors, 86k stars). Releases are frequent (days-old).
- **D2** has strong adoption (23k stars) but development has slowed — last commit Oct 2025, last release Aug 2025. The 490 open issues suggest a backlog growing faster than the team can address.
- **CeTZ** is young (2023) but actively developed with 3 releases in 2025. The 1.6k stars are strong for a Typst package (Typst's own ecosystem is young). 46 contributors for a niche drawing library is healthy.
- **Fletcher** is the youngest tool (2023-11) with the smallest contributor base (11). Development pace is moderate — last commit Aug 2025. However, it builds on CeTZ, so its effective foundation is larger than its own repo suggests.
- **PlantUML** is the longest-lived (2010) and still actively committed to daily, but carries GPL-3.0 and a Java runtime.
- **Excalidraw** is massively popular (117k stars) but infrequent releases — the gap between v0.17.3 (2024-02) and v0.18.0 (2025-03) is over a year.
- **Kroki** is actively maintained with regular releases, most recently today (2026-02-19).

### Mermaid C4 and architecture diagram limitations

Mermaid offers two diagram types for infrastructure composition:

- **C4 diagrams** (`C4Context`, `C4Container`, `C4Component`, `C4Dynamic`, `C4Deployment`): Marked **experimental** — syntax subject to change. Missing sprites, tags, stereotypes, links, legend, custom shapes, and automatic layout. Open bugs include inability to create relations from boundaries to containers (#4864) and non-deterministic rendering (#6024).
- **Architecture diagrams** (`architecture-beta`): Newer (v11.1.0+). Supports groups, services, edges, junctions, and 200k+ iconify icons. Nestable groups via `in` keyword. But still has non-deterministic rendering, node overlap bugs (#6120), and no multi-edge from same node side.

**Neither type supports component reuse.** A template/reuse feature request (#1396) has been open since 2020 with no implementation. Every service, group, and edge must be redeclared per diagram. There is no `define`, `import`, `include`, variable, or macro system.

| Tool | Can you define a component once and reuse it? | Mechanism |
|---|---|---|
| **Mermaid** | No | None. Copy-paste per diagram. |
| **D2** | Yes | `imports` + `spread imports`. Define in a `.d2` file, import into any diagram. Variables for parameterization. |
| **CeTZ/Fletcher** | Yes | Typst functions: `#let component(name, ...) = { ... }`. Full language composability. |
| **PlantUML** | Partially | `!include`, `!define` macros. Preprocessor-level, fragile. |
| **Structurizr** | Yes | Model-view separation. Define model once, render multiple views. C4-only. |
| **Excalidraw** | Partially | Libraries of reusable visual elements (drag-and-drop). No declarative/text-based reuse. |

### Architecture direction: model-renderer separation

The evaluation surfaced a deeper question: rather than choosing *a diagram tool*, should the project separate the **semantic model** (components, relationships, properties) from the **rendering backend**?

```
┌──────────────────────────────────────────────────┐
│  Layer 1: SEMANTIC MODEL (SSoT)                  │
│  Components, relationships, properties           │
│  Format: YAML / TOML / SQL                       │
│  "Auth service connects to User DB via reads"    │
├──────────────────────────────────────────────────┤
│  Layer 2: VIEW DEFINITIONS                       │
│  Which components, which perspective, filters    │
│  "Show me the backend topology"                  │
├──────────────────────────────────────────────────┤
│  Layer 3: RENDERERS (pluggable)                  │
│  Mermaid (GitHub inline) | D2 (high-quality SVG) │
│  Fletcher/CeTZ (Typst docs) | Graphviz (graphs)  │
└──────────────────────────────────────────────────┘
```

#### Prior art

| Tool | Model format | View separation | Renderers | Limitation |
|---|---|---|---|---|
| **Structurizr** | Custom DSL / JSON | Yes — model once, multiple views | PlantUML, Mermaid, D2, Ilograph, native | C4-only; Java CLI; GPL (on-prem) |
| **Ilograph** | YAML resource tree | Yes — "perspectives" and "contexts" | Native only (interactive web) | Proprietary renderer, no export |
| **Bluefish** | Compound graph (JS) | Yes — composable relations | SVG (web) | Academic/research; JS-only |
| **LinkML** | YAML schema | Yes — schema to multiple outputs | JSON Schema, PlantUML, ER, YUML | Schema-focused, not general |

None provides a general-purpose "model once, render to Mermaid/D2/Fletcher/Graphviz."

#### Possible directions

**A. YAML/TOML model + Python renderers (recommended for exploration)**

A lightweight custom layer matching existing project patterns:

```yaml
# diagrams/model.yaml — SSoT
components:
  auth-service: { type: service, group: backend, icon: server }
  user-db:      { type: database, group: data, icon: database }
edges:
  - { from: auth-service, to: user-db, label: "reads/writes" }
views:
  backend-topology:
    filter: { group: backend }
    include_edges: true
```

```bash
python scripts/render_diagram.py --model diagrams/model.yaml --view backend-topology --format mermaid
python scripts/render_diagram.py --model diagrams/model.yaml --view backend-topology --format d2
python scripts/render_diagram.py --model diagrams/model.yaml --view backend-topology --format fletcher
```

- Pro: Fits existing project patterns (Python scripts, YAML/TOML config, `just` recipes). YAGNI — start with one renderer, add more. Easy for humans and agents to author.
- Con: Custom tool = maintenance. Per-renderer output tuning needed.

**B. SQL (SQLite) as model store**

Components and relationships stored relationally. Views are literally SQL queries (`SELECT ... WHERE group = 'backend'`). Queryable: "what depends on auth-service?" is a JOIN.

- Pro: Powerful for large graphs. Familiar tooling. Trivially versionable (DDL + seed).
- Con: Awkward authoring UX (INSERT statements). Overkill for < 50 components. Harder for agents.
- Migration path: YAML model can be loaded into SQLite when complexity warrants it.

**C. Adopt Structurizr for architecture, simpler tools for the rest**

Use existing model-view-renderer pattern where it works (C4). Don't reinvent.

- Pro: Production-ready, proven, exports to Mermaid/D2/PlantUML.
- Con: Java dependency. C4-scoped only. Doesn't solve general component reuse.

#### Excalidraw's code layer

Excalidraw deserves a nuance correction: it does expose diagrams as code. `.excalidraw` files are JSON with a well-documented schema (`type`, `version`, `elements[]`, `appState`, `files`). The `ExcalidrawElementSkeleton` API allows programmatic generation with minimal required properties (`type`, `x`, `y`). Most notably, **scene data can be embedded in exported PNG/SVG metadata** (`exportEmbedScene: true`), enabling round-trip editing — export a PNG, re-import it, and get the full editable scene back.

This makes Excalidraw viable as a *rendering target* in a model-renderer architecture: generate the JSON programmatically from a semantic model, export with embedded metadata, and retain editability. The weakness remains that the JSON format is coordinate-based (noisy diffs) and there's no human-friendly declarative authoring syntax.

### Evaluation criteria

| Criterion | Weight | Description |
|---|---|---|
| Reusable components | High | Define diagram building blocks once, compose everywhere |
| Declarative syntax simplicity | High | Text-first definition, readable diffs |
| Open-source (permissive license) | High | No GPL, no commercial dependencies for core workflow |
| Manual edit after declare | Medium | Ability to refine auto-layout visually |
| CI asset generation | Medium | CLI renders to SVG/PNG without heavy runtimes |
| GitHub rendering | Medium | Inline in issues/PRs (native or pre-rendered images) |
| Typst integration | High | Native to Typst or easily embedded |
| Learning curve | Medium | Accessible to contributors and autonomous agents |
| Diagram type breadth | Medium | Flowcharts, sequences, architecture, ER, state, etc. |
| Ecosystem / adoption | Low | Community size, plugins, tooling |
| Maturity / project health | Medium | Version stability, release cadence, contributor base, issue backlog health |

## Impact

### Beneficiaries

- Documentation authors get a composable diagram toolkit with reusable components.
- Architecture reviewers get a consistent visual language across designs.
- Autonomous agents get a declared diagramming standard they can generate against.
- The Typst pipeline gets native diagram support instead of external toolchain dependencies.

### Compatibility

- Breaking changes: No — this adds tooling, doesn't remove existing Mermaid usage.
- Migration path: Existing Mermaid diagrams can stay as-is or be migrated incrementally.
- Backward compatibility: Full.

### Risks

| Risk | Severity | Mitigation |
|---|---|---|
| CeTZ/Fletcher pre-1.0 stability | Medium | Both are actively maintained; pin versions; Typst itself is pre-1.0 |
| D2 TALA engine is commercial | Low | Free engines (dagre, ELK) cover most needs; TALA is optional |
| Multiple toolchain maintenance | Medium | Limit to 2 tools max; define clear "when to use which" guidelines |
| Learning curve for contributors | Low-Medium | Fletcher abstracts most complexity; provide templates/examples |

### Dependencies

- **External**: Typst CLI (already in use), potentially D2 CLI
- **Internal**: Documentation pipeline, CI workflows
- **Team**: Familiarity with Typst (already present)

## Open Questions

1. **Model-renderer separation vs. pick-a-tool:** Should we invest in a semantic model layer (YAML/TOML/SQL) with pluggable renderers, or is that premature? The model layer adds power (define once, render everywhere, queryable relationships) but also custom code to maintain.
2. **If model-renderer: what model format?** YAML for authoring simplicity? TOML for project consistency? SQL for queryability? Start with YAML and migrate to SQL later if the graph grows?
3. **Which renderers to support first?** Mermaid (GitHub inline) is the obvious first target. Fletcher/CeTZ (Typst docs) second. D2 and Excalidraw (with embedded scene metadata) as optional extras?
4. **Two-tool strategy vs. single tool:** If we don't build a model layer, should we use Mermaid for GitHub-inline + CeTZ/Fletcher for docs, or go all-in on one?
5. **Component library now vs. later?** Should we invest in reusable diagram components now, or let patterns emerge organically first?
6. **Excalidraw as render target:** Is the round-trip PNG-with-embedded-metadata workflow worth supporting for visual/manual editing?

## References

- Prior art: [text-to-diagram.com](https://text-to-diagram.com/) — side-by-side comparison of D2, Mermaid, PlantUML, Graphviz
- CeTZ docs: [cetz-package.github.io/docs](https://cetz-package.github.io/docs/)
- Fletcher docs: [typst.app/universe/package/fletcher](https://typst.app/universe/package/fletcher/)
- D2 docs: [d2lang.com](https://d2lang.com/)
- Mermaid docs: [mermaid.js.org](https://mermaid.js.org/)
- Kroki docs: [kroki.io](https://kroki.io/)
- Structurizr (model-view-renderer): [docs.structurizr.com](https://docs.structurizr.com/)
- Ilograph (multiperspective): [ilograph.com/docs](https://ilograph.com/docs/spec)
- Bluefish (declarative relations): [bluefishjs.org](https://bluefishjs.org/)
- Excalidraw element skeleton API: [docs.excalidraw.com](https://docs.excalidraw.com/docs/@excalidraw/excalidraw/api/excalidraw-element-skeleton)
- Excalidraw export with embedded scene: [docs.excalidraw.com/utils/export](https://docs.excalidraw.com/docs/@excalidraw/excalidraw/api/utils/export)
- Mermaid C4 limitations: [mermaid.js.org/syntax/c4](https://mermaid.js.org/syntax/c4.html)
- Mermaid architecture diagrams: [mermaid.js.org/syntax/architecture](https://mermaid.js.org/syntax/architecture)
- Existing Mermaid usage: `docs/RELEASE_CYCLE.md`, `.cursor/skills/inception:architect/SKILL.md`, `docs/templates/DESIGN.md`
