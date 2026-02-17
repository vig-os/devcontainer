---
type: issue
state: open
created: 2026-02-17T19:44:31Z
updated: 2026-02-17T19:44:31Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/61
comments: 0
labels: feature
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-17T19:44:50.092Z
---

# [Issue 61]: [Add agent-friendly issue templates, changelog rule, and PR template enhancements](https://github.com/vig-os/devcontainer/issues/61)

## Description

Add new issue templates, a Cursor rule for changelog updates, and enhance the PR template to close the agent workflow loop — ensuring coding agents (Cursor, Copilot, etc.) can properly handle commits, changelog entries, and pull requests end-to-end.

## Problem Statement

Currently, coding agents have no guidance on:
- **When and how to update CHANGELOG.md** — the contributing guide documents this, but agents don't read it unless instructed. There is no Cursor rule for changelog updates.
- **What changelog category to use** — issue templates don't signal whether a change is "Added", "Fixed", "Changed", etc.
- **Structured inputs for common work types** — refactoring, documentation, and CI/build changes all funnel through the generic "Task" template, losing important context (scope boundaries, invariants, target workflows).
- **Blank issue prevention** — without a `config.yml`, users can bypass all structured templates.

## Proposed Solution

### 1. New Cursor rule: `.cursor/rules/changelog.mdc` (always applied)
- When to update CHANGELOG.md (which commit types, when to skip)
- Where to update (only `## Unreleased`, correct category heading)
- Entry format (bold title, issue link, sub-bullets)
- Relationship to the issue template's Changelog Category field

### 2. Changelog Category dropdown on all issue templates
- Added to `bug_report.yml` (default: Fixed), `feature_request.yml` (default: Added), `task.yml` (full list)
- Gives agents a direct signal at issue-read time

### 3. New issue templates
- **`refactor.yml`** — files in scope, out of scope, invariants/constraints, acceptance criteria
- **`documentation.yml`** — encodes `docs/templates/` + `just docs` workflow, target files, doc type
- **`ci_build.yml`** — target workflows/actions, trigger types, release pipeline impact

### 4. Template chooser: `.github/ISSUE_TEMPLATE/config.yml`
- Disables blank issues
- Links to project documentation

### 5. Enhanced PR template
- New **Changelog Entry** section (paste the actual entry for review)
- Added "CI / Build change" to type of change options
- Updated checklist wording to reference `docs/templates/` and `just docs`

## Acceptance Criteria

- [ ] `.cursor/rules/changelog.mdc` created and always applied
- [ ] `changelog-category` dropdown added to `bug_report.yml`, `feature_request.yml`, `task.yml`
- [ ] `config.yml` template chooser created
- [ ] `refactor.yml`, `documentation.yml`, `ci_build.yml` issue templates created
- [ ] `pull_request_template.md` enhanced with Changelog Entry section
- [ ] CHANGELOG.md updated under `## Unreleased / ### Added`
