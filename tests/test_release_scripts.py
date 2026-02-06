"""
Tests for release management scripts.

These tests verify that prepare-release.sh and finalize-release.sh work correctly
for managing the release cycle with proper git workflows and QMS documentation.
"""

import subprocess
from pathlib import Path

import pytest


class TestPrepareReleaseScript:
    """Tests for scripts/prepare-release.sh - release branch preparation."""

    @pytest.fixture
    def install_script(self):
        """Path to prepare-release.sh."""
        return Path(__file__).resolve().parents[1] / "scripts" / "prepare-release.sh"

    @pytest.fixture
    def minimal_git_repo(self, tmp_path):
        """Create a minimal git repository for testing."""
        repo = tmp_path / "test-repo"
        repo.mkdir()

        # Initialize git repo
        subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=repo,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        # Create dev branch
        subprocess.run(
            ["git", "checkout", "-b", "dev"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        # Create CHANGELOG.md with Unreleased section
        changelog = repo / "CHANGELOG.md"
        changelog.write_text("""# Changelog

## Unreleased

### Added

- New feature X
- New feature Y

### Fixed

- Bug fix Z

## [0.2.0] - 2026-01-01

### Added

- Previous feature
""")

        # Create initial commit
        subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        return repo

    # ═══════════════════════════════════════════════════════════════════════════
    # RED TESTS - Version Validation
    # ═══════════════════════════════════════════════════════════════════════════

    def test_rejects_invalid_semver_format(self, install_script, minimal_git_repo):
        """Should reject non-semantic version formats."""
        result = subprocess.run(
            [str(install_script), "1.2.3.4", "--dry-run"],
            cwd=minimal_git_repo,
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0, "Should fail for invalid semver"
        assert (
            "Invalid version format" in result.stdout
            or "Invalid version format" in result.stderr
        )

    def test_rejects_version_with_v_prefix(self, install_script, minimal_git_repo):
        """Should reject versions with 'v' prefix."""
        result = subprocess.run(
            [str(install_script), "v1.2.3", "--dry-run"],
            cwd=minimal_git_repo,
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        output = result.stdout + result.stderr
        assert "Invalid version format" in output or "1.2.3" in output

    def test_rejects_version_with_prerelease_suffix(
        self, install_script, minimal_git_repo
    ):
        """Should reject versions with pre-release suffixes."""
        result = subprocess.run(
            [str(install_script), "1.2.3-alpha", "--dry-run"],
            cwd=minimal_git_repo,
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        assert (
            "Invalid version format" in result.stdout
            or "Invalid version format" in result.stderr
        )

    def test_accepts_valid_semver(self, install_script, minimal_git_repo):
        """Should accept valid semantic versions."""
        # Test with dry-run to avoid actually creating branches
        result = subprocess.run(
            [str(install_script), "1.2.3", "--dry-run"],
            cwd=minimal_git_repo,
            capture_output=True,
            text=True,
        )
        # Should not fail on version validation
        assert "Invalid version format" not in (result.stdout + result.stderr)

    # ═══════════════════════════════════════════════════════════════════════════
    # RED TESTS - Branch Requirements
    # ═══════════════════════════════════════════════════════════════════════════

    def test_requires_dev_branch(self, install_script, minimal_git_repo):
        """Should fail if not on dev branch."""
        # Create and checkout a different branch
        subprocess.run(
            ["git", "checkout", "-b", "feature/test"],
            cwd=minimal_git_repo,
            check=True,
            capture_output=True,
        )

        result = subprocess.run(
            [str(install_script), "1.0.0", "--dry-run"],
            cwd=minimal_git_repo,
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0, "Should fail when not on dev branch"
        output = result.stdout + result.stderr
        assert "dev branch" in output.lower()

    def test_detects_uncommitted_changes(self, install_script, minimal_git_repo):
        """Should fail if uncommitted changes exist."""
        # Modify CHANGELOG without committing
        changelog = minimal_git_repo / "CHANGELOG.md"
        changelog.write_text(changelog.read_text() + "\n- Uncommitted change\n")

        result = subprocess.run(
            [str(install_script), "1.0.0", "--dry-run"],
            cwd=minimal_git_repo,
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0, "Should fail with uncommitted changes"
        output = result.stdout + result.stderr
        assert "uncommitted" in output.lower() or "changes" in output.lower()

    def test_prevents_duplicate_release_branch(self, install_script, minimal_git_repo):
        """Should fail if release branch already exists."""
        # Create a release branch
        subprocess.run(
            ["git", "checkout", "-b", "release/1.0.0"],
            cwd=minimal_git_repo,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "checkout", "dev"],
            cwd=minimal_git_repo,
            check=True,
            capture_output=True,
        )

        result = subprocess.run(
            [str(install_script), "1.0.0", "--dry-run"],
            cwd=minimal_git_repo,
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0, "Should fail if release branch exists"
        output = result.stdout + result.stderr
        assert "already exists" in output.lower()

    # ═══════════════════════════════════════════════════════════════════════════
    # RED TESTS - CHANGELOG Requirements
    # ═══════════════════════════════════════════════════════════════════════════

    def test_requires_unreleased_section(self, install_script, minimal_git_repo):
        """Should fail if no Unreleased section in CHANGELOG."""
        # Remove Unreleased section
        changelog = minimal_git_repo / "CHANGELOG.md"
        content = changelog.read_text().replace("## Unreleased", "## Old Section")
        changelog.write_text(content)
        subprocess.run(
            ["git", "add", "CHANGELOG.md"],
            cwd=minimal_git_repo,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Remove Unreleased"],
            cwd=minimal_git_repo,
            check=True,
            capture_output=True,
        )

        result = subprocess.run(
            [str(install_script), "1.0.0", "--dry-run"],
            cwd=minimal_git_repo,
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0, "Should fail without Unreleased section"
        output = result.stdout + result.stderr
        assert "unreleased" in output.lower()

    # ═══════════════════════════════════════════════════════════════════════════
    # RED TESTS - Dry-run Mode
    # ═══════════════════════════════════════════════════════════════════════════

    def test_dry_run_creates_no_branches(self, install_script, minimal_git_repo):
        """Dry-run should not create any branches."""
        # Get current branches
        result_before = subprocess.run(
            ["git", "branch", "--list"],
            cwd=minimal_git_repo,
            capture_output=True,
            text=True,
            check=True,
        )
        branches_before = set(result_before.stdout.strip().split("\n"))

        # Run prepare-release in dry-run mode
        subprocess.run(
            [str(install_script), "1.0.0", "--dry-run"],
            cwd=minimal_git_repo,
            capture_output=True,
            text=True,
        )

        # Check branches after
        result_after = subprocess.run(
            ["git", "branch", "--list"],
            cwd=minimal_git_repo,
            capture_output=True,
            text=True,
            check=True,
        )
        branches_after = set(result_after.stdout.strip().split("\n"))

        assert branches_before == branches_after, "Dry-run should not create branches"

    def test_dry_run_modifies_no_files(self, install_script, minimal_git_repo):
        """Dry-run should not modify any files."""
        # Get current git status
        result_before = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=minimal_git_repo,
            capture_output=True,
            text=True,
            check=True,
        )

        # Run prepare-release in dry-run mode
        subprocess.run(
            [str(install_script), "1.0.0", "--dry-run"],
            cwd=minimal_git_repo,
            capture_output=True,
            text=True,
        )

        # Check git status after
        result_after = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=minimal_git_repo,
            capture_output=True,
            text=True,
            check=True,
        )

        assert result_before.stdout == result_after.stdout, (
            "Dry-run should not modify files"
        )

    def test_dry_run_shows_planned_actions(self, install_script, minimal_git_repo):
        """Dry-run should display what would be done."""
        result = subprocess.run(
            [str(install_script), "1.0.0", "--dry-run"],
            cwd=minimal_git_repo,
            capture_output=True,
            text=True,
        )

        output = result.stdout + result.stderr
        assert "dry run" in output.lower() or "would" in output.lower()
        assert "release/1.0.0" in output


class TestFinalizeReleaseScript:
    """Tests for scripts/finalize-release.sh - release finalization.

    These tests will be implemented after prepare-release.sh is working.
    """

    @pytest.fixture
    def finalize_script(self):
        """Path to finalize-release.sh."""
        return Path(__file__).resolve().parents[1] / "scripts" / "finalize-release.sh"

    def test_script_exists(self, finalize_script):
        """finalize-release.sh should exist (placeholder test)."""
        # This will fail until we create the script
        assert finalize_script.exists(), "finalize-release.sh not yet created"
