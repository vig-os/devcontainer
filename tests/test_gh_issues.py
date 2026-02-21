"""Unit tests for scripts/gh_issues.py."""

import importlib.util
from pathlib import Path

scripts_dir = Path(__file__).parent.parent / "scripts"
gh_issues_spec = importlib.util.spec_from_file_location(
    "gh_issues", scripts_dir / "gh_issues.py"
)
gh_issues = importlib.util.module_from_spec(gh_issues_spec)
gh_issues_spec.loader.exec_module(gh_issues)


class TestGhLink:
    """Test _gh_link helper for clickable issue/PR numbers."""

    def test_issue_link_format(self):
        """Issue number renders as Rich hyperlink to GitHub issues URL."""
        result = gh_issues._gh_link("vig-os/devcontainer", 104, "issues")
        assert (
            result
            == "[link=https://github.com/vig-os/devcontainer/issues/104]104[/link]"
        )

    def test_pr_link_format(self):
        """PR number renders as Rich hyperlink to GitHub pull URL."""
        result = gh_issues._gh_link("vig-os/devcontainer", 42, "pull")
        assert (
            result == "[link=https://github.com/vig-os/devcontainer/pull/42]42[/link]"
        )
