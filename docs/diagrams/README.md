# Diagram-as-Code Benchmark

Reproduces the **skill pipeline** diagram (from issue #90) in all tools evaluated in
[RFC-001](../rfcs/RFC-001-2026-02-20-diagram-as-code-tooling.md).

## Source files

| Format | File | SSoT? |
|--------|------|-------|
| YAML model | `skill-pipeline.yaml` | Yes — defines components, edges, views |
| Mermaid | `skill-pipeline.mmd` | No — hand-crafted |
| D2 | `skill-pipeline.d2` | No — hand-crafted |
| PlantUML | `skill-pipeline.puml` | No — hand-crafted |
| Graphviz DOT | `skill-pipeline.dot` | No — hand-crafted |
| Fletcher/Typst | `skill-pipeline.typ` | No — hand-crafted |

## Rendering commands

```bash
# Graphviz DOT → SVG
dot -Tsvg docs/diagrams/skill-pipeline.dot -o docs/diagrams/skill-pipeline-graphviz.svg

# D2 → SVG
d2 docs/diagrams/skill-pipeline.d2 docs/diagrams/skill-pipeline-d2.svg

# PlantUML → SVG
plantuml -tsvg docs/diagrams/skill-pipeline.puml -o .

# Mermaid → SVG (requires @mermaid-js/mermaid-cli)
mmdc -i docs/diagrams/skill-pipeline.mmd -o docs/diagrams/skill-pipeline-mermaid.svg

# Typst / Fletcher → SVG
typst compile docs/diagrams/skill-pipeline.typ docs/diagrams/skill-pipeline-fletcher.svg

# From YAML model → Mermaid / D2 / DOT (then render with tool above)
python3 scripts/render_diagram.py --model docs/diagrams/skill-pipeline.yaml --format mermaid
python3 scripts/render_diagram.py --model docs/diagrams/skill-pipeline.yaml --format d2
python3 scripts/render_diagram.py --model docs/diagrams/skill-pipeline.yaml --format dot
```

## Tool comparison notes

| Criterion | Mermaid | D2 | Graphviz | PlantUML | Fletcher/Typst |
|-----------|---------|-----|----------|----------|----------------|
| GitHub inline rendering | Native | No | No | No | No |
| Composability / reuse | None | Imports + vars | None | `!include` macros | Full Typst modules |
| Layout quality | Unpredictable | Good (dagre) | Good (dot) | Acceptable | Manual control |
| CLI weight | Node.js | Go binary | C binary | Java + JAR | Rust binary |
| Typst integration | None | None | None | None | Native |
| License | MIT | MPL-2.0 | EPL-2.0 | GPL-3.0 | MIT |
| Authoring complexity | Low | Low | Medium | Low | Medium-High |

## Refs

- Issue: [#113](https://github.com/vig-os/devcontainer/issues/113)
- RFC: [`docs/rfcs/RFC-001-2026-02-20-diagram-as-code-tooling.md`](../rfcs/RFC-001-2026-02-20-diagram-as-code-tooling.md)
