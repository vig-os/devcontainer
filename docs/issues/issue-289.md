---
type: issue
state: open
created: 2026-03-13T10:56:28Z
updated: 2026-03-13T10:56:28Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/289
comments: 0
labels: chore, priority:medium, area:ci, effort:small
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-14T04:15:55.879Z
---

# [Issue 289]: [[CHORE] Add source run metadata to smoke-test dispatch payload for downstream reporting](https://github.com/vig-os/devcontainer/issues/289)

## Chore Type
CI / Build change

## Description
Increase `repository_dispatch` payload metadata sent by `release.yml` so the downstream smoke-test workflow can report traceable source context (origin repo/workflow run) and optionally post completion status back.

## Acceptance Criteria
- [ ] `release.yml` dispatch includes metadata beyond `tag` (at minimum source repo and source run URL/ID).
- [ ] Receiver workflow consumes metadata and logs it in summary output.
- [ ] Receiver can construct a deterministic source run link from payload/context.
- [ ] A follow-up mechanism is defined for downstream completion reporting (e.g. dispatch/status callback, issue/pr comment, or check update), with chosen approach documented.
- [ ] Backward compatibility is preserved if older payloads only include `tag`.

## Implementation Notes
- Sender: `.github/workflows/release.yml` (`gh api .../dispatches`)
- Receiver template: `assets/smoke-test/.github/workflows/repository-dispatch.yml`
- Candidate payload keys:
  - `client_payload[source_repo]`
  - `client_payload[source_run_id]`
  - `client_payload[source_run_url]`
  - optional correlation key for callback/reporting
- Keep validation tolerant: required `tag`, optional metadata keys.

## Related Issues
Related to #284
Related to #169

## Priority
Medium

## Changelog Category
No changelog needed

## Additional Context
Current flow only sends `client_payload.tag`, which limits end-to-end traceability and makes completion reporting from downstream workflows harder.
