# Diagram-as-Code Benchmark

Reproduces the **skill pipeline** diagram (from issue #90) in all tools evaluated in
[RFC-001](../rfcs/RFC-001-2026-02-20-diagram-as-code-tooling.md).

## Source files

| Format | File | SSoT? | Render status |
|--------|------|-------|---------------|
| YAML model | `skill-pipeline.yaml` | Yes | SSoT — RFC-001 direction A |
| Mermaid | `skill-pipeline.mmd` | No | `mmdc` ✓ |
| D2 | `skill-pipeline.d2` | No | `d2` ✓ |
| PlantUML | `skill-pipeline.puml` | No | `plantuml` ✓ |
| Graphviz DOT | `skill-pipeline.dot` | No | `dot -Tsvg` ✓ |
| Fletcher/Typst | `skill-pipeline.typ` | No | `typst compile` ✓ (Libertinus Serif) |
| TikZ | `skill-pipeline.tex` | No | `lualatex` ✓ |
| Pikchr | `skill-pipeline.pikchr` | No | Kroki API ✓ |
| Structurizr DSL | `skill-pipeline.dsl` | No | `structurizr-cli export` → Mermaid ✓ |
| Excalidraw | `skill-pipeline.excalidraw` | No | Open in excalidraw.com ✓ |

## Rendering commands

```bash
# Mermaid → SVG (requires @mermaid-js/mermaid-cli)
mmdc -i docs/diagrams/skill-pipeline.mmd -o docs/diagrams/skill-pipeline-mermaid.svg

# D2 → SVG
d2 docs/diagrams/skill-pipeline.d2 docs/diagrams/skill-pipeline-d2.svg

# PlantUML → SVG (requires Java + PlantUML)
plantuml -tsvg docs/diagrams/skill-pipeline.puml -o .

# Graphviz DOT → SVG
dot -Tsvg docs/diagrams/skill-pipeline.dot -o docs/diagrams/skill-pipeline-graphviz.svg

# Typst / Fletcher → SVG
typst compile docs/diagrams/skill-pipeline.typ docs/diagrams/skill-pipeline-fletcher.svg

# TikZ → PDF → SVG (requires TeX Live + pdf2svg)
lualatex -output-directory=docs/diagrams docs/diagrams/skill-pipeline.tex
pdf2svg docs/diagrams/skill-pipeline.pdf docs/diagrams/skill-pipeline-tikz.svg

# Pikchr → SVG (via Kroki public API)
curl -s -X POST https://kroki.io/pikchr/svg \
  --data-binary @docs/diagrams/skill-pipeline.pikchr \
  -H "Content-Type: text/plain" \
  -o docs/diagrams/skill-pipeline-pikchr.svg

# Structurizr DSL → Mermaid → SVG
structurizr-cli export --workspace docs/diagrams/skill-pipeline.dsl --format mermaid --output /tmp
mmdc -i /tmp/structurizr-SkillPipeline.mmd -o docs/diagrams/skill-pipeline-structurizr.svg

# Excalidraw — open in browser
# Upload skill-pipeline.excalidraw at https://excalidraw.com

# From YAML model → Mermaid / D2 / DOT (then render with tool above)
python3 scripts/render_diagram.py --model docs/diagrams/skill-pipeline.yaml --format mermaid
python3 scripts/render_diagram.py --model docs/diagrams/skill-pipeline.yaml --format d2
python3 scripts/render_diagram.py --model docs/diagrams/skill-pipeline.yaml --format dot
```

## Tool comparison notes

| Criterion | Mermaid | D2 | Graphviz | PlantUML | Fletcher | TikZ | Pikchr | Structurizr | Excalidraw |
|-----------|---------|-----|----------|----------|----------|------|--------|-------------|------------|
| GitHub inline | Native | No | No | No | No | No | No | No | No |
| Composability | None | Imports+vars | None | `!include` | Full Typst | `\newcommand` | None | Model-view | Libraries |
| Layout quality | Unpredictable | Good | Good | Acceptable | Manual | Manual | Acceptable | Auto LR | Manual |
| CLI weight | Node.js | Go binary | C binary | Java+JAR | Rust binary | TeX Live | C binary | Java | Browser |
| Typst integration | None | None | None | None | Native | None | None | None | None |
| License | MIT | MPL-2.0 | EPL-2.0 | GPL-3.0 | MIT | LPPL | BSD | Apache-2.0 | MIT |
| Authoring complexity | Low | Low | Medium | Low | Medium-High | High | Low | Medium | Visual |
| Diff readability | Good | Good | Good | Good | Good | Good | Good | Good | Poor (JSON) |

## Refs

- Issue: [#113](https://github.com/vig-os/devcontainer/issues/113)
- RFC: [`docs/rfcs/RFC-001-2026-02-20-diagram-as-code-tooling.md`](../rfcs/RFC-001-2026-02-20-diagram-as-code-tooling.md)
