"""Scaffold-lint tests: two structural regressions the scaffold must never reship.

**Rule 1 — unshipped-path references** (#1046, #1056, #1062): a file scaffolded
into a consumer repo must not point at a repo path the scaffold does not ship, or
every consumer carries a dead pointer. Two deliberately conservative extractor
shapes, applied file-type by file-type:

* **bare ``docs/<path>.md`` tokens** — in workflow + composite-action YAML
  comments, ``flake.nix`` comments and ``ISSUE_TEMPLATE/*.yml`` body text (all
  code/config, no code spans), plus shipped ``docs/*.md`` prose *after* inline
  code spans are stripped; each must resolve inside the scaffold tree.
* **relative Markdown link targets** — in shipped ``docs/*.md`` and in agent
  ``.claude/skills/*/SKILL.md`` files; each resolves against the linking file's
  directory, so a skill's sibling ``../<skill>/SKILL.md`` links (which ship) pass
  and only refs to unshipped repo-root/devkit docs fail.

Extraction is intentionally narrow — #1057: "few false positives beat exhaustive
coverage." Absolute URLs, pure anchors and angle-bracket placeholders are exempt;
by-name ``docs/...`` mentions inside inline code spans (label text of an adjacent
absolute link) and the immutable ``.devcontainer/CHANGELOG.md`` mirror are out of
scope by construction, not by suppression. ``RULE1_ALLOWLIST`` is the documented
escape hatch for a deliberate exception and is empty by design.

**Rule 2 — non-default-ref checkout + local action** (#1034): a workflow job
that checks out a ref other than the one it was triggered on must not invoke a
local (``uses: ./...``) action. GitHub resolves local actions against the
*checked-out* workspace, so a job that pins a foreign branch may run against a
tree that does not carry the action yet — the sync-main-to-dev bootstrap
deadlock. Every current scaffold + devkit workflow is asserted clean, and the
rule predicate is unit-tested against the pre-#1034 pattern as a constructed
regression fixture.

Refs: #1057
"""

from __future__ import annotations

import re
from fnmatch import fnmatch
from pathlib import Path

import pytest
import yaml

# Repository root (tests/ -> repo root) and the consumer scaffold tree.
REPO_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = REPO_ROOT / "assets" / "workspace"


# --------------------------------------------------------------------------- #
# Rule 1 — unshipped-path references
# --------------------------------------------------------------------------- #

# Deliberate, documented exceptions to Rule 1, keyed by the exact reference
# string. Empty by design: the fixes (#1056, #1062) resolve the known instances.
#
# NOT walked, by construction: ``.devcontainer/CHANGELOG.md`` (the hook-synced
# mirror of the repo CHANGELOG). It is released history — immutable by policy —
# so its many by-name mentions of since-unshipped devkit docs (docs/MIGRATION.md,
# docs/NIX.md, ADRs, …) are out of scope and never rewritten. It lives outside
# every set below (it is not under ``docs/`` nor a workflow/action/flake/issue
# template), so it is excluded without needing an allowlist entry.
RULE1_ALLOWLIST: dict[str, str] = {}

_ABSOLUTE_URL = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*://")
# A bare repo-relative ``docs/....md`` path token, as written in a comment or in
# prose. The negative lookbehind keeps it from matching the same substring
# embedded in an absolute URL (``.../blob/main/docs/....md``) or a longer path.
_DOCS_TOKEN = re.compile(r"(?<![\w./-])docs/[A-Za-z0-9_./-]+\.md")
_MD_LINK = re.compile(r"\]\(([^)]+)\)")
# Inline code spans. A ``docs/....md`` name rendered as code is display text —
# typically the label of an adjacent absolute link (#1056) or a by-name mention,
# not a navigable pointer — so it is stripped before the shipped-doc prose scan,
# staying out of scope by construction (like the changelog history above).
_CODE_SPAN = re.compile(r"`[^`]*`")


def _scaffold_workflows() -> list[Path]:
    base = WORKSPACE / ".github" / "workflows"
    return sorted([*base.glob("*.yml"), *base.glob("*.yaml")])


