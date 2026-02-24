#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge
#set page(width: auto, height: auto, margin: 1em)
#set text(font: "Libertinus Serif", size: 10pt)

#let phase-box(body, fill-color) = rect(
  fill: fill-color,
  stroke: luma(180),
  radius: 4pt,
  inset: 8pt,
  body,
)

#let skill-node(label, phase: none) = {
  let content = if phase != none {
    align(center)[#text(weight: "bold", label) \ #text(size: 8pt, style: "italic", "(" + phase + ")")]
  } else {
    align(center, text(weight: "bold", label))
  }
  content
}

#diagram(
  spacing: (12mm, 10mm),
  node-stroke: luma(160),
  node-fill: white,
  node-inset: 6pt,
  edge-stroke: luma(120),

  // Inception Phase
  node((0, 0), skill-node("Signal"), shape: fletcher.shapes.ellipse, fill: rgb("#FFFDE7"), name: <signal>),
  node((1, 0), skill-node("inception:explore", phase: "diverge"), fill: rgb("#E8F5E9"), name: <explore>),
  node((2, 0), skill-node("inception:scope", phase: "converge"), fill: rgb("#E8F5E9"), name: <scope>),
  node((3, 0), skill-node("inception:architect", phase: "evaluate"), fill: rgb("#E8F5E9"), name: <architect>),
  node((4, 0), skill-node("inception:plan", phase: "decompose"), fill: rgb("#E8F5E9"), name: <plan>),

  // Development Phase
  node((5, 0), skill-node("design:brainstorm"), fill: rgb("#E3F2FD"), name: <brainstorm>),
  node((6, 0), skill-node("issue:*"), fill: rgb("#E3F2FD"), name: <issue>),
  node((7, 0), skill-node("design:*"), fill: rgb("#E3F2FD"), name: <design>),
  node((8, 0), skill-node("code:*"), fill: rgb("#E3F2FD"), name: <code>),

  // Delivery Phase
  node((9, 0), skill-node("git:*"), fill: rgb("#FFF3E0"), name: <git>),
  node((10, 0), skill-node("ci:*"), fill: rgb("#FFF3E0"), name: <ci>),
  node((11, 0), skill-node("pr:*"), fill: rgb("#FFF3E0"), name: <pr>),

  // Edges
  edge(<signal>, <explore>, "->"),
  edge(<explore>, <scope>, "->"),
  edge(<scope>, <architect>, "->"),
  edge(<architect>, <plan>, "->"),
  edge(<plan>, <brainstorm>, "->"),
  edge(<brainstorm>, <issue>, "->"),
  edge(<issue>, <design>, "->"),
  edge(<design>, <code>, "->"),
  edge(<code>, <git>, "->"),
  edge(<git>, <ci>, "->"),
  edge(<ci>, <pr>, "->"),

  // Phase labels
  node(enclose: (<signal>, <plan>), snap: -1, inset: 12pt,
    align(center, text(size: 8pt, weight: "bold", fill: rgb("#388E3C"), "Inception Phase")),
    stroke: rgb("#388E3C") + 0.5pt, fill: rgb("#E8F5E9").transparentize(80%), corner-radius: 6pt),
  node(enclose: (<brainstorm>, <code>), snap: -1, inset: 12pt,
    align(center, text(size: 8pt, weight: "bold", fill: rgb("#1565C0"), "Development Phase")),
    stroke: rgb("#1565C0") + 0.5pt, fill: rgb("#E3F2FD").transparentize(80%), corner-radius: 6pt),
  node(enclose: (<git>, <pr>), snap: -1, inset: 12pt,
    align(center, text(size: 8pt, weight: "bold", fill: rgb("#E65100"), "Delivery Phase")),
    stroke: rgb("#E65100") + 0.5pt, fill: rgb("#FFF3E0").transparentize(80%), corner-radius: 6pt),
)
