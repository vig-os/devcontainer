---
type: issue
state: open
created: 2026-01-28T20:41:51Z
updated: 2026-01-29T09:28:46Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/32
comments: 3
labels: none
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-01-29T09:44:20.395Z
---

# [Issue 32]: [Question: Was the dev branch intentionally removed?](https://github.com/vig-os/devcontainer/issues/32)

## Question

@c-vigo Was there a particular reason the `dev` branch was removed from the repository?

I noticed when trying to pull that the `origin/dev` branch no longer exists on the remote. Several other branches were also cleaned up:
- `origin/dev`
- `origin/c-vigo/issue1`
- `origin/gerchowl/issue8`
- `origin/revert-6-dev`
- `origin/revert-fix`

Just want to confirm if this was intentional and what branches working on for dev / pre-release?
---

# [Comment #1]() by [c-vigo]()

_Posted on January 29, 2026 at 07:59 AM_

I wanted to bring `dev`  up to date with `main` but forgot to re-create it. For the other branches, I did some clean-up, yeah.

We should establish clear rules on these branches and put them into workflows. I have also become more appreciative of the "release" branches where one can fully test before merging. To be discussed when you are back. For now, we keep `dev` as the main development branch with topic branches if necessary.

---

# [Comment #2]() by [gerchowl]()

_Posted on January 29, 2026 at 09:23 AM_

Sounds good to me.
I’d even go so far as to name it
rc-X.Y.Z for clarity and delete after merge.
So dev could also be in a ‘broken state’ and or continue development of other features while rc- gets reviewed?!

> On Jan 29, 2026, at 08:59, Carlos Vigo ***@***.***> wrote:
> 
> 
> c-vigo
>  left a comment 
> (vig-os/devcontainer#32)
>  <https://github.com/vig-os/devcontainer/issues/32#issuecomment-3816072687>
> I wanted to bring dev up to date with main but forgot to re-create it. For the other branches, I did some clean-up, yeah.
> 
> We should establish clear rules on these branches and put them into workflows. I have also become more appreciative of the "release" branches where one can fully test before merging. To be discussed when you are back. For now, we keep dev as the main development branch with topic branches if necessary.
> 
> —
> Reply to this email directly, view it on GitHub <https://github.com/vig-os/devcontainer/issues/32#issuecomment-3816072687>, or unsubscribe <https://github.com/notifications/unsubscribe-auth/AHCAU2INWB6PWMVIKM53JRT4JG4XXAVCNFSM6AAAAACTHGEGPOVHI2DSMVQWIX3LMV43OSLTON2WKQ3PNVWWK3TUHMZTQMJWGA3TENRYG4>.
> You are receiving this because you authored the thread.
> 



---

# [Comment #3]() by [c-vigo]()

_Posted on January 29, 2026 at 09:28 AM_

Agree, but after release I'd argue that a release branch should be actually kept forever, so that one can always apply a fix to a release and bump it.
I will open another issue with a proposal on:
- Branch structure and policy
- Setup to actually enforce it by default through GitHub rules directly created by the devcontainer

