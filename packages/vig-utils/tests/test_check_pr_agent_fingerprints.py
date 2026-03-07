"""Tests for vig_utils.check_pr_agent_fingerprints."""

from unittest.mock import patch

from vig_utils import check_pr_agent_fingerprints


class TestMain:
    """Tests for main entrypoint."""

    def test_returns_zero_when_blocklist_missing(self, tmp_path):
        missing = tmp_path / "missing.toml"
        with (
            patch.dict(
                "os.environ", {"PR_TITLE": "title", "PR_BODY": "body"}, clear=True
            ),
            patch(
                "vig_utils.check_pr_agent_fingerprints.agent_blocklist_path",
                return_value=missing,
            ),
        ):
            assert check_pr_agent_fingerprints.main() == 0

    def test_returns_one_when_fingerprint_found(self, tmp_path, capsys):
        blocklist_file = tmp_path / "agent-blocklist.toml"
        blocklist_file.write_text("[patterns]\n")
        blocklist = {"names": ["cursor"], "emails": [], "trailers": []}

        with (
            patch.dict(
                "os.environ",
                {"PR_TITLE": "feat: update", "PR_BODY": "Authored by Cursor"},
                clear=True,
            ),
            patch(
                "vig_utils.check_pr_agent_fingerprints.agent_blocklist_path",
                return_value=blocklist_file,
            ),
            patch(
                "vig_utils.check_pr_agent_fingerprints.load_blocklist",
                return_value=blocklist,
            ),
            patch(
                "vig_utils.check_pr_agent_fingerprints.contains_agent_fingerprint",
                return_value="cursor",
            ),
        ):
            result = check_pr_agent_fingerprints.main()

        captured = capsys.readouterr()
        assert result == 1
        assert "blocked AI agent fingerprint" in captured.err

    def test_returns_zero_when_no_fingerprint(self, tmp_path):
        blocklist_file = tmp_path / "agent-blocklist.toml"
        blocklist_file.write_text("[patterns]\n")
        blocklist = {"names": ["cursor"], "emails": [], "trailers": []}

        with (
            patch.dict(
                "os.environ",
                {"PR_TITLE": "fix: adjust parser", "PR_BODY": "Refs: #217"},
                clear=True,
            ),
            patch(
                "vig_utils.check_pr_agent_fingerprints.agent_blocklist_path",
                return_value=blocklist_file,
            ),
            patch(
                "vig_utils.check_pr_agent_fingerprints.load_blocklist",
                return_value=blocklist,
            ),
            patch(
                "vig_utils.check_pr_agent_fingerprints.contains_agent_fingerprint",
                return_value=None,
            ),
        ):
            assert check_pr_agent_fingerprints.main() == 0

    def test_handles_empty_title_and_body(self, tmp_path):
        blocklist_file = tmp_path / "agent-blocklist.toml"
        blocklist_file.write_text("[patterns]\n")
        blocklist = {"names": ["cursor"], "emails": [], "trailers": []}

        with (
            patch.dict("os.environ", {}, clear=True),
            patch(
                "vig_utils.check_pr_agent_fingerprints.agent_blocklist_path",
                return_value=blocklist_file,
            ),
            patch(
                "vig_utils.check_pr_agent_fingerprints.load_blocklist",
                return_value=blocklist,
            ),
            patch(
                "vig_utils.check_pr_agent_fingerprints.contains_agent_fingerprint",
                return_value=None,
            ) as mock_contains,
        ):
            assert check_pr_agent_fingerprints.main() == 0

        assert mock_contains.called
