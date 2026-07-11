---
type: issue
state: closed
created: 2026-06-30T16:50:45Z
updated: 2026-07-02T11:33:20Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devkit/issues/786
comments: 0
labels: feature, area:workspace, area:workflow, security
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:46.459Z
---

# [Issue 786]: [Establish an agent secret-management principle as a first-class repo standard](https://github.com/vig-os/devkit/issues/786)

## Summary

Establish **agent secret management** as a first-class, versioned principle of this repo — and one that propagates to consumers through the workspace template — rather than the single "No secrets" line that lives in the always-apply rules today.

## Why

This repo is agent-first: it ships agent scaffolding (`.claude/skills`, agent-models, agent-blocklist, rules) into every consumer via the workspace template, and agents operate here with powerful, outward-facing capabilities — running shells, fetching URLs, writing files, and posting to PRs/issues.

A secret pulled into an agent's context can leak through many vectors that the current one-liner under-specifies:

- committed into a file or `.env`,
- echoed into logs, command output, or a saved transcript,
- sent to an external service via a tool call (`curl`, an MCP server, a web request),
- pasted into a PR/issue comment or a diff,
- carried forward into a downstream consumer's scaffold.

The discipline an agent must follow around secrets deserves to be an explicit, shipped standard — versioned like the commit-message and changelog standards — not ad hoc.

## Proposal

Define an **Agent Secret Management** principle as a documented standard, wired into the always-apply rules and reflected in the workspace template so every consumer inherits it. At minimum it should cover:

- **Discovery & flagging** — on encountering a secret (in code, env, or output), flag it; never propagate, echo, or commit it.
- **Surfacing** — secrets reach agents only via approved channels (env / secret store / OIDC), never inline in prompts, configs, or committed files.
- **Redaction** — agents must scrub secret-shaped material from anything outward-facing: commits, PR/issue comments, logs, transcripts, and external tool calls.
- **Exfiltration guardrails** — no sending secret-bearing content to external services; treat arbitrary outbound (`curl | sh`, untrusted endpoints) as suspect.
- **Credential files** — never commit `.env`/key material; respect ignore rules; warn on discovery.
- **Propagation** — ship the principle to consumers through the workspace template (`.claude` rules), so the devkit's agent secret discipline is uniform downstream.

## Relationship to other work

This is the **agent behavior / governance** layer. It is distinct from — and composes with — the secret *plumbing* thread (sops-nix/age + OIDC) tracked separately: that issue is about how secrets are stored and delivered; this one is about how an agent is obligated to behave around them once they exist.

## Out of scope

- The secret-delivery plumbing/tooling (covered by the separate secrets-infra issue).
- Specific scanner/tool choices for enforcement (can be a follow-up).

## Acceptance criteria (sketch)

- [ ] A documented agent-secret-management principle exists in the repo.
- [ ] It is wired into the always-apply rules.
- [ ] It is reflected in the workspace template so consumers inherit it.
- [ ] (Optional) a hook/check that scans agent-authored, outward-facing output for secret-shaped material.