def _scaffold_actions() -> list[Path]:
    return sorted((WORKSPACE / ".github" / "actions").rglob("action.yml"))


def _scaffold_issue_templates() -> list[Path]:
    base = WORKSPACE / ".github" / "ISSUE_TEMPLATE"
    return sorted([*base.glob("*.yml"), *base.glob("*.yaml")])


def _scaffold_flake() -> list[Path]:
    flake = WORKSPACE / "flake.nix"
    return [flake] if flake.exists() else []


def _scaffold_docs() -> list[Path]:
    return sorted((WORKSPACE / "docs").glob("*.md"))


def _scaffold_skills() -> list[Path]:
    return sorted((WORKSPACE / ".claude" / "skills").glob("*/SKILL.md"))


def _bare_token_violations(
    files: list[Path], *, strip_code_spans: bool
) -> list[tuple[Path, str]]:
    """Bare ``docs/....md`` tokens (comment/prose) that do not resolve."""
    out: list[tuple[Path, str]] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        if strip_code_spans:
            text = _CODE_SPAN.sub("", text)
        for token in _DOCS_TOKEN.findall(text):
            if token in RULE1_ALLOWLIST:
                continue
            if not (WORKSPACE / token).exists():
                out.append((path, token))
    return out


def _md_link_violations(files: list[Path]) -> list[tuple[Path, str]]:
    """Relative Markdown link targets that do not resolve in the scaffold.

    Targets resolve against the linking file's own directory, so a skill's
    sibling ``../<skill>/SKILL.md`` links (which ship) pass and only refs to
    unshipped repo-root/devkit docs fail. Angle-bracket placeholders such as
    ``](<url>)`` are template syntax, not paths, and are skipped.
    """
    out: list[tuple[Path, str]] = []
    for path in files:
        for target in _MD_LINK.findall(path.read_text(encoding="utf-8")):
            target = target.strip()
            base = target.split("#", 1)[0]
            if base == "" or target.startswith(("#", "mailto:")):
                continue
            if _ABSOLUTE_URL.match(target) or target in RULE1_ALLOWLIST:
                continue
            if "<" in target or ">" in target:
                continue
            if not (path.parent / base).exists():
                out.append((path, target))
    return out


def _rule1_violations() -> list[tuple[Path, str]]:
    # Comment/config bare tokens: workflow + composite-action YAML comments,
    # flake.nix comments and ISSUE_TEMPLATE body text carry no code spans, so
    # every bare docs/*.md token in them is a literal pointer.
    violations = _bare_token_violations(
        [
            *_scaffold_workflows(),
            *_scaffold_actions(),
            *_scaffold_flake(),
            *_scaffold_issue_templates(),
        ],
        strip_code_spans=False,
    )
    # Shipped-doc prose: strip inline code spans first (see _CODE_SPAN).
    violations += _bare_token_violations(_scaffold_docs(), strip_code_spans=True)
    # Markdown links in shipped docs and agent skills.
    violations += _md_link_violations([*_scaffold_docs(), *_scaffold_skills()])
    return violations


def test_scaffold_has_no_unshipped_path_references() -> None:
    """No scaffolded file points at a repo path the scaffold does not ship."""
    violations = _rule1_violations()
    assert not violations, (
        "scaffolded files reference paths absent from the scaffold "
        "(rewrite to an absolute https://github.com/vig-os/devkit/... URL, or "
        "add to RULE1_ALLOWLIST with a reason):\n"
        + "\n".join(f"  {p.relative_to(REPO_ROOT)} -> {ref}" for p, ref in violations)
    )


# --------------------------------------------------------------------------- #
# Rule 2 — non-default-ref checkout + local action
# --------------------------------------------------------------------------- #

ALL_WORKFLOWS = [
    p
    for base in (
        REPO_ROOT / ".github" / "workflows",
        WORKSPACE / ".github" / "workflows",
    )
    for p in sorted([*base.glob("*.yml"), *base.glob("*.yaml")])
]


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _on(doc: dict) -> object:
    # YAML 1.1 parses the bare ``on:`` key as the boolean ``True``.
    return doc.get("on", doc.get(True))


