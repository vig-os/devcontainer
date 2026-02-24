# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Fixed

- **CI Project Checks coverage includes devc_remote_uri tests** ([#70](https://github.com/vig-os/devcontainer/issues/70))
  - Add `tests/test_devc_remote_uri.py` to test-project action pytest run
  - Add build_uri validation tests for empty devcontainer_path, ssh_host, container_workspace
- **just check uses wrong path — justfile_directory() resolves incorrectly in imported justfile.base** ([#187](https://github.com/vig-os/devcontainer/issues/187))
  - Replace `dirname(justfile_directory())` with `source_directory()/scripts` to correctly locate version-check.sh in deployed workspaces and devcontainer repo
  - Regression test: `just check config` runs successfully from workspace
- **gh-issues CI status deduplicates re-run checks** ([#176](https://github.com/vig-os/devcontainer/issues/176))
  - Deduplicate `statusCheckRollup` by check name, keeping only the latest result (by `completedAt`)
  - CI column now matches GitHub PR page when checks are re-run
- **worktree-start swallows derive-branch-summary error messages** ([#183](https://github.com/vig-os/devcontainer/issues/183))
  - Remove stderr suppression so error messages from derive-branch-summary.sh are visible
  - Retry with standard model when lightweight model fails; print manual workaround hint if both fail
  - Add optional MODEL_TIER parameter to derive-branch-summary.sh; BATS test for retry path
- **validate-commit-msg rejects AI agent identity fingerprints** ([#163](https://github.com/vig-os/devcontainer/issues/163))
  - Commit-msg hook now rejects commits containing Co-authored-by, cursoragent, cursor.com, claude, codex, chatgpt, copilot
  - Blocks "Made with [Cursor](https://cursor.com)" and similar branding
  - Enforced before other validation; applies to full message including subject-only mode
- **worktree-start preflight gaps — agent hang and gh repo set-default** ([#154](https://github.com/vig-os/devcontainer/issues/154))
  - Add timeout (30s) to agent-based branch summary derivation; failure produces clear error with manual workaround
  - Add gh repo set-default preflight before any gh API calls; auto-resolve from origin or fail with instructions
  - Extract derive-branch-summary.sh with BRANCH_SUMMARY_CMD mock for tests; BATS tests for timeout and error paths
- **gh-issues cross-ref detects Refs: #N in PR bodies** ([#121](https://github.com/vig-os/devcontainer/issues/121))
  - `_build_cross_refs` now parses `Refs: #102` and comma-separated variants (`Refs: #102, #103`) alongside Closes/Fixes/Resolves
- **PR table Reviewer column distinguishes requested vs completed reviewers** ([#105](https://github.com/vig-os/devcontainer/issues/105))
  - Requested reviewers (no review yet) display as `?login` with dim italic style
  - Actual reviewers (submitted review) display as plain login with green/red
- **worktree-attach restarts stopped tmux session when worktree dir exists** ([#132](https://github.com/vig-os/devcontainer/issues/132))
  - Detect when worktree directory exists but tmux session has terminated
  - Automatically restart session in existing worktree before attaching
  - Guard `worktree-start` against branches already checked out elsewhere with an informative error
  - BATS integration tests for restart, error paths, and checkout detection
- **Issue numbers in PR table are now clickable hyperlinks** ([#174](https://github.com/vig-os/devcontainer/issues/174))
  - Replace plain styled text with Rich hyperlink markup in the Issues column of the PR table
- **Synced justfiles reference scripts not included in workspace manifest** ([#190](https://github.com/vig-os/devcontainer/issues/190))
  - Add manifest entries for resolve-branch.sh, derive-branch-summary.sh, check-skill-names.sh → `.devcontainer/scripts/`
  - Update justfile.worktree to use `source_directory() / "scripts"` for portable path resolution
  - Add Sed transform for check-skill-names.sh path in synced `.pre-commit-config.yaml`

### Changed

- **worktree-clean: add filter mode for stopped-only vs all** ([#158](https://github.com/vig-os/devcontainer/issues/158))
  - Default `just worktree-clean` (no args) now cleans only stopped worktrees, skips running tmux sessions
  - `just worktree-clean all` retains previous behavior (clean all worktrees) with warning
  - Summary output shows cleaned vs skipped worktrees
  - `just wt-clean` alias unchanged
- **Consolidate sync_manifest.py and utils.py into manifest-as-config architecture** ([#89](https://github.com/vig-os/devcontainer/issues/89))
  - Extract transform classes (Sed, RemoveLines, etc.) to `scripts/transforms.py`
  - Unify sed logic: `substitute_in_file()` in utils shared by sed_inplace and Sed transform
  - Convert MANIFEST from Python code to declarative `scripts/manifest.toml`
- **justfile.base is canonical at repo root, synced via manifest** ([#71](https://github.com/vig-os/devcontainer/issues/71))
  - Root `justfile.base` is now the single source of truth; synced to `assets/workspace/.devcontainer/justfile.base` via `sync_manifest.py`
  - `just sync-workspace` and prepare-build keep workspace template in sync
- **Autonomous PR skills use pull request template** ([#147](https://github.com/vig-os/devcontainer/issues/147))
  - `pr_create` and `worktree_pr` now read `.github/pull_request_template.md` and fill each section from available context
  - Explicit read-then-fill procedure with section-by-section mapping (Description, Type of Change, Changelog Entry, Testing, Checklist, Refs)
  - Ensures autonomous PRs match manual PR structure and include all checklist items
- **Rename skill namespace separator from colon to underscore** ([#128](https://github.com/vig-os/devcontainer/issues/128))
  - All skill directories under `.cursor/skills/` and `assets/workspace/.cursor/skills/` renamed (e.g. `issue:create` → `issue_create`)
  - All internal cross-references, frontmatter, prose, `CLAUDE.md` command table, and label taxonomy updated
  - `issue_create` skill enhanced: gathers context via `just gh-issues` before drafting, suggests parent/child relationships and milestones
  - `issue_create` skill now includes TDD acceptance criterion for testable issue types
  - Remaining `sync-issues` workflow trigger references removed from skills
  - `tdd.mdc` expanded with test scenario checklist and test type guidance; switched from always-on to glob-triggered on source/test files
  - `code_tdd`, `code_execute`, and `worktree_execute` skills now reference `tdd.mdc` explicitly
- **Clickable issue and PR numbers in gh-issues table** ([#104](https://github.com/vig-os/devcontainer/issues/104))
  - `#` column in issue and PR tables now uses Rich OSC 8 hyperlinks to GitHub URLs
  - Clicking an issue or PR number opens it in the browser (or Cursor's integrated terminal)
- **PR template aligned with canonical commit types** ([#115](https://github.com/vig-os/devcontainer/issues/115))
  - Replace ad-hoc Type of Change checkboxes with the 10 canonical commit types
  - Move breaking change from type to a separate modifier checkbox
  - Add release-branch hint to Related Issues section

### Added

- **devc-remote.sh — bash orchestrator for remote devcontainer** ([#152](https://github.com/vig-os/devcontainer/issues/152))
  - `scripts/devc-remote.sh`: parse_args, detect_editor_cli, check_ssh, remote_preflight, remote_compose_up, open_editor
  - `scripts/devc_remote_uri.py`: stub for URI construction (sibling sub-issue)
  - BATS unit tests with mocked commands
- **devc_remote_uri.py — Cursor URI construction for remote devcontainers** ([#153](https://github.com/vig-os/devcontainer/issues/153))
  - Standalone Python module with `hex_encode()` and `build_uri()` for vscode-remote URIs
  - CLI: `devc_remote_uri.py <workspace_path> <ssh_host> <container_workspace>` prints URI to stdout
  - Stdlib only (json, argparse); called by devc-remote.sh (sibling sub-issue)
- **Devcontainer and git recipes in justfile.base** ([#71](https://github.com/vig-os/devcontainer/issues/71))
  - Devcontainer group (host-side only): `up`, `down`, `status`, `logs`, `shell`, `restart`, `open`
  - Auto-detect podman/docker compose; graceful failure if run inside container
  - Git group: `log` (pretty one-line, last 20), `branch` (current + recent)
- **CI status column in just gh-issues PR table** ([#143](https://github.com/vig-os/devcontainer/issues/143))
  - PR table shows CI column with pass/fail/pending summary (✓ 6/6, ⏳ 3/6, ✗ 5/6)
  - Failed check names visible when checks fail
  - CI cell links to GitHub PR checks page
- **Config-driven model tier assignments for agent skills** ([#103](https://github.com/vig-os/devcontainer/issues/103))
  - Extended `.cursor/agent-models.toml` with `standard` tier (sonnet-4.5) and `[skill-tiers]` mapping for skill categories (data-gathering, formatting, review, orchestration)
  - New rule `.cursor/rules/subagent-delegation.mdc` documenting when and how to delegate mechanical sub-steps to lightweight subagents via the Task tool
  - Added `## Delegation` sections to 12 skills identifying steps that should spawn lightweight/standard-tier subagents to reduce token consumption on the primary autonomous model
  - Skills updated: `worktree_solve-and-pr`, `worktree_brainstorm`, `worktree_plan`, `worktree_execute`, `worktree_verify`, `worktree_pr`, `worktree_ci-check`, `worktree_ci-fix`, `code_review`, `issue_triage`, `pr_post-merge`, `ci_check`
- **hadolint pre-commit hook for Containerfile linting** ([#122](https://github.com/vig-os/devcontainer/issues/122))
  - Add `hadolint` hook to `.pre-commit-config.yaml`, pinned by SHA (v2.9.3)
  - Enforce Dockerfile best practices: pinned base image tags, consolidated `RUN` layers, shellcheck for inline scripts
  - Fix `tests/fixtures/sidecar.Containerfile` to pass hadolint with no warnings
- **tmux installed in container image for worktree session persistence** ([#130](https://github.com/vig-os/devcontainer/issues/130))
  - Add `tmux` to the Containerfile `apt-get install` block
  - Enables autonomous worktree agents to survive Cursor session disconnects
- **pr_solve skill — diagnose PR failures, plan fixes, execute** ([#133](https://github.com/vig-os/devcontainer/issues/133))
  - Single entry point that gathers CI failures, review feedback, and merge state into a consolidated diagnosis
  - Presents diagnosis for approval before any fixes, plans fixes using design_plan conventions, executes with TDD discipline
  - Pre-commit hook `check-skill-names` enforces `[a-z0-9][a-z0-9_-]*` naming for skill directories
  - BATS test suite with canary test that injects a bad name into the real repo
  - TDD scenario checklist expanded with canary, idempotency, and concurrency categories
- **Optional reviewer parameter for autonomous worktree pipeline** ([#102](https://github.com/vig-os/devcontainer/issues/102))
  - Support `reviewer` parameter in `just worktree-start`
  - Propagate `PR_REVIEWER` via tmux environment to the autonomous agent
  - Update `worktree_pr` skill to automatically request review when `PR_REVIEWER` is set
- **Inception skill family for pre-development product thinking** ([#90](https://github.com/vig-os/devcontainer/issues/90))
  - Four-phase pipeline: `inception_explore` (divergent problem understanding), `inception_scope` (convergent scoping), `inception_architect` (pattern-validated design), `inception_plan` (decomposition into GitHub issues)
  - Document templates: `docs/templates/RFC.md` (Problem Statement, Proposed Solution, Alternatives, Impact, Phasing) and `docs/templates/DESIGN.md` (Architecture, Components, Data Flow, Technology Stack, Testing)
  - Document directories: `docs/rfcs/` and `docs/designs/` for durable artifacts
  - Certified architecture reference repos embedded in `inception_architect` skill: ByteByteGoHq/system-design-101, donnemartin/system-design-primer, karanpratapsingh/system-design, binhnguyennus/awesome-scalability, mehdihadeli/awesome-software-architecture
  - Fills the gap between "I have an idea" and "I have issues ready for design"
- **Automatic update notifications on devcontainer attach** ([#73](https://github.com/vig-os/devcontainer/issues/73))
  - Wire `version-check.sh` into `post-attach.sh` for automatic update checks
  - Silent, throttled checks (24-hour interval by default)
  - Graceful failure - never disrupts the attach process
- **Host-side devcontainer upgrade recipe** ([#73](https://github.com/vig-os/devcontainer/issues/73))
  - New `just devcontainer-upgrade` recipe for convenient upgrades from host
  - Container detection - prevents accidental execution inside devcontainer
  - Clear error messages with instructions when run from wrong context
- **`just check` recipe for version management** ([#73](https://github.com/vig-os/devcontainer/issues/73))
  - Expose version-check.sh subcommands: `just check`, `just check config`, `just check on/off`, `just check 7d`
  - User-friendly interface for managing update notifications
- **Cursor worktree support for parallel agent development** ([#64](https://github.com/vig-os/devcontainer/issues/64))
  - `.cursor/worktrees.json` for native Cursor worktree initialization (macOS/Linux local)
  - `justfile.worktree` with tmux + cursor-agent CLI recipes (`worktree-start`, `worktree-list`, `worktree-attach`, `worktree-stop`, `worktree-clean`) for devcontainer environments
  - Autonomous worktree skills: `worktree_brainstorm`, `worktree_plan`, `worktree_execute`, `worktree_verify`, `worktree_pr`, `worktree_ask`, `worktree_solve-and-pr`
  - Sync manifest updated to propagate worktree config and recipes to downstream projects
- **GitHub issue and PR dashboard recipe** ([#84](https://github.com/vig-os/devcontainer/issues/84))
  - `just gh-issues` displays open issues grouped by milestone in rich tables with columns for type, title, assignee, linked branch, priority, scope, effort, and semver
  - Open pull requests section with author, branch, review status, and diff delta
  - Linked branches fetched via a single GraphQL call
  - Ships to downstream workspaces via sync manifest (`.devcontainer/justfile.gh` + `.devcontainer/scripts/gh_issues.py`)
- **Issue triage agent skill** ([#81](https://github.com/vig-os/devcontainer/issues/81))
  - Cursor skill at `.cursor/skills/issue_triage/` for triaging open issues across priority, area, effort, SemVer impact, dependencies, and release readiness
  - Decision matrix groups issues into parent/sub-issue clusters with milestone suggestions
  - Predefined label taxonomy (`label-taxonomy.md`) for priority, area, effort, and SemVer dimensions
  - Sync manifest updated to propagate skill to workspace template
- **Cursor commands and rules for agent-driven development workflows** ([#63](https://github.com/vig-os/devcontainer/issues/63))
  - Always-on rules: `coding-principles.mdc` (YAGNI, minimal diff, DRY, no secrets, traceability, single responsibility) and `tdd.mdc` (RED-GREEN-REFACTOR discipline)
  - Tier 1 commands: `start-issue.md`, `create-issue.md`, `brainstorm.md`, `tdd.md`, `review.md`, `verify.md`
  - Tier 2 commands: `check-ci.md`, `fix-ci.md`
  - Tier 3 commands: `plan.md`, `execute-plan.md`, `debug.md`
- **Agent-friendly issue templates, changelog rule, and PR template enhancements** ([#61](https://github.com/vig-os/devcontainer/issues/61))
  - Cursor rule `.cursor/rules/changelog.mdc` (always applied) guiding agents on when, where, and how to update CHANGELOG.md
  - Changelog Category dropdown added to `bug_report.yml`, `feature_request.yml`, and `task.yml` issue templates
  - New issue templates: `refactor.yml` (scope/invariants), `documentation.yml` (docs/templates workflow), `ci_build.yml` (target workflows/triggers/release impact)
  - Template chooser `config.yml` disabling blank issues and linking to project docs
  - PR template enhanced with explicit Changelog Entry section, CI/Build change type, and updated checklist referencing `docs/templates/` and `just docs`
- **GitHub issue and PR templates in workspace template** ([#63](https://github.com/vig-os/devcontainer/issues/63))
  - Pull request template, issue templates, Dependabot config, and `.gitmessage` synced to `assets/workspace/`
  - Ground truth lives in repo root; `assets/workspace/` is generated output
- **cursor-agent CLI pre-installed in devcontainer image** ([#108](https://github.com/vig-os/devcontainer/issues/108))
  - Enables `just worktree-start` to work out of the box without manual installation
- **Automatic merge commit message compliance** ([#79](https://github.com/vig-os/devcontainer/issues/79))
  - `setup-gh-repo.sh` configures repo merge settings via `gh api` (`merge_commit_title=PR_TITLE`, `merge_commit_message=PR_BODY`, `allow_auto_merge=true`)
  - Wired into `post-create.sh` so downstream devcontainer projects get compliant merge commits automatically
  - `--subject-only` flag for `validate-commit-msg` to validate PR titles without requiring body or Refs
  - `pr-title-check.yml` CI workflow enforces commit message standard on PR titles
  - PR body template includes `Refs: #` placeholder for merge commit traceability

### Changed

- **Updated update notification message** ([#73](https://github.com/vig-os/devcontainer/issues/73))
  - Fixed misleading `just update` instruction (Python deps, not devcontainer upgrade)
  - Show correct upgrade instructions: `just devcontainer-upgrade` and curl fallback
  - Clarify that upgrade must run from host terminal, not inside container
  - Add reminder to rebuild container in VS Code after upgrade
- **Declarative Python sync manifest** ([#67](https://github.com/vig-os/devcontainer/issues/67))
  - Replaced `sync-manifest.txt` + bash function and `sync-workspace.sh` with `scripts/sync_manifest.py`
  - Single source of truth for which files to sync and what transformations to apply
  - `prepare-build.sh` and `just sync-workspace` both call the same manifest
- **Namespace-prefixed Cursor skill names** ([#67](https://github.com/vig-os/devcontainer/issues/67))
  - Renamed all 15 skills with colon-separated namespace prefixes (`issue:`, `design:`, `code:`, `git:`, `ci:`, `pr:`)
  - Enables filtering by namespace when invoking skills (e.g., typing `code:` shows implementation skills)
- **`--org` flag for install script** ([#33](https://github.com/vig-os/devcontainer/issues/33))
  - Allows overriding the default organization name (default: `vigOS`)
  - Passes `ORG_NAME` as environment variable to the container
  - Usage: `curl -sSf ... | bash -s --org MyOrg -- ~/my-project`
  - Unit tests for `--org` flag in help, default value, and custom override
- **Virtual environment prompt renaming** ([#34](https://github.com/vig-os/devcontainer/issues/34))
  - Post-create script updates venv prompt from "template-project" to project short name
  - Integration test verifies venv activate script does not contain "template-project"
- **BATS (Bash Automated Testing System) shell testing framework** ([#35](https://github.com/vig-os/devcontainer/issues/35))
  - npm dependencies for bats, bats-support, bats-assert, and bats-file
  - `test-bats` justfile task and requirements configuration
  - `test_helper.bash` supporting both local (node_modules) and CI (BATS_LIB_PATH) library resolution
  - CI integration in setup-env and test-project actions with conditional parallel execution via GNU parallel
  - Comprehensive BATS test suites for build, clean, init, install, and prepare-build scripts
  - Tests verify script structure, argument parsing, function definitions, error handling, and OS/runtime detection patterns
- **Post-install user configuration step** ([#35](https://github.com/vig-os/devcontainer/issues/35))
  - Automatically call copy-host-user-conf.sh after workspace initialization
  - `run_user_conf()` helper for host-side setup (git, ssh, gh)
  - Integration tests for .devcontainer/.conf/ directory creation and expected config files
- **Git repository initialization in install script** ([#35](https://github.com/vig-os/devcontainer/issues/35))
  - `setup_git_repo()` function to initialize git if missing
  - Creates initial commit "chore: initial project scaffold" for new repos
  - Automatically creates main and dev branches
  - `test-install` justfile recipe for running install tests
  - Integration tests for git repo initialization, branches, and initial commit
- **Commit message standardization** ([#36](https://github.com/vig-os/devcontainer/issues/36))
  - Commit message format: `type(scope)!: subject` with mandatory `Refs: #<issue>` line
  - Documentation: `docs/COMMIT_MESSAGE_STANDARD.md` defining format, approved types (feat, fix, docs, chore, refactor, test, ci, build, revert, style), and traceability requirements
  - Validation script: `scripts/validate_commit_msg.py` enforcing the standard
  - Commit-msg hook: `.githooks/commit-msg` runs validation on every commit
  - Pre-commit integration: commit-msg stage hook in `.pre-commit-config.yaml`
  - Git commit template: `.gitmessage` with format placeholder
  - Cursor integration: `.cursor/rules/commit-messages.mdc` and `.cursor/commands/commit-msg.md` for AI-assisted commit messages
  - Workspace template: all commit message tooling included in `assets/workspace/` for new projects
  - Tests: `tests/test_validate_commit_msg.py` with comprehensive validation test cases
- **nano text editor** in devcontainer image ([#37](https://github.com/vig-os/devcontainer/issues/37))
- **Chore Refs exemption** in commit message standard ([#37](https://github.com/vig-os/devcontainer/issues/37))
  - `chore` commits may omit the `Refs:` line when no issue or PR is directly related
  - Validator updated with `REFS_OPTIONAL_TYPES` to accept chore commits without Refs
- **Dependency review allowlist entry** for debug@0.6.0 ([#37](https://github.com/vig-os/devcontainer/issues/37))
  - Added GHSA-9vvw-cc9w-f27h exception to `.github/dependency-review-allow.txt`
  - Addresses ReDoS vulnerability in transitive test dependency (bats-assert → verbose → debug)
  - High risk severity but isolated to CI/development environment with expiration 2026-11-17
|- **Dependency review exception for legacy test vulnerabilities** ([#37](https://github.com/vig-os/devcontainer/issues/37))
  - Comprehensive acceptance register for 9 transitive vulnerabilities in unmaintained BATS test framework dependencies
  - All 9 vulnerabilities are isolated to CI/development environment (engine.io, debug, node-uuid, qs, tough-cookie, ws, xmlhttprequest, form-data)
  - Formal risk assessments and mitigations documented in `SECURITY.md` and `.github/dependency-review-allow.txt`
  - Expiration-enforced exceptions with 2026-11-17 expiration date to force periodic re-evaluation

- **Bandit and Safety security scanning** ([#37](https://github.com/vig-os/devcontainer/issues/37), [#50](https://github.com/vig-os/devcontainer/issues/50))
  - Bandit pre-commit hook for medium/high/critical severity Python code analysis
  - CI pipeline job with Bandit static analysis and Safety dependency vulnerability scanning
  - Reports uploaded as artifacts (30-day retention) with job summary integration
- **Scheduled weekly security scan workflow** (`security-scan.yml`) ([#37](https://github.com/vig-os/devcontainer/issues/37))
  - Full Trivy vulnerability scan (all severities) against `dev` branch every Monday 06:00 UTC
  - SBOM generation (CycloneDX) and SARIF upload to GitHub Security tab
  - Non-blocking: catches newly published CVEs between pull requests
- **Non-blocking unfixed vulnerability reporting in CI** ([#37](https://github.com/vig-os/devcontainer/issues/37))
  - Additional CI scan step reports unfixed HIGH/CRITICAL CVEs for awareness without blocking the pipeline
- **Comprehensive `.trivyignore` vulnerability acceptance register** ([#37](https://github.com/vig-os/devcontainer/issues/37))
  - Formal medtech-compliant register (IEC 62304 / ISO 13485) documenting 10 accepted CVEs
  - Each entry includes risk assessment, exploitability justification, fix status, and mitigation
  - 6-month expiration dates enforce periodic re-evaluation
- **Expiration-enforced dependency-review exceptions** ([#37](https://github.com/vig-os/devcontainer/issues/37))
  - Allow GHSA-wvrr-2x4r-394v (bats-file false positive) via `.github/dependency-review-allow.txt`
  - CI validation step parses expiration dates and fails the pipeline when exceptions expire, forcing periodic review
- **Branch name enforcement as a pre-commit hook** ([#38](https://github.com/vig-os/devcontainer/issues/38))
  - New `branch-name` hook enforcing `<type>/<issue>-<summary>` convention (e.g. `feature/38-standardize-branching-strategy-enforcement`)
  - Pre-commit configuration updated in repo and in workspace assets (`.pre-commit-config.yaml`, `assets/workspace/.pre-commit-config.yaml`)
  - Integration tests added for valid and invalid branch names
- **Cursor rules for branch naming and issue workflow** ([#38](https://github.com/vig-os/devcontainer/issues/38))
  - `.cursor/rules/branch-naming.mdc`: topic branch naming format, branch types, workflow for creating/linking branches via `gh issue develop`
  - Guidelines for inferring branch type from issue labels and deriving short summary from issue title
- **Release cycle documentation** ([#38](https://github.com/vig-os/devcontainer/issues/38), [#48](https://github.com/vig-os/devcontainer/issues/48))
  - `docs/RELEASE_CYCLE.md` with complete release workflow, branching strategy, and CI/CD integration
  - Cursor commands: `after-pr-merge.md`, `submit-pr.md`
- **pip-licenses** installed system-wide with version verification test ([#43](https://github.com/vig-os/devcontainer/issues/43))
- **just-lsp** language server and VS Code extension for Just files ([#44](https://github.com/vig-os/devcontainer/issues/44))
- **Automated release cycle** ([#48](https://github.com/vig-os/devcontainer/issues/48))
  - `prepare-release` and `finalize-release` justfile commands triggering GitHub Actions workflows
  - `prepare-changelog.py` script with prepare, validate, reset, and finalize commands for CHANGELOG automation
  - `reset-changelog` justfile command for post-merge CHANGELOG cleanup
  - `prepare-release.yml` GitHub Actions workflow: validates semantic version, creates release branch, prepares CHANGELOG
  - Unified `release.yml` pipeline: validate → finalize → build/test → publish → rollback
  - Comprehensive test suite in `tests/test_release_cycle.py`
- **CI testing infrastructure** ([#48](https://github.com/vig-os/devcontainer/issues/48))
  - `ci.yml` workflow replacing `test.yml` with streamlined project checks (lint, changelog validation, utility and release-cycle tests)
  - Reusable composite actions: `setup-env`, `build-image`, `test-image`, `test-integration`, `test-project`
  - Artifact transfer between jobs for consistent image testing
  - Retry logic across all CI operations for transient failure handling
- **GitHub Actions SHA pinning enforcement** ([#50](https://github.com/vig-os/devcontainer/issues/50))
  - `scripts/check_action_pins.py` pre-commit hook and CI check ensuring all GitHub Actions and Docker actions reference commit SHAs
  - Comprehensive test suite in `tests/test_check_action_pins.py`
- **CODEOWNERS** for automated review assignment ([#50](https://github.com/vig-os/devcontainer/issues/50))
- **SECURITY.md** with vulnerability reporting procedures and supported version policy ([#50](https://github.com/vig-os/devcontainer/issues/50))
- **OpenSSF Scorecard workflow** (`scorecard.yml`) for supply chain security scoring ([#50](https://github.com/vig-os/devcontainer/issues/50))
- **CodeQL analysis workflow** (`codeql.yml`) for automated static security analysis ([#50](https://github.com/vig-os/devcontainer/issues/50))
- **Dependabot configuration** for automated dependency update PRs with license compliance monitoring ([#50](https://github.com/vig-os/devcontainer/issues/50))
- **Vulnerability scanning and dependency review** in CI pipeline with non-blocking MEDIUM severity reporting ([#50](https://github.com/vig-os/devcontainer/issues/50))
- **SBOM generation, container signing, and provenance attestation** in release and CI pipelines ([#50](https://github.com/vig-os/devcontainer/issues/50))
- **Edge case tests** for changelog validation, action SHA pinning, and install script ([#50](https://github.com/vig-os/devcontainer/issues/50))
- **`vig-utils` reusable CLI utilities package** ([#51](https://github.com/vig-os/devcontainer/issues/51))
  - Python package in `packages/vig-utils/` for shared validation and build utilities
  - `validate_commit_msg` module: enforces commit message format and references standards
    - Configurable commit scopes validation: scope list can be customized per project
    - Scopes are optional by default; if used, must be in the approved list
    - Support for multiple scopes, comma-separated (e.g., `feat(api, cli): add feature`)
    - Support for GitHub auto-linked issue references (e.g., PR cross-repo links)
    - Comprehensive test suite with edge case coverage for PR and cross-repo issue links
  - `prepare_changelog` module: CHANGELOG management and validation
  - `check_action_pins` module: GitHub Actions SHA pinning enforcement
  - Integrated into CI/CD pipeline and pre-commit hooks as standard Python package
  - Package version tests verify installation and correct versioning
- **Code coverage reporting in CI** ([#52](https://github.com/vig-os/devcontainer/issues/52))
  - Code coverage measurement integrated into test action workflow
  - Coverage threshold raised to 50% for unit tests
  - Expanded unit tests to improve overall test coverage
- **File duplication detection and elimination** ([#53](https://github.com/vig-os/devcontainer/issues/53))
  - Build-time manifest system detects and removes duplicated workspace assets
  - Replaces duplicated files with sync manifest entries, reducing redundancy
  - Workspace assets now synchronized from central manifest during build preparation
  - GitHub workflow templates for devcontainer projects included in sync manifest
  - Automated npm dependency management with centralized version pinning in `.github/package.json`
  - Extract build preparation into dedicated `prepare-build.sh` script with manifest sync
  - SHA-256 checksum verification tests for synced files via `parse_manifest` fixture and `test_manifest_files`
- **GitHub workflow templates for devcontainer projects** ([#53](https://github.com/vig-os/devcontainer/issues/53))
  - Reusable workflow templates for continuous integration and deployment
  - Support for projects using devcontainer-based development environments
- **Centralized `@devcontainers/cli` version management** ([#53](https://github.com/vig-os/devcontainer/issues/53))
  - Version pinned in `.github/package.json` for consistent behavior across workflows and builds
  - Ensures reproducibility across build and setup environments
- **`--require-scope` flag for `validate-commit-msg`** ([#58](https://github.com/vig-os/devcontainer/issues/58))
  - New CLI flag to mandate that all commits include at least one scope (e.g. `feat(api): ...`)
  - When enabled, scopeless commits (e.g. `feat: ...`) are rejected at the commit-msg stage
  - Comprehensive tests added to `test_validate_commit_msg.py`
- **`post-start.sh` devcontainer lifecycle script** ([#60](https://github.com/vig-os/devcontainer/issues/60))
  - New script runs on every container start (create + restart)
  - Handles Docker socket permissions and dependency sync via `just sync`
  - Replaces inline `postStartCommand` in `devcontainer.json`

### Changed

- **Dependency sync delegated to `just sync` across all lifecycle hooks** ([#60](https://github.com/vig-os/devcontainer/issues/60))
  - `post-create.sh`, `post-start.sh`, and `post-attach.sh` now call `just sync` instead of `uv sync` directly
  - `justfile.base` `sync` recipe updated with `--all-extras --no-install-project` flags and `pyproject.toml` guard
  - Abstracts toolchain details so future dependency managers only need a recipe change

- **Git initialization default branch** ([#35](https://github.com/vig-os/devcontainer/issues/35))
  - Updated git initialization to set the default branch to 'main' instead of 'master'
  - Consolidated Podman installation with other apt commands in Containerfile
- **CI release workflow uses GitHub API** ([#35](https://github.com/vig-os/devcontainer/issues/35))
  - Replace local git operations with GitHub API in prepare-release workflow
  - Use commit-action for CHANGELOG updates instead of local git
  - Replace git operations with GitHub API in release finalization flow
  - Simplify rollback and tag deletion to use gh api
  - Add sync-dependencies input to setup-env action (default: false)
  - Remove checkout step from setup-env; callers must checkout explicitly
  - Update all workflow callers to pass sync-dependencies input
  - Update CI security job to use uv with setup-env action
- **Commit message guidelines** - updated documentation ([#36](https://github.com/vig-os/devcontainer/issues/37))
- **Expected version checks** - updated ruff and pre-commit versions in test suite ([#37](https://github.com/vig-os/devcontainer/issues/37))
- **Bumped `actions/create-github-app-token`** from v1 to v2 across workflows with updated SHA pins ([#37](https://github.com/vig-os/devcontainer/issues/37))
- **Pinned `@devcontainers/cli`** to version 0.81.1 in CI for consistent behavior ([#37](https://github.com/vig-os/devcontainer/issues/37))
- **CI and release Trivy scans gate on fixable CVEs only** ([#37](https://github.com/vig-os/devcontainer/issues/37))
  - Added `ignore-unfixed: true` to blocking scan steps in `ci.yml` and `release.yml`
  - Unfixable CVEs no longer block the pipeline; documented in `.trivyignore` with risk assessments
- **Updated pre-commit hook configuration in the devcontainer** ([#38](https://github.com/vig-os/devcontainer/issues/38))
  - Exclude issue and template docs from .github_data
  - Autofix shellcheck
  - Autofix pymarkdown
  - Add license compliance check
- **Renamed `publish-container-image.yml` to `release.yml`** and expanded into unified release pipeline ([#48](https://github.com/vig-os/devcontainer/issues/48))
- **Merged `prepare-build.sh` into `build.sh`** — consolidated directory preparation, asset copying, placeholder replacement, and README updates into a single entry point ([#48](https://github.com/vig-os/devcontainer/issues/48))
- **Consolidated test files by domain** — reorganized from 6 files to 4 (`test_image.py`, `test_integration.py`, `test_utils.py`, `test_release_cycle.py`) ([#48](https://github.com/vig-os/devcontainer/issues/48))
- **Replaced `setup-python-uv` with flexible `setup-env` composite action** supporting optional inputs for podman, Node.js, and devcontainer CLI ([#48](https://github.com/vig-os/devcontainer/issues/48))
- **Reduced `sync-issues` workflow triggers** — removed `edited` event type from issues and pull_request triggers ([#48](https://github.com/vig-os/devcontainer/issues/48))
- **Release workflow pushes tested images** instead of rebuilding after tests pass ([#48](https://github.com/vig-os/devcontainer/issues/48))
- **Updated CONTRIBUTE.md** release workflow documentation to match automated process ([#50](https://github.com/vig-os/devcontainer/issues/50))
- **CodeQL Action v3 → v4 upgrade**
  - Updated all CodeQL Action references from v3 (deprecated Dec 2026) to v4.32.2
  - Updated in `.github/workflows/codeql.yml`, `security-scan.yml`, and `ci.yml`
  - Uses commit hash `45cbd0c69e560cd9e7cd7f8c32362050c9b7ded2` for integrity
- **Sync-issues workflow output directory** ([#53](https://github.com/vig-os/devcontainer/issues/53))
  - Changed output directory from '.github_data' to 'docs' for better project structure alignment
- **Workspace `validate-commit-msg` hook configured strict-by-default** ([#58](https://github.com/vig-os/devcontainer/issues/58))
  - `assets/workspace/.pre-commit-config.yaml` now ships with explicit `args` instead of commented-out examples
  - Default args enable type enforcement, scope enforcement with `--require-scope`, and `chore` refs exemption
  - Link to `vig-utils` README added as a comment above the hook for discoverability

### Deprecated

### Removed

- **`scripts/prepare-build.sh`** — merged into `build.sh` ([#48](https://github.com/vig-os/devcontainer/issues/48))
- **`scripts/sync-prs-issues.sh`** — deprecated sync script ([#48](https://github.com/vig-os/devcontainer/issues/48))
- **`test.yml` workflow** — replaced by `ci.yml` ([#48](https://github.com/vig-os/devcontainer/issues/48))
- **Stale `.github_data/` directory** — 98 files superseded by `docs/issues/` and `docs/pull-requests/` ([#91](https://github.com/vig-os/devcontainer/issues/91))

### Fixed

- **Sync-issues workflow schedule trigger** ([#91](https://github.com/vig-os/devcontainer/issues/91))
  - `github.event.inputs.target-branch` is null on schedule events, causing `TARGET_BRANCH` to resolve to `refs/heads/` (404 in commit-action)
  - Added `|| 'dev'` fallbacks for all input references so schedule triggers default to `dev`
  - Added `output-dir` and `commit-msg` as parameterized `workflow_dispatch` inputs
- **Host-specific paths in `.gitconfig` and unreliable `postAttachCommand` lifecycle** ([#60](https://github.com/vig-os/devcontainer/issues/60))
  - `copy-host-user-conf.sh` now generates a container-ready `.gitconfig` with `/root/...` paths and strips host-only entries (credential helpers, `excludesfile`, `includeIf`) at export time
  - Refactored devcontainer lifecycle: moved all one-time setup (`init-git.sh`, `setup-git-conf.sh`, `init-precommit.sh`) from `postAttachCommand` into `postCreateCommand`
  - New `verify-auth.sh` script for lightweight SSH agent and `gh` auth verification (read-only, no side effects)
  - `postAttachCommand` now only runs auth verification and dependency sync — no longer depends on unreliable attach hook for critical setup
  - `setup-git-conf.sh` simplified to one-time file placement (removed SSH agent scanning logic)
- **GitHub CLI config copy target path** ([#35](https://github.com/vig-os/devcontainer/issues/35))
  - Corrected target path for copying GitHub CLI configuration in post-install step
- **Install script terminal check in dry-run mode** ([#37](https://github.com/vig-os/devcontainer/issues/37))
  - Moved TTY check to after dry-run flag check to allow --dry-run mode to exit immediately without requiring an interactive terminal
  - Fixes test_dry_run_shows_command timeout in CI environments
- **Sync-issues workflow robustness** — pinned runner to ubuntu-22.04, added target branch validation for `workflow_dispatch`, removed overly broad cache restore-key pattern ([#37](https://github.com/vig-os/devcontainer/issues/37))
- **Integration test image tag normalization** — fixed overly greedy regex that removed commit hashes from image tags; now only removes known architecture suffixes (`-amd64`, `-arm64`) at the end ([#37](https://github.com/vig-os/devcontainer/issues/37))
- **`just precommit` recipe** - Run pre-commit through `uv run` to ensure it uses the virtual environment ([#46](https://github.com/vig-os/devcontainer/issues/46))
- **Sidecar tests in CI** — run via host podman to avoid API version mismatch between host (3.4.4) and container client (4.0.0) ([#48](https://github.com/vig-os/devcontainer/issues/48))
- **Non-ASCII characters in justfiles** - Replaced Unicode box-drawing characters (═, ───) and emojis with ASCII equivalents for just-lsp compatibility ([#49](https://github.com/vig-os/devcontainer/issues/49))
- **Pre-commit exclusion pattern** for pymarkdown updated to correct regex ([#50](https://github.com/vig-os/devcontainer/issues/50))
- **Pytest test collection** - Exclude `tests/tmp/` directory (integration test workspaces) from test discovery to prevent import errors
- **CI/CD release validation and test action checkout refs** ([#72](https://github.com/vig-os/devcontainer/issues/72))
  - Block release if CI checks are still pending, in progress, queued, or in other non-terminal states
  - Add `ref` input to `test-image` and `test-integration` composite actions to pin checkout commit
  - Pass `finalize_sha` to test actions ensuring tests always run against the correct built commit
  - Fix `install-just` conditional in `setup-env` to respect input flag; was unconditionally running
  - Remove dead macOS `stat` fallback from `build-image` verification step (action only runs on ubuntu-22.04)
- **Release tag convention: `v` prefix removed** ([#57](https://github.com/vig-os/devcontainer/issues/57))
  - Git tags now follow the bare `X.Y.Z` format (e.g. `1.0.0`) instead of `vX.Y.Z`
  - `release.yml` and `prepare-release.yml` workflows updated to create, push, and validate tags without the `v` prefix
  - `assets/workspace/.github/workflows/release.yml` template updated to match
  - CHANGELOG historical release links updated to bare-version URLs (`0.2.1`, `0.2.0`, `0.1`)
  - Existing repository tags (`v0.1`, `v0.2.0`, `v0.2.1`) renamed to bare versions and pushed
  - Documentation and inline comments updated across `docs/RELEASE_CYCLE.md`, `CONTRIBUTE.md`, `README.md`, and `build-image` action
- **`gh` version assertion in `test_gh_version`** ([#93](https://github.com/vig-os/devcontainer/issues/93))
  - Updated expected version prefix from `2.86.` to `2.87.` to match GitHub CLI 2.87.0 (released 2026-02-18)
- **BATS test failures in init-workspace and prepare-build suites** ([#67](https://github.com/vig-os/devcontainer/issues/67))
  - Removed premature init-workspace.bats tests for unimplemented `is_git_dirty` feature (9 tests)
  - Fixed prepare-build.bats grep pattern for `sync_manifest.py` invocation to handle shell quoting
- **`just init` fails to install devcontainer CLI on Linux** ([#111](https://github.com/vig-os/devcontainer/issues/111))
  - `npm install -g` requires root access to `/usr/local/lib/node_modules`, causing EACCES permission denied
  - Switched to local `npm install` (package already declared in `package.json`), matching the existing `bats` pattern
  - Updated pytest fixtures in `conftest.py` to also check `node_modules/.bin/devcontainer`
- **Worktree branch resolution broken by tab-separated `gh` output** ([#103](https://github.com/vig-os/devcontainer/issues/103))
  - `gh issue develop --list` now returns `branch<TAB>URL`; the previous `grep -oE '[^ ]+$'` captured the entire line
  - Extracted parsing into `scripts/resolve-branch.sh` (`head -1 | cut -f1`) used by both call sites in `justfile.worktree`

### Security

- **Eliminated 13 transitive vulnerabilities in BATS test dependencies** ([#37](https://github.com/vig-os/devcontainer/issues/37))
  - Bumped bats-assert from v2.1.0 to v2.2.0, which dropped a bogus runtime dependency on the `verbose` npm package
  - Removed entire transitive dependency tree: engine.io, debug, node-uuid, qs, tough-cookie, ws, xmlhttprequest, form-data, request, sockjs, and others (50+ packages reduced to 5)
  - Cleaned 13 now-unnecessary GHSA exceptions from `.github/dependency-review-allow.txt`
- **Go stdlib CVEs from gh binary accepted and documented** ([#37](https://github.com/vig-os/devcontainer/issues/37))
- CVE-2025-68121, CVE-2025-61726, CVE-2025-61728, CVE-2025-61730 added to `.trivyignore`
- Vulnerabilities embedded in statically-linked GitHub CLI binary; low exploitability in devcontainer context
- Each entry includes risk assessment, justification, and 3-month expiration date to force re-review
- Awaiting upstream `gh` release with Go 1.25.7 or later
- **GHSA-wvrr-2x4r-394v (bats-file false positive) accepted in dependency review** ([#37](https://github.com/vig-os/devcontainer/issues/37))
- Added to `.github/dependency-review-allow.txt` with 6-month expiration date enforced by CI
- **Upgraded pip** in Containerfile to fix CVE-2025-8869 (symbolic link extraction vulnerability) ([#37](https://github.com/vig-os/devcontainer/issues/37))
- **Digest-pinned base image** (`python:3.12-slim-bookworm`) with SHA256 checksum verification for all downloaded binaries and `.trivyignore` risk-assessment policy in Containerfile ([#50](https://github.com/vig-os/devcontainer/issues/50))
- **Minisign signature verification** for cargo-binstall downloads ([#50](https://github.com/vig-os/devcontainer/issues/50))
- **GitHub Actions and Docker actions pinned to commit SHAs** across all workflows ([#50](https://github.com/vig-os/devcontainer/issues/50))
- **Pre-commit hook repos pinned to commit SHAs** ([#50](https://github.com/vig-os/devcontainer/issues/50))
- **Workflow permissions hardened** with least-privilege principle and explicit token scoping ([#50](https://github.com/vig-os/devcontainer/issues/50))
- **Input sanitization** — inline expression interpolation replaced with environment variables in workflow run blocks to prevent injection ([#50](https://github.com/vig-os/devcontainer/issues/50))

## [0.2.1](https://github.com/vig-os/devcontainer/releases/tag/0.2.1) - 2026-01-28

### Added

- **Manual target branch specification** for sync-issues workflow
  - Added `target-branch` input to `workflow_dispatch` trigger for manually specifying commit target branch
  - Allows explicit branch selection when triggering workflow manually (e.g., `main`, `dev`)
- **cargo-binstall** in Containerfile
  - Install via official install script; binaries in `/root/.cargo/bin` with `ENV PATH` set
  - Version check in `tests/test_image.py`
- **typstyle** linting
  - Install via `cargo-binstall` in Containerfile
  - Version check in test suite
  - Pre-commit hook configuration for typstyle
- **Just command runner** installation and version verification
  - Added installation of the latest version of `just` (1.46.0) in the Containerfile
  - Added tests to verify `just` installation and version in `test_image.py`
  - Added integration tests for `just` recipes (`test_just_default`, `test_just_help`, `test_just_info`, `test_just_pytest`)
- **GitHub Actions workflow for multi-architecture container image publishing** (`.github/workflows/release.yml`)
  - Automated build and publish workflow triggered on semantic version tags (X.Y.Z)
  - Multi-architecture support (amd64, arm64) with parallel builds on native runners
  - Image testing before push: runs `pytest tests/test_image.py` against built images
  - Manual dispatch support for testing workflow changes without pushing images (default version: 99.0.1)
  - Optional manual publishing: `workflow_dispatch` can publish images/manifests when `publish=true` (default false)
  - Architecture validation and dynamic selection: users can specify single or multiple architectures (amd64, arm64) with validation
  - Comprehensive error handling and verification steps
  - OCI-standard labels via `docker/metadata-action`
  - Build log artifacts for debugging (always uploaded for manual dispatch and on failure)
  - Multi-architecture manifest creation for automatic platform selection
  - Centralized version extraction job for reuse across build and manifest jobs
  - Concurrency control to prevent duplicate builds
  - Timeout protection (60 minutes for builds, 10 minutes for manifest)
- **GitHub Actions workflow for syncing issues and PRs** (`.github/workflows/sync-issues.yml`)
  - Automated sync of GitHub issues and PRs to markdown files in `.github_data/`
  - Runs on schedule (daily), manual trigger, issue events, and PR events
  - Smart branch selection: commits to `main` when PRs are merged into `main`, otherwise commits to `dev`
  - Cache-based state management to track last sync timestamp
  - Force update option for manual workflow dispatch
- **Enhanced test suite**
  - Added utility function tests (`tests/test_utils.py`) for `sed_inplace` and `update_version_line`
  - Improved test organization in justfile with grouped test commands (`just test-all`, `just test-image`, `just test-utils`)
- **Documentation improvements**
  - Added workflow status badge to README template showing publish workflow status
  - Simplified contribution guidelines by removing QEMU build instructions

### Changed

- **Sync-issues workflow branch protection bypass**
  - Added GitHub App token generation step using `actions/create-github-app-token@v2`
  - Updated commit-action to use GitHub App token for bypassing branch protection rules
  - Updated `vig-os/commit-action` from `v0.1.1` to `v0.1.3`
  - Changed commit-action environment variable from `GITHUB_TOKEN`/`GITHUB_REF` to `GH_TOKEN`/`TARGET_BRANCH` to match action's expected interface
- **Devcontainer test fixtures** (`tests/conftest.py`)
  - Shared helpers for `devcontainer_up` and `devcontainer_with_sidecar`: path resolution, env/SSH, project yaml mount, run up, teardown
  - `devcontainer_with_sidecar` scope set to session (one bring-up per session for sidecar tests)
  - Cleanup uses same approach as `just clean-test-containers` (list containers by name, `podman rm -f`) so stacks are torn down reliably
  - Redundant imports removed; fixture logic simplified for maintainability
- **Build process refactoring**
  - Separated build preparation into dedicated `prepare-build.sh` script
  - Handles template replacement, asset copying, and README version updates
  - Improved build script with `--no-cache` flag support and better error handling
- **Development workflow streamlining**
  - Simplified contribution guidelines: removed QEMU build instructions and registry testing complexity
  - Consolidated test commands in justfile for better clarity
  - Updated development setup instructions to reflect simplified workflow
- **Package versions**
  - Updated `ruff` from 0.14.10 to 0.14.11 in test expectations

### Removed

- **Deprecated justfile test recipe and test**
  - Removed deprecated test command from justfile
  - Removed deprecated test for default recipe in justfile (`TestJustIntegration.test_default_recipe_includes_check`)
- **Registry testing infrastructure** (moved to GitHub Actions workflow)
  - Removed `scripts/push.sh` (455 lines) - functionality now in GitHub Actions workflow
  - Removed `tests/test_registry.py` (788 lines) - registry tests now in CI/CD pipeline
  - Removed `scripts/update_readme.py` (80 lines) - README updates handled by workflow
  - Removed `scripts/utils.sh` (75 lines) - utilities consolidated into other scripts
  - Removed `just test-registry` command - no longer needed with automated workflow

### Fixed

- **Multi-platform container builds** in Containerfile
  - Removed default value from `TARGETARCH` ARG to allow Docker BuildKit's automatic platform detection
  - Fixes "Exec format error" when building for different architectures (amd64, arm64)
  - Ensures correct architecture-specific binaries are downloaded during build
- **Image tagging after podman load** in publish workflow
  - Explicitly tag loaded images with expected name format (`ghcr.io/vig-os/devcontainer:VERSION-ARCH`)
  - Fixes test failures where tests couldn't find the image after loading from tar file
  - Ensures proper image availability for testing before publishing
- **GHCR publish workflow push permissions**
  - Authenticate to `ghcr.io` with the repository owner and token context, and set explicit job-level `packages: write` permissions to prevent `403 Forbidden` errors when pushing layers.
- **Sync-issues workflow branch determination logic**
  - Fixed branch selection to prioritize manual `target-branch` input when provided via `workflow_dispatch`
  - Improved branch detection: manual input → PR merge detection → default to `dev`
- **Justfile default recipe conflict**
  - Fixed multiple default recipes issue by moving `help` command to the main justfile
  - Removed default command from `justfile.project` and `justfile.base` to prevent conflicts
  - Updated just recipe tests to handle variable whitespace in command output formatting
- **Invalid docker-compose.project.yaml**
  - Added empty services section to docker-compose.project.yaml to fix YAML validation
- **Python import resolution in tests**
  - Fixed import errors in `tests/test_utils.py` by using `importlib.util` for explicit module loading
  - Improved compatibility with static analysis tools and linters
- **Build script improvements**
  - Fixed shellcheck warnings by properly quoting script paths
  - Improved debug output and error messages

## [0.2.0](https://github.com/vig-os/devcontainer/releases/tag/0.2.0) - 2026-01-06

### Added

- **Automatic version check** for devcontainer updates with DRY & SOLID design
  - Checks GitHub API for new releases and notifies users when updates are available
  - Silent mode with graceful failure (no disruption to workflow)
  - Configurable check interval (default: 24 hours) with spam prevention
  - Mute notifications for specified duration (`just check 7d`, `1w`, `12h`, etc.)
  - Enable/disable toggle (`just check on|off`)
  - One-command update: `just update` downloads install script and updates template files
  - Configuration stored in `.devcontainer/.local/` (gitignored, machine-specific)
  - Auto-runs on `just` default command (can be disabled)
  - Comprehensive test suite (`tests/test_version_check.py`) with 24 tests covering all functionality
- **One-line install script** (`install.sh`) for curl-based devcontainer deployment
  - Auto-detection of podman/docker runtime (prefers podman)
  - Auto-detection and sanitization of project name from folder name (lowercase, underscores)
  - OS-specific installation instructions when runtime is missing (macOS, Ubuntu, Fedora, Arch, Windows)
  - Runtime health check with troubleshooting advice (e.g., "podman machine start" on macOS)
  - Flags: `--force`, `--version`, `--name`, `--dry-run`, `--docker`, `--podman`, `--skip-pull`
- `--no-prompts` flag for `init-workspace.sh` enabling non-interactive/CI usage
- `SHORT_NAME` environment variable support in `init-workspace.sh`
- Test suite for install script (`tests/test_install_script.py`) with unit and integration tests
- `just` as build automation tool (replaces `make`)
- Layered justfile architecture: `justfile.base` (managed), `justfile.project` (team-shared), `justfile.local` (personal)
- Generic sidecar passthrough: `just sidecar <name> <recipe>` for executing commands in sidecar containers
- Documentation generation system (`docs/generate.py`) with Jinja2 templates
- Python project template with `pyproject.toml` and standard structure (`src/`, `tests/`, `docs/`)
- Pre-built Python virtual environment with common dev/science dependencies (numpy, scipy, pandas, matplotlib, pytest, jupyter)
- Auto-sync Python dependencies on container attach via `uv sync`
- `UV_PROJECT_ENVIRONMENT` environment variable for instant venv access without rebuild
- `pip-licenses` pre-commit hook for dependency license compliance checking (blocks GPL-3.0/AGPL-3.0)
- Pre-flight container cleanup check in test suite with helpful error messages
- `just clean-test-containers` recipe for removing lingering test containers
- `PYTEST_AUTO_CLEANUP` environment variable for automatic test container cleanup
- `docker-compose.project.yaml` for team-shared configuration (git-tracked, preserved during upgrades)
- `docker-compose.local.yaml` for personal configuration (git-ignored, preserved during upgrades)
- Build-time manifest generation for optimized placeholder replacement
- `tests/CLEANUP.md` documentation for test container management

### Changed

- `ORG_NAME` now defaults to `"vigOS/devc"` instead of requiring user input
- `init-workspace.sh` now escapes special characters in placeholder values (fixes sed errors with `/` in ORG_NAME)
- Documentation updated with curl-based install as primary quick start method
- **BREAKING**: Replaced `make` with `just` - all build commands now use `just` (e.g., `just test`, `just build`, `just push`)
- **Versioning scheme**: Switched from X.Y format to Semantic Versioning (X.Y.Z format).
All new releases use MAJOR.MINOR.PATCH format (e.g., 0.2.0).
The previous v0.1 release is kept as-is for backwards compatibility.
- **Package versions**: Bumped tool and project versions from previous release:
  - `uv` (0.9.17 → 0.9.21)
  - `gh` (2.83.1 → 2.83.2)
  - `pre-commit` (4.5.0 → 4.5.1)
  - `ruff` (0.14.8 → 0.14.10)
- VS Code Python interpreter now points to pre-built venv (`/root/assets/workspace/.venv`)
- Test container cleanup check runs once at start of `just test` instead of each test phase
- **BREAKING**: Docker Compose file hierarchy now uses `project.yaml` and `local.yaml` instead of `override.yml`
- Socket detection prioritizes Podman over Docker Desktop on macOS and Linux
- `{{TAG}}` placeholder replacement moved to container with build-time manifest generation (significantly faster initialization)
- Socket mount configuration uses environment variable with fallback: `${CONTAINER_SOCKET_PATH:-/var/run/docker.sock}`
- `initialize.sh` writes socket path to `.env` file instead of modifying YAML directly
- `init-workspace.sh` simplified: removed cross-platform `sed` handling (always runs in Linux)

### Removed

- Deprecated `version` field from all Docker Compose files
- `:Z` SELinux flag from socket mounts (incompatible with macOS socket files)
- `docker-compose.override.yml` (replaced by `project.yaml` and `local.yaml`)
- `docker-compose.sidecar.yaml` (merged into main `docker-compose.yml`)

### Fixed

- Test failures from lingering containers between test phases
(now detected and reported before test run; added `PYTEST_SKIP_CONTAINER_CHECK` environment variable)
- Improved error messages for devcontainer startup failures
- SSH commit signing: Changed `user.signingkey` from file path to email identifier to support SSH agent forwarding.
  Git now uses the SSH agent for signing by looking up the email in allowed-signers and matching with the agent key.
- Fixed `gpg.ssh.allowedSignersFile` path to use container path instead of host path after copying git configuration.
- Automatically add git user email to allowed-signers file during setup to ensure commits can be signed and verified.
- macOS Podman socket mounting errors caused by SELinux `:Z` flag on socket files
- Socket detection during tests now matches runtime behavior (Podman-first)

## [0.1](https://github.com/vig-os/devcontainer/releases/tag/0.1) - 2025-12-10

### Core Image

- Development container image based on Python 3.12 (Debian Trixie)
- Multi-architecture support (AMD64, ARM64)
- System tools: git, gh (GitHub CLI), curl, openssh-client, ca-certificates
- Python tools: uv, pre-commit, ruff
- Pre-configured development environment with minimal overhead

### Devcontainer Integration

- VS Code devcontainer template with init-workspace script setting organization and project name
- Docker Compose orchestration for flexible container management
- Support for mounting additional folders via docker-compose.override.yml
- Container lifecycle scripts `post-create.sh`, `initialize.sh` and `post-attach.sh` for seamless development setup
- Automatic Git configuration synchronization from host machine
- SSH commit signing support with signature verification
- Focused `.devcontainer/README.md` with version tracking, lifecycle documentation, and workspace configuration guide
- User-specific `workspace.code-workspace.example` for multi-root VS Code workspaces (actual file is gitignored)

### Testing Infrastructure

- Three-tiered test suite: image tests, integration tests, and registry tests
- Automated testing with pytest and testinfra
- Registry tests with optimized minimal Containerfile (10-20s builds)
- Session-scoped fixtures for efficient test execution
- Comprehensive validation of push/pull/clean workflows
- Tests verify devcontainer README version in pushed images
- Helper function tests for README update utilities

### Automation and Tooling

- Justfile with build, test, push, pull, and clean recipes
- Automated version management and git tagging
- Automatic README.md updates with version and image size during releases
- Push script with multi-architecture builds and registry validation
- Setup script for development environment initialization
- `update_readme.py` helper script for patching README metadata (version, size, development reset)
- Automatic devcontainer README version updates during releases

### Documentation and Templates

- GitHub issue templates (bug report, feature request, task)
- Pull request template with comprehensive checklist
- Complete project documentation (README.md, CONTRIBUTE.md, TESTING.md)
- Detailed testing strategy and workflow documentation
- Push script updates README files in both project and assets
