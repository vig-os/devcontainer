#!/usr/bin/env python3
"""Render diagram from YAML model to Mermaid, D2, or Graphviz DOT.

Usage:
    python scripts/render_diagram.py --model docs/diagrams/skill-pipeline.yaml --format mermaid
    python scripts/render_diagram.py --model docs/diagrams/skill-pipeline.yaml --format d2
    python scripts/render_diagram.py --model docs/diagrams/skill-pipeline.yaml --format dot
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None


def load_model(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise SystemExit("PyYAML required: pip install pyyaml")
    with path.open() as f:
        return yaml.safe_load(f)


GROUP_STYLES = {
    "inception": {
        "mermaid_class": "inception",
        "d2_fill": "#E8F5E9",
        "dot_fill": "#E8F5E9",
    },
    "development": {
        "mermaid_class": "development",
        "d2_fill": "#E3F2FD",
        "dot_fill": "#E3F2FD",
    },
    "delivery": {
        "mermaid_class": "delivery",
        "d2_fill": "#FFF3E0",
        "dot_fill": "#FFF3E0",
    },
}


def render_mermaid(model: dict[str, Any]) -> str:
    lines = ["graph LR"]
    components = model["components"]
    edges = model["edges"]

    groups: dict[str, list[str]] = {}
    for cid, comp in components.items():
        g = comp.get("group", "default")
        groups.setdefault(g, []).append(cid)

    for gname, cids in groups.items():
        lines.append(f"    subgraph {gname}[{gname.title()} Phase]")
        for cid in cids:
            comp = components[cid]
            label = comp["label"]
            phase = comp.get("phase", "")
            display = f"{label}\\n({phase})" if phase else label
            if comp.get("type") == "trigger":
                lines.append(f'        {cid}(("{display}"))')
            else:
                lines.append(f'        {cid}["{display}"]')
        lines.append("    end")

    for edge in edges:
        lines.append(f"    {edge['from']} --> {edge['to']}")

    lines.extend(
        [
            "",
            "    classDef inception fill:#E8F5E9,stroke:#388E3C",
            "    classDef development fill:#E3F2FD,stroke:#1565C0",
            "    classDef delivery fill:#FFF3E0,stroke:#E65100",
        ]
    )

    return "\n".join(lines) + "\n"


def render_d2(model: dict[str, Any]) -> str:
    lines = [f"title: {model['title']}", "direction: right", ""]
    components = model["components"]
    edges = model["edges"]

    groups: dict[str, list[str]] = {}
    for cid, comp in components.items():
        g = comp.get("group", "default")
        groups.setdefault(g, []).append(cid)

    for gname, cids in groups.items():
        style = GROUP_STYLES.get(gname, {})
        fill = style.get("d2_fill", "#FFFFFF")
        lines.append(f"{gname}: {gname.title()} Phase {{")
        lines.append(f'  style.fill: "{fill}"')
        for cid in cids:
            comp = components[cid]
            label = comp["label"]
            phase = comp.get("phase", "")
            display = f"{label}\\n({phase})" if phase else label
            if comp.get("type") == "trigger":
                lines.append(f"  {cid}: {display} {{ shape: oval }}")
            elif comp.get("type") == "skill":
                lines.append(f"  {cid}: {display} {{ shape: rectangle }}")
            else:
                lines.append(f"  {cid}: {display} {{ shape: rectangle }}")
        lines.append("}")
        lines.append("")

    for edge in edges:
        src = edge["from"]
        dst = edge["to"]
        src_group = components[src].get("group", "default")
        dst_group = components[dst].get("group", "default")
        lines.append(f"{src_group}.{src} -> {dst_group}.{dst}")

    return "\n".join(lines) + "\n"


def render_dot(model: dict[str, Any]) -> str:
    lines = [
        f'digraph "{model["title"]}" {{',
        "    rankdir=LR;",
        '    node [fontname="Helvetica" fontsize=11 style=filled];',
        '    edge [fontname="Helvetica" fontsize=9];',
        "",
    ]
    components = model["components"]
    edges = model["edges"]

    groups: dict[str, list[str]] = {}
    for cid, comp in components.items():
        g = comp.get("group", "default")
        groups.setdefault(g, []).append(cid)

    for gname, cids in groups.items():
        style = GROUP_STYLES.get(gname, {})
        fill = style.get("dot_fill", "#FFFFFF")
        lines.append(f"    subgraph cluster_{gname} {{")
        lines.append(f'        label="{gname.title()} Phase";')
        lines.append(f'        style=filled; color="{fill}";')
        for cid in cids:
            comp = components[cid]
            label = comp["label"]
            phase = comp.get("phase", "")
            display = f"{label}\\n({phase})" if phase else label
            if comp.get("type") == "trigger":
                lines.append(
                    f'        {cid.replace("-", "_")} [label="{display}" shape=oval fillcolor="#FFFDE7"];'
                )
            else:
                lines.append(
                    f'        {cid.replace("-", "_")} [label="{display}" shape=box fillcolor=white];'
                )
        lines.append("    }")
        lines.append("")

    for edge in edges:
        src = edge["from"].replace("-", "_")
        dst = edge["to"].replace("-", "_")
        lines.append(f"    {src} -> {dst};")

    lines.append("}")
    return "\n".join(lines) + "\n"


RENDERERS = {
    "mermaid": render_mermaid,
    "d2": render_d2,
    "dot": render_dot,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Render YAML diagram model")
    parser.add_argument("--model", required=True, type=Path, help="Path to YAML model")
    parser.add_argument("--format", required=True, choices=RENDERERS.keys(), dest="fmt")
    parser.add_argument("--output", type=Path, help="Output path (default: stdout)")
    args = parser.parse_args()

    model = load_model(args.model)
    result = RENDERERS[args.fmt](model)

    if args.output:
        args.output.write_text(result)
        print(f"Wrote {args.output}", file=sys.stderr)
    else:
        print(result, end="")


if __name__ == "__main__":
    main()
