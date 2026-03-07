"""Tests for vig_utils.prepare_commit_msg_strip_trailers."""

import re
from unittest.mock import patch

from vig_utils import prepare_commit_msg_strip_trailers


class TestLoadTrailerPatterns:
    """Tests for _load_trailer_patterns helper."""

    def test_loads_and_compiles_patterns(self, tmp_path):
        blocklist = tmp_path / "agent-blocklist.toml"
        blocklist.write_text(
            '[patterns]\ntrailers = ["^Co-authored-by: .+$", "^Signed-off-by: .+$"]\n'
        )

        patterns = prepare_commit_msg_strip_trailers._load_trailer_patterns(blocklist)

        assert len(patterns) == 2
        assert all(isinstance(pattern, re.Pattern) for pattern in patterns)
        assert patterns[0].pattern == "^Co-authored-by: .+$"


class TestStripTrailers:
    """Tests for strip_trailers helper."""

    def test_removes_matching_lines_and_returns_true(self, tmp_path):
        blocklist = tmp_path / "agent-blocklist.toml"
        blocklist.write_text('[patterns]\ntrailers = ["^Co-authored-by: .+$"]\n')

        msg = tmp_path / "COMMIT_EDITMSG"
        msg.write_text(
            "feat: add tests\n\nSome body line\nCo-authored-by: Bot <bot@example.com>\n"
        )

        changed = prepare_commit_msg_strip_trailers.strip_trailers(msg, blocklist)

        assert changed is True
        assert "Co-authored-by:" not in msg.read_text()
        assert "Some body line" in msg.read_text()

    def test_no_matching_lines_returns_false_and_preserves_file(self, tmp_path):
        blocklist = tmp_path / "agent-blocklist.toml"
        blocklist.write_text('[patterns]\ntrailers = ["^Co-authored-by: .+$"]\n')

        msg = tmp_path / "COMMIT_EDITMSG"
        original = "fix: cleanup\n\nRefs: #217\n"
        msg.write_text(original)

        changed = prepare_commit_msg_strip_trailers.strip_trailers(msg, blocklist)

        assert changed is False
        assert msg.read_text() == original


class TestMain:
    """Tests for main entrypoint."""

    def test_missing_argument_returns_2(self):
        with patch("sys.argv", ["prepare-commit-msg-strip-trailers"]):
            assert prepare_commit_msg_strip_trailers.main() == 2

    def test_missing_blocklist_returns_0(self, tmp_path):
        missing = tmp_path / "missing.toml"
        msg = tmp_path / "COMMIT_EDITMSG"
        msg.write_text("feat: add tests\n")

        with (
            patch("sys.argv", ["prepare-commit-msg-strip-trailers", str(msg)]),
            patch(
                "vig_utils.prepare_commit_msg_strip_trailers.agent_blocklist_path",
                return_value=missing,
            ),
        ):
            assert prepare_commit_msg_strip_trailers.main() == 0

    def test_missing_message_file_returns_2(self, tmp_path):
        blocklist = tmp_path / "agent-blocklist.toml"
        blocklist.write_text('[patterns]\ntrailers = ["^Co-authored-by: .+$"]\n')
        msg = tmp_path / "COMMIT_EDITMSG"

        with (
            patch("sys.argv", ["prepare-commit-msg-strip-trailers", str(msg)]),
            patch(
                "vig_utils.prepare_commit_msg_strip_trailers.agent_blocklist_path",
                return_value=blocklist,
            ),
        ):
            assert prepare_commit_msg_strip_trailers.main() == 2

    def test_successful_run_returns_0_and_strips(self, tmp_path):
        blocklist = tmp_path / "agent-blocklist.toml"
        blocklist.write_text('[patterns]\ntrailers = ["^Co-authored-by: .+$"]\n')
        msg = tmp_path / "COMMIT_EDITMSG"
        msg.write_text("feat: add tests\n\nCo-authored-by: Bot <bot@example.com>\n")

        with (
            patch("sys.argv", ["prepare-commit-msg-strip-trailers", str(msg)]),
            patch(
                "vig_utils.prepare_commit_msg_strip_trailers.agent_blocklist_path",
                return_value=blocklist,
            ),
        ):
            assert prepare_commit_msg_strip_trailers.main() == 0

        assert "Co-authored-by:" not in msg.read_text()
