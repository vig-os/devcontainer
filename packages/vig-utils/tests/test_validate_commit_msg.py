"""
Tests for vig_utils.validate_commit_msg.

These tests run locally (pytest); they do not require the devcontainer CLI.
"""

import sys

from vig_utils.validate_commit_msg import (
    DEFAULT_APPROVED_TYPES,
    DEFAULT_REFS_OPTIONAL_TYPES,
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
        for ctype in sorted(DEFAULT_APPROVED_TYPES):
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
        for ctype in sorted(DEFAULT_APPROVED_TYPES - DEFAULT_REFS_OPTIONAL_TYPES):
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


class TestCustomApprovedTypes:
    """Test validate_commit_message() with custom approved types."""

    def test_custom_types_valid_with_custom_type(self):
        """Custom types override defaults."""
        custom_types = frozenset({"mytype", "othertype"})
        msg = "mytype: do something\n\nRefs: #1\n"
        valid, err = validate_commit_message(msg, approved_types=custom_types)
        assert valid is True
        assert err is None

    def test_custom_types_reject_default_type(self):
        """Default types are rejected when custom types are used."""
        custom_types = frozenset({"mytype", "othertype"})
        msg = "feat: add feature\n\nRefs: #1\n"
        valid, err = validate_commit_message(msg, approved_types=custom_types)
        assert valid is False
        assert "Unknown commit type" in err
        assert "feat" in err

    def test_custom_types_allows_all_custom(self):
        """All custom types are accepted."""
        custom_types = frozenset({"alpha", "beta", "gamma"})
        for ctype in custom_types:
            msg = f"{ctype}: do something\n\nRefs: #1\n"
            valid, err = validate_commit_message(msg, approved_types=custom_types)
            assert valid is True, f"Type {ctype} should be valid: {err}"

    def test_custom_types_empty_set_rejects_all(self):
        """Empty custom types set rejects all types."""
        custom_types = frozenset()
        msg = "feat: add feature\n\nRefs: #1\n"
        valid, err = validate_commit_message(msg, approved_types=custom_types)
        assert valid is False
        assert "Unknown commit type" in err

    def test_custom_types_single_type(self):
        """Single custom type works."""
        custom_types = frozenset({"only"})
        msg = "only: do something\n\nRefs: #1\n"
        valid, err = validate_commit_message(msg, approved_types=custom_types)
        assert valid is True
        assert err is None


class TestCustomRefsOptionalTypes:
    """Test validate_commit_message() with custom refs-optional types."""

    def test_custom_refs_optional_types_makes_type_optional(self):
        """Custom refs-optional-types makes specified types not require Refs."""
        custom_optional = frozenset({"feat", "build"})
        msg = "feat: add feature\n\n"
        valid, err = validate_commit_message(msg, refs_optional_types=custom_optional)
        assert valid is True
        assert err is None

    def test_custom_refs_optional_types_preserves_others(self):
        """Types not in refs-optional still require Refs."""
        custom_optional = frozenset({"chore"})
        msg = "fix: fix bug\n\n"
        valid, err = validate_commit_message(msg, refs_optional_types=custom_optional)
        assert valid is False
        assert "Refs" in err

    def test_custom_refs_optional_types_empty_all_require_refs(self):
        """Empty refs-optional-types makes all types require Refs."""
        custom_optional = frozenset()
        msg = "chore: do something\n\n"
        valid, err = validate_commit_message(msg, refs_optional_types=custom_optional)
        assert valid is False
        assert "Refs" in err

    def test_custom_refs_optional_types_multiple(self):
        """Multiple custom refs-optional types work together."""
        custom_optional = frozenset({"chore", "build", "ci"})
        for ctype in custom_optional:
            msg = f"{ctype}: do something\n\n"
            valid, err = validate_commit_message(
                msg, refs_optional_types=custom_optional
            )
            assert valid is True, f"Type {ctype} should be optional: {err}"

    def test_custom_refs_optional_with_refs_still_valid(self):
        """Custom refs-optional types with Refs are still valid."""
        custom_optional = frozenset({"feat"})
        msg = "feat: add feature\n\nRefs: #1\n"
        valid, err = validate_commit_message(msg, refs_optional_types=custom_optional)
        assert valid is True
        assert err is None


class TestCustomApprovedAndOptionalTypes:
    """Test combining custom approved types and custom refs-optional types."""

    def test_combined_custom_types(self):
        """Custom approved types with custom refs-optional types."""
        custom_types = frozenset({"task", "hotfix", "release"})
        custom_optional = frozenset({"release"})
        msg = "release: prepare v1.0\n\n"
        valid, err = validate_commit_message(
            msg, approved_types=custom_types, refs_optional_types=custom_optional
        )
        assert valid is True
        assert err is None

    def test_combined_custom_types_with_refs(self):
        """Custom types with Refs when not required."""
        custom_types = frozenset({"task", "hotfix", "release"})
        custom_optional = frozenset({"release"})
        msg = "release: prepare v1.0\n\nRefs: #50\n"
        valid, err = validate_commit_message(
            msg, approved_types=custom_types, refs_optional_types=custom_optional
        )
        assert valid is True
        assert err is None

    def test_combined_custom_types_required_refs(self):
        """Custom types that require Refs still do."""
        custom_types = frozenset({"task", "hotfix", "release"})
        custom_optional = frozenset({"release"})
        msg = "task: fix something\n\n"
        valid, err = validate_commit_message(
            msg, approved_types=custom_types, refs_optional_types=custom_optional
        )
        assert valid is False
        assert "Refs" in err

    def test_combined_custom_types_rejects_non_custom(self):
        """Non-custom types are rejected."""
        custom_types = frozenset({"task", "hotfix"})
        custom_optional = frozenset({"task"})
        msg = "feat: add feature\n\nRefs: #1\n"
        valid, err = validate_commit_message(
            msg, approved_types=custom_types, refs_optional_types=custom_optional
        )
        assert valid is False
        assert "Unknown commit type" in err


class TestCustomScopes:
    """Test validate_commit_message() with custom approved scopes."""

    def test_scopes_not_enforced_by_default(self):
        """Scopes are not enforced when not provided."""
        msg = "feat(any-scope): add feature\n\nRefs: #1\n"
        valid, err = validate_commit_message(msg)
        assert valid is True
        assert err is None

    def test_scopes_not_enforced_empty_set(self):
        """Empty scopes set means no scope enforcement."""
        custom_scopes = frozenset()
        msg = "feat(random-scope): add feature\n\nRefs: #1\n"
        valid, err = validate_commit_message(msg, approved_scopes=custom_scopes)
        assert valid is True
        assert err is None

    def test_valid_with_enforced_scopes(self):
        """Valid commit with enforced scopes."""
        custom_scopes = frozenset({"api", "cli", "utils"})
        msg = "feat(api): add endpoint\n\nRefs: #1\n"
        valid, err = validate_commit_message(msg, approved_scopes=custom_scopes)
        assert valid is True
        assert err is None

    def test_invalid_scope_not_in_list(self):
        """Reject commit with scope not in approved list."""
        custom_scopes = frozenset({"api", "cli", "utils"})
        msg = "feat(database): add migration\n\nRefs: #1\n"
        valid, err = validate_commit_message(msg, approved_scopes=custom_scopes)
        assert valid is False
        assert "Unknown scope" in err
        assert "database" in err

    def test_scope_required_when_enforced(self):
        """When scopes are enforced, they must be provided."""
        custom_scopes = frozenset({"api", "cli"})
        msg = "feat: add feature\n\nRefs: #1\n"
        valid, err = validate_commit_message(msg, approved_scopes=custom_scopes)
        assert valid is False
        assert "Scope is required" in err

    def test_all_enforced_scopes_valid(self):
        """All enforced scopes are accepted."""
        custom_scopes = frozenset({"api", "cli", "utils"})
        for scope in custom_scopes:
            msg = f"feat({scope}): do something\n\nRefs: #1\n"
            valid, err = validate_commit_message(msg, approved_scopes=custom_scopes)
            assert valid is True, f"Scope {scope} should be valid: {err}"

    def test_scope_with_hyphens(self):
        """Scopes can contain hyphens."""
        custom_scopes = frozenset({"api-v2", "cli-tool", "db-utils"})
        msg = "feat(api-v2): add endpoint\n\nRefs: #1\n"
        valid, err = validate_commit_message(msg, approved_scopes=custom_scopes)
        assert valid is True
        assert err is None

    def test_scope_case_sensitive(self):
        """Scope matching is case-sensitive."""
        custom_scopes = frozenset({"api", "cli"})
        msg = "feat(API): add feature\n\nRefs: #1\n"
        valid, err = validate_commit_message(msg, approved_scopes=custom_scopes)
        assert valid is False
        assert "Unknown scope" in err

    def test_combined_types_and_scopes(self):
        """Use custom types with custom scopes."""
        custom_types = frozenset({"feature", "bugfix"})
        custom_scopes = frozenset({"backend", "frontend"})
        msg = "feature(backend): add API\n\nRefs: #1\n"
        valid, err = validate_commit_message(
            msg, approved_types=custom_types, approved_scopes=custom_scopes
        )
        assert valid is True
        assert err is None

    def test_combined_types_and_scopes_invalid_type(self):
        """Invalid type rejected even with valid scope."""
        custom_types = frozenset({"feature", "bugfix"})
        custom_scopes = frozenset({"backend", "frontend"})
        msg = "feat(backend): add API\n\nRefs: #1\n"
        valid, err = validate_commit_message(
            msg, approved_types=custom_types, approved_scopes=custom_scopes
        )
        assert valid is False
        assert "Unknown commit type" in err

    def test_combined_types_and_scopes_invalid_scope(self):
        """Invalid scope rejected even with valid type."""
        custom_types = frozenset({"feature", "bugfix"})
        custom_scopes = frozenset({"backend", "frontend"})
        msg = "feature(mobile): add app\n\nRefs: #1\n"
        valid, err = validate_commit_message(
            msg, approved_types=custom_types, approved_scopes=custom_scopes
        )
        assert valid is False
        assert "Unknown scope" in err


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
        import pytest

        orig_argv = sys.argv
        try:
            sys.argv = ["validate_commit_msg.py"]
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 2
            captured = capsys.readouterr()
            # Message goes to stderr
            assert "usage" in (captured.out + captured.err).lower()
        finally:
            sys.argv = orig_argv

    def test_main_wrong_arg_count_too_many(self, capsys):
        """Test main() called with too many arguments."""
        import pytest

        orig_argv = sys.argv
        try:
            sys.argv = ["validate_commit_msg.py", "arg1", "arg2"]
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 2
            captured = capsys.readouterr()
            # Message goes to stderr
            assert "usage" in (captured.out + captured.err).lower()
        finally:
            sys.argv = orig_argv


class TestMainWithCustomTypes:
    """Test main() CLI with --types and --refs-optional-types arguments."""

    def test_main_with_custom_types(self, tmp_path):
        """Test main() with --types argument."""
        msg_file = tmp_path / "msg"
        msg_file.write_text("custom: do something\n\nRefs: #1\n")
        orig_argv = sys.argv
        try:
            sys.argv = [
                "validate_commit_msg.py",
                str(msg_file),
                "--types",
                "custom,other",
            ]
            assert main() == 0
        finally:
            sys.argv = orig_argv

    def test_main_with_custom_types_rejects_default_type(self, tmp_path):
        """Test main() with --types rejects default types."""
        msg_file = tmp_path / "msg"
        msg_file.write_text("feat: add feature\n\nRefs: #1\n")
        orig_argv = sys.argv
        try:
            sys.argv = [
                "validate_commit_msg.py",
                str(msg_file),
                "--types",
                "custom,other",
            ]
            assert main() == 1
        finally:
            sys.argv = orig_argv

    def test_main_with_custom_refs_optional_types(self, tmp_path):
        """Test main() with --refs-optional-types argument."""
        msg_file = tmp_path / "msg"
        msg_file.write_text("custom: do something\n\n")
        orig_argv = sys.argv
        try:
            sys.argv = [
                "validate_commit_msg.py",
                str(msg_file),
                "--types",
                "custom,other",
                "--refs-optional-types",
                "custom",
            ]
            assert main() == 0
        finally:
            sys.argv = orig_argv

    def test_main_with_custom_refs_optional_types_still_enforces_others(self, tmp_path):
        """Test main() --refs-optional-types still enforces Refs for other types."""
        msg_file = tmp_path / "msg"
        msg_file.write_text("other: do something\n\n")
        orig_argv = sys.argv
        try:
            sys.argv = [
                "validate_commit_msg.py",
                str(msg_file),
                "--types",
                "custom,other",
                "--refs-optional-types",
                "custom",
            ]
            assert main() == 1
        finally:
            sys.argv = orig_argv

    def test_main_with_comma_separated_types(self, tmp_path):
        """Test main() with comma-separated type list."""
        msg_file = tmp_path / "msg"
        msg_file.write_text("feat: add feature\n\nRefs: #1\n")
        orig_argv = sys.argv
        try:
            # Include 'feat' in custom types
            sys.argv = [
                "validate_commit_msg.py",
                str(msg_file),
                "--types",
                "feat,fix,docs",
            ]
            assert main() == 0
        finally:
            sys.argv = orig_argv

    def test_main_with_spaces_in_comma_separated_types(self, tmp_path):
        """Test main() handles spaces in comma-separated types."""
        msg_file = tmp_path / "msg"
        msg_file.write_text("feat: add feature\n\nRefs: #1\n")
        orig_argv = sys.argv
        try:
            # Types with spaces around commas should be parsed correctly
            sys.argv = [
                "validate_commit_msg.py",
                str(msg_file),
                "--types",
                "feat , fix , docs",
            ]
            assert main() == 0
        finally:
            sys.argv = orig_argv

    def test_main_with_comma_separated_refs_optional_types(self, tmp_path):
        """Test main() with comma-separated refs-optional-types."""
        msg_file = tmp_path / "msg"
        msg_file.write_text("chore: do something\n\n")
        orig_argv = sys.argv
        try:
            sys.argv = [
                "validate_commit_msg.py",
                str(msg_file),
                "--refs-optional-types",
                "chore,build",
            ]
            assert main() == 0
        finally:
            sys.argv = orig_argv

    def test_main_pre_commit_hook_simulation(self, tmp_path):
        """Simulate pre-commit hook with custom configuration."""
        msg_file = tmp_path / "msg"
        msg_file.write_text("workflow: update CI\n\n")
        orig_argv = sys.argv
        try:
            # Simulate pre-commit hook configuration
            sys.argv = [
                "validate_commit_msg.py",
                str(msg_file),
                "--types",
                "feat,fix,workflow",
                "--refs-optional-types",
                "workflow",
            ]
            assert main() == 0
        finally:
            sys.argv = orig_argv


class TestGitHubLinkedRefs:
    """Test that Refs line accepts GitHub auto-linked issue format [#N](URL).

    After pushing, GitHub rewrites '#31' to '[#31](https://github.com/…/issues/31)'.
    The validator must accept both plain and linked formats.
    """

    def test_valid_single_linked_issue(self):
        msg = (
            "feat: add feature\n\nRefs: [#31](https://github.com/org/repo/issues/31)\n"
        )
        valid, err = validate_commit_message(msg)
        assert valid is True
        assert err is None

    def test_valid_multiple_linked_issues(self):
        msg = (
            "fix: fix bug\n\n"
            "Refs: [#31](https://github.com/org/repo/issues/31), "
            "[#32](https://github.com/org/repo/issues/32)\n"
        )
        valid, err = validate_commit_message(msg)
        assert valid is True
        assert err is None

    def test_valid_mixed_plain_and_linked_issue(self):
        msg = (
            "feat: add feature\n\n"
            "Refs: #10, [#31](https://github.com/org/repo/issues/31)\n"
        )
        valid, err = validate_commit_message(msg)
        assert valid is True
        assert err is None

    def test_valid_linked_issue_with_other_ref_types(self):
        msg = (
            "docs: update docs\n\n"
            "Refs: [#31](https://github.com/org/repo/issues/31), REQ-DOC-01, RISK-H-02\n"
        )
        valid, err = validate_commit_message(msg)
        assert valid is True
        assert err is None

    def test_valid_linked_issue_with_body(self):
        msg = (
            "feat: add feature\n\n"
            "Some body text explaining the change.\n\n"
            "Refs: [#31](https://github.com/org/repo/issues/31)\n"
        )
        valid, err = validate_commit_message(msg)
        assert valid is True
        assert err is None

    def test_valid_linked_issue_without_trailing_newline(self):
        msg = "feat: add x\n\nRefs: [#31](https://github.com/org/repo/issues/31)"
        valid, err = validate_commit_message(msg)
        assert valid is True
        assert err is None

    def test_valid_linked_issue_pull_url(self):
        """GitHub may link to /pull/ instead of /issues/."""
        msg = "feat: add feature\n\nRefs: [#31](https://github.com/org/repo/pull/31)\n"
        valid, err = validate_commit_message(msg)
        assert valid is True
        assert err is None

    def test_invalid_linked_ref_without_issue(self):
        """Linked REQ/RISK/SOP alone (no issue) is still rejected."""
        msg = "feat: add feature\n\nRefs: REQ-123\n"
        valid, err = validate_commit_message(msg)
        assert valid is False
        assert "issue" in err.lower()

    def test_valid_chore_with_linked_issue(self):
        msg = "chore: sync dev\n\nRefs: [#42](https://github.com/org/repo/issues/42)\n"
        valid, err = validate_commit_message(msg)
        assert valid is True
        assert err is None


class TestMainWithCustomScopes:
    """Test main() CLI with --scopes argument."""

    def test_main_with_custom_scopes(self, tmp_path):
        """Test main() with --scopes argument."""
        msg_file = tmp_path / "msg"
        msg_file.write_text("feat(api): add endpoint\n\nRefs: #1\n")
        orig_argv = sys.argv
        try:
            sys.argv = [
                "validate_commit_msg.py",
                str(msg_file),
                "--scopes",
                "api,cli,utils",
            ]
            assert main() == 0
        finally:
            sys.argv = orig_argv

    def test_main_with_custom_scopes_rejects_invalid(self, tmp_path):
        """Test main() with --scopes rejects invalid scopes."""
        msg_file = tmp_path / "msg"
        msg_file.write_text("feat(invalid): add something\n\nRefs: #1\n")
        orig_argv = sys.argv
        try:
            sys.argv = [
                "validate_commit_msg.py",
                str(msg_file),
                "--scopes",
                "api,cli,utils",
            ]
            assert main() == 1
        finally:
            sys.argv = orig_argv

    def test_main_without_scopes_no_enforcement(self, tmp_path):
        """Test main() without --scopes allows any scope."""
        msg_file = tmp_path / "msg"
        msg_file.write_text("feat(anything): add feature\n\nRefs: #1\n")
        orig_argv = sys.argv
        try:
            sys.argv = ["validate_commit_msg.py", str(msg_file)]
            assert main() == 0
        finally:
            sys.argv = orig_argv

    def test_main_with_scopes_requires_scope_when_enforced(self, tmp_path):
        """Test main() with --scopes requires scope in commits."""
        msg_file = tmp_path / "msg"
        msg_file.write_text("feat: add feature\n\nRefs: #1\n")
        orig_argv = sys.argv
        try:
            sys.argv = [
                "validate_commit_msg.py",
                str(msg_file),
                "--scopes",
                "api,cli",
            ]
            assert main() == 1
        finally:
            sys.argv = orig_argv

    def test_main_with_all_options(self, tmp_path):
        """Test main() with all custom options together."""
        msg_file = tmp_path / "msg"
        msg_file.write_text("task(backend): implement feature\n\nRefs: #51\n")
        orig_argv = sys.argv
        try:
            sys.argv = [
                "validate_commit_msg.py",
                str(msg_file),
                "--types",
                "task,bugfix",
                "--scopes",
                "backend,frontend",
                "--refs-optional-types",
                "task",
            ]
            assert main() == 0
        finally:
            sys.argv = orig_argv

    def test_main_with_comma_separated_scopes(self, tmp_path):
        """Test main() with comma-separated scopes."""
        msg_file = tmp_path / "msg"
        msg_file.write_text("feat(utils): add helper\n\nRefs: #1\n")
        orig_argv = sys.argv
        try:
            sys.argv = [
                "validate_commit_msg.py",
                str(msg_file),
                "--scopes",
                "api,utils,cli",
            ]
            assert main() == 0
        finally:
            sys.argv = orig_argv

    def test_main_with_spaces_in_scopes(self, tmp_path):
        """Test main() handles spaces in comma-separated scopes."""
        msg_file = tmp_path / "msg"
        msg_file.write_text("feat(api): add endpoint\n\nRefs: #1\n")
        orig_argv = sys.argv
        try:
            # Scopes with spaces around commas should be parsed correctly
            sys.argv = [
                "validate_commit_msg.py",
                str(msg_file),
                "--scopes",
                "api , cli , utils",
            ]
            assert main() == 0
        finally:
            sys.argv = orig_argv
