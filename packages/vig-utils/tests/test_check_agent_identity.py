"""Tests for vig_utils.check_agent_identity."""

from unittest.mock import Mock, patch

from vig_utils import check_agent_identity


class TestCheckValue:
    """Tests for _check_value helper."""

    def test_empty_value_returns_none(self):
        blocklist = {"names": ["cursor"], "emails": ["cursoragent@cursor.com"]}
        assert check_agent_identity._check_value("", blocklist) is None

    def test_name_match_is_case_insensitive(self):
        blocklist = {"names": ["cursor"], "emails": []}
        assert (
            check_agent_identity._check_value("Authored by CurSor Agent", blocklist)
            == "cursor"
        )

    def test_email_match_is_case_insensitive(self):
        blocklist = {"names": [], "emails": ["cursoragent@cursor.com"]}
        assert (
            check_agent_identity._check_value("CURSORAGENT@CURSOR.COM", blocklist)
            == "cursoragent@cursor.com"
        )

    def test_no_match_returns_none(self):
        blocklist = {"names": ["cursor"], "emails": ["cursoragent@cursor.com"]}
        assert (
            check_agent_identity._check_value("Alice <alice@example.com>", blocklist)
            is None
        )


class TestGetGitConfig:
    """Tests for _get_git_config helper."""

    def test_returns_stripped_stdout(self, tmp_path):
        mocked = Mock(stdout="  user-value  \n")
        with patch(
            "vig_utils.check_agent_identity.subprocess.run", return_value=mocked
        ):
            value = check_agent_identity._get_git_config(tmp_path, "user.name")
        assert value == "user-value"

    def test_returns_empty_on_exception(self, tmp_path):
        with patch(
            "vig_utils.check_agent_identity.subprocess.run",
            side_effect=RuntimeError("boom"),
        ):
            value = check_agent_identity._get_git_config(tmp_path, "user.email")
        assert value == ""


class TestMain:
    """Tests for main entrypoint."""

    def test_github_actions_environment_skips_check(self):
        with patch.dict("os.environ", {"GITHUB_ACTIONS": "true"}, clear=True):
            assert check_agent_identity.main() == 0

    def test_ci_environment_skips_check(self):
        with patch.dict("os.environ", {"CI": "true"}, clear=True):
            assert check_agent_identity.main() == 0

    def test_missing_blocklist_skips_check(self, tmp_path):
        missing = tmp_path / "missing.toml"
        with (
            patch.dict("os.environ", {}, clear=True),
            patch(
                "vig_utils.check_agent_identity.find_repo_root", return_value=tmp_path
            ),
            patch(
                "vig_utils.check_agent_identity.agent_blocklist_path",
                return_value=missing,
            ),
        ):
            assert check_agent_identity.main() == 0

    def test_detects_match_from_env_values(self, tmp_path, capsys):
        blocklist = {"names": ["cursor"], "emails": []}
        blocklist_file = tmp_path / "agent-blocklist.toml"
        blocklist_file.write_text("[patterns]\n")

        with (
            patch.dict(
                "os.environ",
                {
                    "GIT_AUTHOR_NAME": "Cursor Agent",
                    "GIT_AUTHOR_EMAIL": "human@example.com",
                    "GIT_COMMITTER_NAME": "Human",
                    "GIT_COMMITTER_EMAIL": "human@example.com",
                },
                clear=True,
            ),
            patch(
                "vig_utils.check_agent_identity.find_repo_root", return_value=tmp_path
            ),
            patch(
                "vig_utils.check_agent_identity.agent_blocklist_path",
                return_value=blocklist_file,
            ),
            patch(
                "vig_utils.check_agent_identity.load_blocklist", return_value=blocklist
            ),
        ):
            result = check_agent_identity.main()

        captured = capsys.readouterr()
        assert result == 1
        assert "GIT_AUTHOR_NAME matches blocklisted" in captured.err

    def test_detects_match_from_git_config_fallback(self, tmp_path):
        blocklist = {"names": ["claude"], "emails": []}
        blocklist_file = tmp_path / "agent-blocklist.toml"
        blocklist_file.write_text("[patterns]\n")

        with (
            patch.dict("os.environ", {}, clear=True),
            patch(
                "vig_utils.check_agent_identity.find_repo_root", return_value=tmp_path
            ),
            patch(
                "vig_utils.check_agent_identity.agent_blocklist_path",
                return_value=blocklist_file,
            ),
            patch(
                "vig_utils.check_agent_identity.load_blocklist", return_value=blocklist
            ),
            patch(
                "vig_utils.check_agent_identity._get_git_config",
                side_effect=["Claude Assistant", "human@example.com"],
            ),
        ):
            assert check_agent_identity.main() == 1

    def test_clean_identity_passes(self, tmp_path):
        blocklist = {"names": ["cursor"], "emails": ["cursoragent@cursor.com"]}
        blocklist_file = tmp_path / "agent-blocklist.toml"
        blocklist_file.write_text("[patterns]\n")

        with (
            patch.dict(
                "os.environ",
                {
                    "GIT_AUTHOR_NAME": "Alice",
                    "GIT_AUTHOR_EMAIL": "alice@example.com",
                    "GIT_COMMITTER_NAME": "Alice",
                    "GIT_COMMITTER_EMAIL": "alice@example.com",
                },
                clear=True,
            ),
            patch(
                "vig_utils.check_agent_identity.find_repo_root", return_value=tmp_path
            ),
            patch(
                "vig_utils.check_agent_identity.agent_blocklist_path",
                return_value=blocklist_file,
            ),
            patch(
                "vig_utils.check_agent_identity.load_blocklist", return_value=blocklist
            ),
        ):
            assert check_agent_identity.main() == 0
