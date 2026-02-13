"""
Tests for vig_utils.validate_commit_msg.

These tests run locally (pytest); they do not require the devcontainer CLI.
"""

import sys

from vig_utils.validate_commit_msg import (
    APPROVED_TYPES,
    REFS_OPTIONAL_TYPES,
    main,
    validate_commit_message,
)


class TestValidateCommitMessage:
    """Test validate_commit_message() with valid and invalid messages."""

    def test_valid_feat_with_issue_ref(self):
        msg = "feat: add new feature\n\nRefs: #36\n"
        valid, err = validate_commit_message(msg)
        assert valid is True
        assert err is None

    def test_valid_feat_with_scope_and_hash_ref(self):
        msg = "feat(ci): add workflow\n\nRefs: #36\n"
        valid, err = validate_commit_message(msg)
        assert valid is True
        assert err is None

    def test_valid_fix_with_multiple_refs(self):
        msg = "fix: correct version substitution\n\nRefs: #42, REQ-123\n"
        valid, err = validate_commit_message(msg)
        assert valid is True
        assert err is None

    def test_valid_docs_with_req_risk_sop_refs(self):
        msg = "docs: describe commit standard\n\nRefs: #36, REQ-DOC-01, RISK-H-02, SOP-DEV-02\n"
        valid, err = validate_commit_message(msg)
        assert valid is True
        assert err is None

    def test_valid_all_approved_types(self):
        for ctype in sorted(APPROVED_TYPES):
            msg = f"{ctype}: do something\n\nRefs: #1\n"
            valid, err = validate_commit_message(msg)
            assert valid is True, f"Type {ctype} should be valid: {err}"
            assert err is None

    def test_valid_scope_with_hyphens(self):
        msg = "chore(deps): bump pre-commit\n\nRefs: #37\n"
        valid, err = validate_commit_message(msg)
        assert valid is True
        assert err is None

    def test_valid_breaking_change_exclamation(self):
        msg = "feat!: breaking change\n\nRefs: #36\n"
        valid, err = validate_commit_message(msg)
        assert valid is True
        assert err is None

    def test_valid_with_optional_body(self):
        msg = "feat: add feature\n\nBody first paragraph.\n\nBody second paragraph.\n\nRefs: #36\n"
        valid, err = validate_commit_message(msg)
        assert valid is True
        assert err is None

    def test_valid_message_without_trailing_newline(self):
        msg = "feat: add x\n\nRefs: #36"
        valid, err = validate_commit_message(msg)
        assert valid is True
        assert err is None

    def test_invalid_empty_message(self):
        valid, err = validate_commit_message("")
        assert valid is False
        assert "empty" in err.lower()

    def test_invalid_unknown_type(self):
        msg = "feature: add new feature\n\nRefs: #36\n"
        valid, err = validate_commit_message(msg)
        assert valid is False
        assert "Unknown commit type" in err
        assert "feature" in err

    def test_invalid_missing_refs_line(self):
        msg = "feat: add new feature\n\nBody with no Refs line.\n"
        valid, err = validate_commit_message(msg)
        assert valid is False
        assert "Refs" in err

    def test_invalid_no_blank_line_before_refs(self):
        msg = "feat: add new feature\nRefs: #36\n"
        valid, err = validate_commit_message(msg)
        assert valid is False
        assert "blank line" in err.lower()

    def test_invalid_single_line_only(self):
        msg = "feat: add new feature\n"
        valid, err = validate_commit_message(msg)
        assert valid is False
        assert "blank" in err.lower() or "Refs" in err

    def test_invalid_malformed_first_line_no_colon(self):
        msg = "feat add new feature\n\nRefs: #36\n"
        valid, err = validate_commit_message(msg)
        assert valid is False
        assert "First line" in err or "type" in err

    def test_valid_body_multiple_lines_before_refs(self):
        msg = "feat: add feature\n\nSome body text.\n\nMore context.\n\nRefs: #36\n"
        valid, err = validate_commit_message(msg)
        assert valid is True
        assert err is None

    def test_invalid_missing_hashtag_in_refs(self):
        msg = "feat: add feature\n\nRefs: 36\n"
        valid, err = validate_commit_message(msg)
        assert valid is False
        assert "Refs" in err or "reference" in err.lower()

    def test_invalid_refs_line_empty_refs(self):
        msg = "feat: add feature\n\nRefs:\n"
        valid, err = validate_commit_message(msg)
        assert valid is False
        assert "Refs" in err or "reference" in err.lower()

    def test_invalid_refs_line_invalid_id_format(self):
        msg = "feat: add feature\n\nRefs: abc\n"
        valid, err = validate_commit_message(msg)
        assert valid is False
        assert "Refs" in err or "reference" in err.lower()

    def test_invalid_refs_without_issue(self):
        msg = "feat: add feature\n\nRefs: REQ-123\n"
        valid, err = validate_commit_message(msg)
        assert valid is False
        assert "issue" in err.lower()

    def test_invalid_multiple_refs_lines(self):
        msg = "feat: add feature\n\nRefs: #36\nRefs: #37\n"
        valid, err = validate_commit_message(msg)
        assert valid is False
        assert "Only one Refs line" in err

    def test_invalid_content_after_refs_line(self):
        msg = "feat: add feature\n\nRefs: #36\n\nExtra line after Refs.\n"
        valid, err = validate_commit_message(msg)
        assert valid is False
        assert "Only one Refs line" in err

    def test_invalid_empty_whitespace_only(self):
        """Test commit message with only whitespace."""
        msg = "\n\n   \n"
        valid, err = validate_commit_message(msg)
        assert valid is False
        assert "empty" in err.lower()


