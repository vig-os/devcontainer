---
type: issue
state: open
created: 2026-02-20T13:03:35Z
updated: 2026-02-20T13:05:29Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/113
comments: 1
labels: feature, area:workflow, area:docs, effort:large, semver:minor
assignees: gerchowl
milestone: none
projects: none
relationship: none
synced: 2026-02-20T13:17:14.457Z
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

