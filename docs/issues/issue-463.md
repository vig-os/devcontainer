---
type: issue
state: closed
created: 2026-03-27T10:12:51Z
updated: 2026-03-27T17:09:35Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/463
comments: 2
labels: none
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-28T04:26:13.447Z
---

# [Issue 463]: [[CHORE] Prune stale RC and sha256 tags from GHCR](https://github.com/vig-os/devcontainer/issues/463)

### Question

@c-vigo Should we prune the stale RC tags (and orphaned `sha256-*` tags) from `ghcr.io/vig-os/devcontainer`?

### Current State

The GHCR registry currently has **100 tags**, broken down as:

| Category | Count | Notes |
|----------|-------|-------|
| Release tags | 12 | `0.1`, `0.2.0`, `0.2.1`, `0.3.0`, `0.3.1` (+ arch variants) |
| `latest` | 1 | |
| RC tags | 65 | `0.3.0-rc1` through `0.3.0-rc3`, `0.3.1-rc1` through `0.3.1-rc19` (+ arch variants) |
| `sha256-*` tags | 22 | Orphaned manifest digests |

Both `0.3.0` and `0.3.1` have been released as final versions, so all 65 RC tags are stale. The 22 `sha256-*` tags appear to be orphaned intermediate manifests.

### Context

Issue #172 originally scoped automated RC cleanup as part of the release workflow, but the cleanup step was never implemented — only a manual cleanup note exists in the rollback failure message (line 1527 of `release.yml`).

### Proposal

1. **One-time manual prune** of all `*-rc*` and orphaned `sha256-*` tags
2. **Automate cleanup** as a post-release step (as originally planned in #172) so this doesn't accumulate again

Happy to take this on if you agree it should be done.
---

# [Comment #1]() by [c-vigo]()

_Posted on March 27, 2026 at 11:27 AM_

@gerchowl agree. I would make it part of the [`promote-release.yml`](https://github.com/vig-os/devcontainer/blob/dev/.github/workflows/promote-release.yml) workflow. The question remains what to do with GitHub tags as well. In the end they are just that, a tag, the underlying SHA will remain valid forever, and the only tag that must always remain is the final one (which is anyway immutable since it is linked to a release). What do you think?

---

# [Comment #2]() by [gerchowl]()

_Posted on March 27, 2026 at 12:06 PM_

Kill em all, except the final one =) only one that counts once released.

> On Mar 27, 2026, at 12:27, Carlos Vigo ***@***.***> wrote:
> 
> 
> c-vigo
>  left a comment 
> (vig-os/devcontainer#463)
>  <https://github.com/vig-os/devcontainer/issues/463#issuecomment-4141938912>
> @gerchowl <https://github.com/gerchowl> agree. I would make it part of the promote-release.yml <https://github.com/vig-os/devcontainer/blob/dev/.github/workflows/promote-release.yml> workflow. The question remains what to do with GitHub tags as well. In the end they are just that, a tag, the underlying SHA will remain valid forever, and the only tag that must always remain is the final one (which is anyway immutable since it is linked to a release). What do you think?
> 
> —
> Reply to this email directly, view it on GitHub <https://github.com/vig-os/devcontainer/issues/463?email_source=notifications&email_token=AHCAU2NVCTMV5XELBNMT62L4SZQTNA5CNFSNUABFM5UWIORPF5TWS5BNNB2WEL2JONZXKZKDN5WW2ZLOOQXTIMJUGE4TGOBZGEZKM4TFMFZW63VHNVSW45DJN5XKKZLWMVXHJLDGN5XXIZLSL5RWY2LDNM#issuecomment-4141938912>, or unsubscribe <https://github.com/notifications/unsubscribe-auth/AHCAU2I5MRPQDHKHXCEG5X34SZQTNAVCNFSM6AAAAACXBXCUMKVHI2DSMVQWIX3LMV43OSLTON2WKQ3PNVWWK3TUHM2DCNBRHEZTQOJRGI>.
> You are receiving this because you were mentioned.
> 