def _job_uses_local_action(job: dict) -> bool:
    return any(
        isinstance(s, dict) and str(s.get("uses", "")).startswith("./")
        for s in job.get("steps", []) or []
    )


def _checkout_refs(job: dict) -> list[str | None]:
    refs: list[str | None] = []
    for s in job.get("steps", []) or []:
        if isinstance(s, dict) and "actions/checkout" in str(s.get("uses", "")):
            refs.append((s.get("with") or {}).get("ref"))
    return refs


def _push_branches(on: object) -> set[str] | None:
    """Literal branch filters of a ``push`` trigger, else ``None``.

    ``None`` means the run's ref cannot be pinned statically (dispatch, PR,
    schedule, ``workflow_call``), so a static checkout ref cannot be proven
    foreign and is not flagged.
    """
    if not isinstance(on, dict):
        return None
    push = on.get("push")
    if not isinstance(push, dict):
        return None
    branches = push.get("branches")
    if not isinstance(branches, list):
        return None
    return {str(b) for b in branches}


def job_checks_out_foreign_ref_with_local_action(on: object, job: dict) -> bool:
    """True if a job runs a local action against a ref foreign to its trigger.

    The pre-#1034 shape: a ``push``-triggered job that pins a static branch ref
    other than the pushed branch and then invokes a local ``uses: ./...``
    action. Dynamic ``${{ ... }}`` refs (the run's own ref/SHA) are safe, as is
    the absence of an explicit ref (the triggering SHA).
    """
    if not _job_uses_local_action(job):
        return False
    branches = _push_branches(on)
    if branches is None:
        return False
    for ref in _checkout_refs(job):
        if ref is None or "${{" in ref:
            continue
        if not any(fnmatch(ref, pattern) for pattern in branches):
            return True
    return False


@pytest.mark.parametrize(
    "path", ALL_WORKFLOWS, ids=lambda p: str(p.relative_to(REPO_ROOT))
)
def test_no_local_action_on_foreign_ref(path: Path) -> None:
    """No current workflow job runs a local action on a foreign checkout ref."""
    doc = _load(path)
    if not isinstance(doc, dict):
        return
    on = _on(doc)
    jobs = doc.get("jobs") or {}
    offending = [
        name
        for name, job in jobs.items()
        if isinstance(job, dict)
        and job_checks_out_foreign_ref_with_local_action(on, job)
    ]
    assert not offending, (
        f"{path.relative_to(REPO_ROOT)} jobs {offending} check out a ref foreign "
        "to the trigger while invoking a local `uses: ./...` action (#1034): a "
        "local action resolves against the checked-out workspace, which may not "
        "carry it yet. Check out the triggering ref (drop `ref:` or use a "
        "run-scoped `${{ ... }}` expression)."
    )


def test_rule2_predicate_catches_pre_1034_pattern() -> None:
    """Regression fixture: the exact pre-#1034 sync-main-to-dev job shape.

    Gitflow-scoped by construction: the ``ref: dev`` + local-action shape is the
    gitflow ``sync-main-to-dev`` bridge, which exists only under the gitflow
    workflow model. A trunk scaffold (#1205) has no long-lived ``dev`` branch
    and copy-excludes that workflow, so this foreign-ref pattern cannot arise
    there — the fixture pins the predicate against the gitflow shape it guards.
    """
    on = {"push": {"branches": ["main"]}}
    job = {
        "steps": [
            {"uses": "actions/checkout@v4", "with": {"ref": "dev"}},
            {"uses": "./.github/actions/setup-env"},
        ]
    }
    assert job_checks_out_foreign_ref_with_local_action(on, job) is True


def test_rule2_predicate_allows_triggering_ref_checkout() -> None:
    """The #1034 fix: no explicit ref (triggering SHA) + local action is safe."""
    on = {"push": {"branches": ["main"]}}
    job = {
        "steps": [
            {"uses": "actions/checkout@v4"},
            {"uses": "./.github/actions/setup-env"},
        ]
    }
    assert job_checks_out_foreign_ref_with_local_action(on, job) is False