class TestChoreRefsExemption:
    """Test that chore commits may omit the Refs line."""

    def test_chore_valid_without_refs(self):
        """chore commits are valid without a Refs line."""
        msg = "chore: sync dev with main after merge\n\n"
        valid, err = validate_commit_message(msg)
        assert valid is True
        assert err is None

    def test_chore_valid_without_refs_with_body(self):
        """chore commits with a body but no Refs are valid."""
        msg = "chore: maintenance task\n\nSome body explaining what happened.\n"
        valid, err = validate_commit_message(msg)
        assert valid is True
        assert err is None

    def test_chore_valid_with_refs(self):
        """chore commits with a Refs line are also valid."""
        msg = "chore: sync dev with main\n\nRefs: #42\n"
        valid, err = validate_commit_message(msg)
        assert valid is True
        assert err is None

    def test_chore_valid_with_scope_without_refs(self):
        """chore(scope) commits are valid without Refs."""
        msg = "chore(deps): bump pre-commit\n\n"
        valid, err = validate_commit_message(msg)
        assert valid is True
        assert err is None

    def test_chore_invalid_malformed_refs_still_rejected(self):
        """chore commits with a malformed Refs line are still invalid."""
        msg = "chore: do something\n\nRefs: abc\n"
        valid, err = validate_commit_message(msg)
        assert valid is False
        assert "Refs" in err or "reference" in err.lower()

    def test_chore_still_needs_blank_line(self):
        """chore commits still require a blank line after the subject."""
        msg = "chore: do something\nRefs: #36\n"
        valid, err = validate_commit_message(msg)
        assert valid is False
        assert "blank line" in err.lower()

    def test_non_chore_types_still_require_refs(self):
        """All non-chore types still require a Refs line."""
        for ctype in sorted(APPROVED_TYPES - REFS_OPTIONAL_TYPES):
            msg = f"{ctype}: do something\n\n"
            valid, err = validate_commit_message(msg)
            assert valid is False, f"Type {ctype} should require Refs but passed"
            assert "Refs" in err

    def test_chore_subject_only_with_blank_line(self):
        """Minimal chore commit: subject + blank line only."""
        msg = "chore: update dependencies\n\n"
        valid, err = validate_commit_message(msg)
        assert valid is True
        assert err is None


class TestValidateCommitMsgMain:
    """Test main() entry point with file path."""

    def test_main_valid_message_file(self, tmp_path):
        msg_file = tmp_path / "msg"
        msg_file.write_text("feat: add feature\n\nRefs: #36\n")
        # main() uses sys.argv; we need to patch it
        orig_argv = sys.argv
        try:
            sys.argv = ["validate_commit_msg.py", str(msg_file)]
            assert main() == 0
        finally:
            sys.argv = orig_argv

    def test_main_invalid_message_file(self, tmp_path):
        msg_file = tmp_path / "msg"
        msg_file.write_text("feat: add feature\n\n")  # missing Refs
        orig_argv = sys.argv
        try:
            sys.argv = ["validate_commit_msg.py", str(msg_file)]
            assert main() == 1
        finally:
            sys.argv = orig_argv

    def test_main_file_not_found(self):
        orig_argv = sys.argv
        try:
            sys.argv = ["validate_commit_msg.py", "/nonexistent/path/msg"]
            assert main() == 2
        finally:
            sys.argv = orig_argv

    def test_main_wrong_arg_count_no_args(self, capsys):
        """Test main() called with no file argument."""
        orig_argv = sys.argv
        try:
            sys.argv = ["validate_commit_msg.py"]
            assert main() == 2
            captured = capsys.readouterr()
            # Message goes to stderr
            assert "usage" in (captured.out + captured.err).lower()
        finally:
            sys.argv = orig_argv

    def test_main_wrong_arg_count_too_many(self, capsys):
        """Test main() called with too many arguments."""
        orig_argv = sys.argv
        try:
            sys.argv = ["validate_commit_msg.py", "arg1", "arg2"]
            assert main() == 2
            captured = capsys.readouterr()
            # Message goes to stderr
            assert "usage" in (captured.out + captured.err).lower()
        finally:
            sys.argv = orig_argv
