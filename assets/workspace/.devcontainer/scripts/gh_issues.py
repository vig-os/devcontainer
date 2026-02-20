#!/usr/bin/env python3
"""Display open GitHub issues and pull requests in rich tables."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rich.table import Table


def _fetch_issues() -> list[dict]:
    result = subprocess.run(
        [
            "gh",
            "issue",
            "list",
            "--state",
            "open",
            "--limit",
            "200",
            "--json",
            "number,title,state,assignees,labels,milestone",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


_LINKED_BRANCHES_QUERY = """
{
  repository(owner: "%s", name: "%s") {
    issues(states: OPEN, first: 100) {
      nodes {
        number
        linkedBranches(first: 5) {
          nodes { ref { name } }
        }
      }
    }
  }
}
"""


def _fetch_linked_branches() -> dict[int, str]:
    """Return {issue_number: branch_name} for issues with a linked branch."""
    owner_result = subprocess.run(
        ["gh", "repo", "view", "--json", "owner,name"],
        capture_output=True,
        text=True,
        check=True,
    )
    repo_info = json.loads(owner_result.stdout)
    query = _LINKED_BRANCHES_QUERY % (repo_info["owner"]["login"], repo_info["name"])

    result = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={query}"],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(result.stdout)
    mapping: dict[int, str] = {}
    for node in data["data"]["repository"]["issues"]["nodes"]:
        branches = [
            b["ref"]["name"]
            for b in node["linkedBranches"]["nodes"]
            if b.get("ref") and b["ref"].get("name")
        ]
        if branches:
            mapping[node["number"]] = branches[0]
    return mapping


LABEL_STYLES: dict[str, str] = {
    "priority:critical": "bold red",
    "priority:high": "red",
    "priority:medium": "yellow",
    "priority:low": "dim",
    "priority:backlog": "dim italic",
    "effort:small": "green",
    "effort:medium": "yellow",
    "effort:large": "red",
    "semver:major": "bold red",
    "semver:minor": "yellow",
    "semver:patch": "green",
}

TYPE_STYLES: dict[str, str] = {
    "feature": "cyan",
    "bug": "bold red",
    "discussion": "bright_magenta",
    "chore": "dim",
}

AREA_STYLE = "blue"


def _styled(value: str, style: str) -> str:
    return f"[{style}]{value}[/]"


def _extract_label(labels: list[dict], prefix: str) -> str:
    for lbl in labels:
        name = lbl["name"]
        if name.startswith(prefix):
            val = name[len(prefix) :]
            style = LABEL_STYLES.get(name, "dim")
            return _styled(val, style)
    return ""


def _extract_type(labels: list[dict]) -> str:
    for lbl in labels:
        name = lbl["name"]
        if name in TYPE_STYLES:
            return _styled(name, TYPE_STYLES[name])
    return ""


def _extract_scope(labels: list[dict]) -> str:
    scopes = []
    for lbl in labels:
        name = lbl["name"]
        if name.startswith("area:"):
            scopes.append(_styled(name[5:], AREA_STYLE))
    return ", ".join(scopes)


_TITLE_PREFIX_RE = re.compile(r"^\[(FEATURE|TASK|BUG|DISCUSSION|CHORE)\]\s*")


def _clean_title(title: str) -> str:
    return _TITLE_PREFIX_RE.sub("", title)


def _format_assignees(assignees: list[dict]) -> str:
    if not assignees:
        return "[dim]—[/]"
    return ", ".join(f"[bright_white]{a['login']}[/]" for a in assignees)


def _build_cross_refs(
    branches: dict[int, str],
    prs: list[dict],
) -> tuple[dict[int, int], dict[int, list[int]]]:
    """Build issue↔PR cross-references via matching branch names.

    Returns (issue_to_pr, pr_to_issues) mappings.
    """
    branch_to_issue = {branch: num for num, branch in branches.items()}
    issue_to_pr: dict[int, int] = {}
    pr_to_issues: dict[int, list[int]] = {}
    for pr in prs:
        head = pr["headRefName"]
        issue_num = branch_to_issue.get(head)
        if issue_num is not None:
            issue_to_pr[issue_num] = pr["number"]
            pr_to_issues.setdefault(pr["number"], []).append(issue_num)
    return issue_to_pr, pr_to_issues


def _build_table(
    title: str,
    issues: list[dict],
    branches: dict[int, str],
    issue_to_pr: dict[int, int],
) -> Table:
    from rich.table import Table

    table = Table(
        title=title,
        title_style="bold",
        show_lines=False,
        pad_edge=True,
        expand=True,
        border_style="dim",
        title_justify="left",
    )
    table.add_column("#", style="bold cyan", no_wrap=True, justify="right", width=4)
    table.add_column("Type", no_wrap=True, width=7)
    table.add_column("Title", no_wrap=True, overflow="ellipsis", ratio=1)
    table.add_column("Assignee", no_wrap=True, max_width=16)
    table.add_column(
        "Branch", style="dim", no_wrap=True, overflow="ellipsis", max_width=24
    )
    table.add_column("PR", no_wrap=True, justify="right", width=4)
    table.add_column("Prio", no_wrap=True, justify="center", width=7)
    table.add_column("Scope", no_wrap=True, width=10)
    table.add_column("Effort", no_wrap=True, justify="center", width=6)
    table.add_column("SemVer", no_wrap=True, justify="center", width=5)

    for issue in sorted(issues, key=lambda i: i["number"]):
        labels = issue.get("labels", [])
        branch = branches.get(issue["number"], "")
        pr_num = issue_to_pr.get(issue["number"])
        pr_cell = _styled(f"#{pr_num}", "green") if pr_num else ""
        table.add_row(
            str(issue["number"]),
            _extract_type(labels),
            _clean_title(issue["title"]),
            _format_assignees(issue["assignees"]),
            branch,
            pr_cell,
            _extract_label(labels, "priority:"),
            _extract_scope(labels),
            _extract_label(labels, "effort:"),
            _extract_label(labels, "semver:"),
        )
    return table


def _fetch_prs() -> list[dict]:
    result = subprocess.run(
        [
            "gh",
            "pr",
            "list",
            "--state",
            "open",
            "--limit",
            "100",
            "--json",
            "number,title,author,isDraft,reviewDecision,"
            "baseRefName,headRefName,additions,deletions,changedFiles,"
            "labels,milestone,createdAt",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


REVIEW_STYLES: dict[str, tuple[str, str]] = {
    "APPROVED": ("green", "approved"),
    "CHANGES_REQUESTED": ("red", "changes"),
    "REVIEW_REQUIRED": ("yellow", "pending"),
}


def _build_pr_table(
    title: str,
    prs: list[dict],
    pr_to_issues: dict[int, list[int]],
) -> Table:
    from rich.table import Table

    table = Table(
        title=title,
        title_style="bold",
        show_lines=False,
        pad_edge=True,
        expand=True,
        border_style="dim",
        title_justify="left",
    )
    table.add_column("#", style="bold cyan", no_wrap=True, justify="right", width=4)
    table.add_column("Title", no_wrap=True, overflow="ellipsis", ratio=1)
    table.add_column("Author", no_wrap=True, width=12)
    table.add_column("Issues", no_wrap=True, width=10)
    table.add_column("Branch", no_wrap=True, overflow="ellipsis", max_width=30)
    table.add_column("Review", no_wrap=True, justify="center", width=8)
    table.add_column("Delta", no_wrap=True, justify="right", width=14)

    for pr in sorted(prs, key=lambda p: p["number"]):
        review_raw = pr.get("reviewDecision") or ""
        style, label = REVIEW_STYLES.get(review_raw, ("dim", review_raw.lower() or "—"))
        review = _styled(label, style)

        draft_marker = _styled(" draft", "dim italic") if pr.get("isDraft") else ""

        adds = pr.get("additions", 0)
        dels = pr.get("deletions", 0)
        files = pr.get("changedFiles", 0)
        delta = f"[green]+{adds}[/] [red]-{dels}[/] [dim]{files}f[/]"

        branch = f"[dim]{pr['headRefName']}[/] → [dim]{pr['baseRefName']}[/]"

        linked = pr_to_issues.get(pr["number"], [])
        issues_cell = (
            " ".join(_styled(f"#{n}", "cyan") for n in sorted(linked)) if linked else ""
        )

        table.add_row(
            str(pr["number"]),
            _clean_title(pr["title"]) + draft_marker,
            f"[bright_white]{pr['author']['login']}[/]",
            issues_cell,
            branch,
            review,
            delta,
        )
    return table


def main() -> int:
    from rich.console import Console

    issues = _fetch_issues()
    prs = _fetch_prs()
    branches = _fetch_linked_branches() if issues else {}
    issue_to_pr, pr_to_issues = _build_cross_refs(branches, prs)

    console = Console()

    # --- Issues ---
    if issues:
        milestones: dict[str, list[dict]] = {}
        no_milestone: list[dict] = []

        for issue in issues:
            ms = issue.get("milestone")
            if ms and ms.get("title"):
                milestones.setdefault(ms["title"], []).append(issue)
            else:
                no_milestone.append(issue)

        console.print()
        console.rule(f"[bold]Open Issues ({len(issues)})[/]")

        for ms_title in sorted(milestones):
            group = milestones[ms_title]
            table = _build_table(
                f"[cyan]▸ Milestone {ms_title}[/]  [dim]({len(group)} issues)[/]",
                group,
                branches,
                issue_to_pr,
            )
            console.print()
            console.print(table)

        if no_milestone:
            table = _build_table(
                f"[yellow]▸ No Milestone[/]  [dim]({len(no_milestone)} issues)[/]",
                no_milestone,
                branches,
                issue_to_pr,
            )
            console.print()
            console.print(table)
    else:
        console.print()
        console.print("[dim]No open issues.[/]")

    # --- Pull Requests ---
    console.print()
    if prs:
        console.rule(f"[bold]Open Pull Requests ({len(prs)})[/]")
        table = _build_pr_table(
            f"[green]▸ Pull Requests[/]  [dim]({len(prs)} open)[/]",
            prs,
            pr_to_issues,
        )
        console.print()
        console.print(table)
    else:
        console.rule("[bold]Pull Requests[/]")
        console.print("[dim]No open pull requests.[/]")

    console.print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
