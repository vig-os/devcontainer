"""
Tests for scripts/validate_commit_msg.py.

These tests run locally (pytest); they do not require the devcontainer CLI.
"""

import importlib.util
import sys
from pathlib import Path

scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

validate_spec = importlib.util.spec_from_file_location(
    "validate_commit_msg", scripts_dir / "validate_commit_msg.py"
)
validate_module = importlib.util.module_from_spec(validate_spec)
validate_spec.loader.exec_module(validate_module)
validate_commit_message = validate_module.validate_commit_message
main = validate_module.main
APPROVED_TYPES = validate_module.APPROVED_TYPES


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

    def test_valid_exactly_one_trailing_newline(self):
        msg = "feat: add x\n\nRefs: #36\n"
        valid, err = validate_commit_message(msg)
        assert valid is True
        assert err is None

    def test_invalid_no_trailing_newline(self):
        msg = "feat: add x\n\nRefs: #36"
        valid, err = validate_commit_message(msg)
        assert valid is False
        assert "trailing newline" in err.lower()

    def test_invalid_multiple_trailing_newlines(self):
        msg = "feat: add x\n\nRefs: #36\n\n"
        valid, err = validate_commit_message(msg)
        assert valid is False
        assert "trailing newline" in err.lower()

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
