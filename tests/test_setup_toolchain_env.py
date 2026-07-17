"""Behavior tests: direnv-mode shellHook env forwarding in setup-devkit-toolchain.

Issue #1180: the direnv-mode CI preamble exports the dev-shell store bin dirs to
``GITHUB_PATH`` but dropped every environment variable a project's flake
``shellHook`` exports, so env defaults that exist in every local
``nix develop``/direnv session silently vanished on CI (proven in
vig-os/org-config#40, where a shellHook-seeded ``OTTERDOG_TOKEN`` placeholder
worked locally and failed on CI).

The fix diffs the ambient environment against the dev-shell environment (the
shellHook has run inside ``nix develop``) and forwards the vars the dev-shell
adds or changes to ``GITHUB_ENV``, minus a denylist of shell session state and
Nix/stdenv build machinery that must never leak into the CI environment.

These tests execute the "Build repo flake dev-shell and export PATH" step's real
``run:`` script against a stubbed ``nix`` that emits a simulated dev-shell
environment, then assert on the ``GITHUB_ENV`` the script wrote — the same
executed-bash pattern as ``test_ci_runner.py``.

Refs: #1180
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
import yaml

# Repository root (tests/ -> repo root).
REPO_ROOT = Path(__file__).resolve().parent.parent
ACTION = (
    REPO_ROOT
    / "assets"
    / "workspace"
    / ".github"
    / "actions"
    / "setup-devkit-toolchain"
    / "action.yml"
)

# The direnv step under test.
DEVSHELL_STEP_NAME = "Build repo flake dev-shell and export PATH"

# The simulated dev-shell environment the stub `nix` emits (null-delimited). It
# mixes shellHook exports (must forward), Nix/stdenv build machinery (must be
# denied), shell session state (must be denied), and an ambient var unchanged
# from the host env (must be filtered out, never re-forwarded — this is how host
# secrets stay out of GITHUB_ENV).
_DEVSHELL_ENV = [
    ("OTTERDOG_TOKEN", "placeholder-set-by-shellhook"),
    ("PROJECT_GREETING", "hello world"),
    ("MULTILINE_VAR", "line-one\nline-two\nline-three"),
    # Nix/stdenv build machinery — every one must be denied.
    ("buildInputs", "/nix/store/xxxxxxxx-foo"),
    ("nativeBuildInputs", "/nix/store/yyyyyyyy-bar"),
    ("stdenv", "/nix/store/zzzzzzzz-stdenv-linux"),
    ("shellHook", "export OTTERDOG_TOKEN=placeholder-set-by-shellhook"),
    ("out", "/nix/store/oooooooo-out"),
    ("system", "x86_64-linux"),
    ("NIX_CFLAGS_COMPILE", "-isystem /nix/store/aaa/include"),
    ("NIX_BUILD_CORES", "4"),
    ("dontUnpack", "1"),
    ("configurePhase", ":"),
    ("depsBuildBuild", ""),
    # Shell session state — must be denied.
    ("PATH", "/nix/store/aaaaaaaa-foo/bin:/usr/bin"),
    ("HOME", "/home/dev-shell"),
    ("SHLVL", "2"),
    ("TMPDIR", "/tmp/nix-shell"),
    # Ambient var, unchanged from the host env — must not be re-forwarded.
    ("AMBIENT_SHARED", "same-on-both-sides"),
]


def _devshell_step_script() -> str:
    action = yaml.safe_load(ACTION.read_text(encoding="utf-8"))
    for step in action["runs"]["steps"]:
        if step.get("name") == DEVSHELL_STEP_NAME:
            return step["run"]
    raise AssertionError(f"step {DEVSHELL_STEP_NAME!r} not found in {ACTION}")


def _write_nix_stub(bin_dir: Path) -> None:
    """A fake `nix` covering every invocation the devshell step makes.

    - `nix develop … --command true`                  -> exit 0 (profile build)
    - `nix develop … --command bash -c 'printf … PATH'`-> a fake store PATH
    - `nix develop … --command bash -c '… UV_… '`      -> the uv-download URL
    - `nix develop … --command env …`                  -> the simulated env dump
    """
    bin_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "# Collect the command after `--command`.",
        "cmd=()",
        "found=0",
        'for a in "$@"; do',
        '  if [ "$found" = 1 ]; then cmd+=("$a"); fi',
        '  if [ "$a" = "--command" ]; then found=1; fi',
        "done",
        'joined="${cmd[*]:-}"',
        'if [ "${cmd[0]:-}" = "true" ]; then exit 0; fi',
        'if [ "${cmd[0]:-}" = "env" ]; then',
    ]
    for name, value in _DEVSHELL_ENV:
        lines.append(f"  printf '%s\\0' {_bash_squote(name + '=' + value)}")
    lines += [
        "  exit 0",
        "fi",
        'case "$joined" in',
        '  *"printf \\"%s\\" \\"\\$PATH\\""*)',
        "    printf '%s' '/nix/store/aaaaaaaa-foo/bin:/nix/store/bbbbbbbb-bar/bin:/usr/bin'; exit 0 ;;",
        "  *UV_PYTHON_DOWNLOADS_JSON_URL*)",
        "    printf 'UV_PYTHON_DOWNLOADS_JSON_URL=https://example.invalid/downloads.json\\n'; exit 0 ;;",
        "esac",
        "exit 0",
    ]
    stub = bin_dir / "nix"
    stub.write_text("\n".join(lines) + "\n", encoding="utf-8")
    stub.chmod(0o755)


def _bash_squote(s: str) -> str:
    """Single-quote a string for safe embedding in the generated bash stub."""
    return "'" + s.replace("'", "'\\''") + "'"


def _run_devshell_step(tmp_path: Path) -> dict[str, str]:
    """Execute the devshell step and return the parsed GITHUB_ENV map.

    Multi-line heredoc values are collapsed with `\\n` joins so a caller can
    assert on them; the presence of a heredoc is asserted separately on the raw
    text where it matters.
    """
    script = _devshell_step_script()

    bin_dir = tmp_path / "stub-bin"
    _write_nix_stub(bin_dir)

    github_env = tmp_path / "github_env"
    github_path = tmp_path / "github_path"
    runner_temp = tmp_path / "runner_temp"
    github_env.touch()
    github_path.touch()
    runner_temp.mkdir()

    env = {
        **os.environ,
        "PATH": f"{bin_dir}:{os.environ['PATH']}",
        "GITHUB_ENV": str(github_env),
        "GITHUB_PATH": str(github_path),
        "RUNNER_TEMP": str(runner_temp),
        # Ambient var that the dev-shell leaves unchanged: must be filtered out.
        "AMBIENT_SHARED": "same-on-both-sides",
    }

    proc = subprocess.run(
        ["bash", "-c", script],
        cwd=tmp_path,  # no pyproject.toml -> non-Python consumer path
        env=env,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, (
        f"devshell step failed:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
    )
    return _parse_github_env(github_env.read_text(encoding="utf-8"))


def _parse_github_env(text: str) -> dict[str, str]:
    """Parse GITHUB_ENV supporting both `KEY=value` and heredoc blocks."""
    out: dict[str, str] = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if "<<" in line and "=" not in line.split("<<", 1)[0]:
            name, _, delim = line.partition("<<")
            i += 1
            body: list[str] = []
            while i < len(lines) and lines[i] != delim:
                body.append(lines[i])
                i += 1
            out[name] = "\n".join(body)
            i += 1  # skip the closing delimiter
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            out[key] = value
        i += 1
    return out


# ── Behavior ─────────────────────────────────────────────────────────────────


def test_shellhook_scalar_exports_are_forwarded(tmp_path: Path) -> None:
    """Plain shellHook exports reach GITHUB_ENV (the org-config#40 regression)."""
    env = _run_devshell_step(tmp_path)
    assert env.get("OTTERDOG_TOKEN") == "placeholder-set-by-shellhook"
    assert env.get("PROJECT_GREETING") == "hello world"


def test_multiline_value_survives_via_heredoc(tmp_path: Path) -> None:
    """A multi-line export is forwarded intact using the GITHUB_ENV heredoc."""
    env = _run_devshell_step(tmp_path)
    assert env.get("MULTILINE_VAR") == "line-one\nline-two\nline-three"


@pytest.mark.parametrize(
    "denied",
    [
        # Nix/stdenv build machinery.
        "buildInputs",
        "nativeBuildInputs",
        "stdenv",
        "shellHook",
        "out",
        "system",
        "NIX_CFLAGS_COMPILE",
        "NIX_BUILD_CORES",
        "dontUnpack",
        "configurePhase",
        "depsBuildBuild",
        # Shell session state.
        "PATH",
        "HOME",
        "SHLVL",
        "TMPDIR",
    ],
)
def test_denylisted_vars_are_not_forwarded(tmp_path: Path, denied: str) -> None:
    """Build machinery and shell session state never leak into GITHUB_ENV."""
    env = _run_devshell_step(tmp_path)
    assert denied not in env, f"{denied} must not be forwarded to GITHUB_ENV"


def test_unchanged_ambient_var_is_not_reforwarded(tmp_path: Path) -> None:
    """A var identical to the host env is filtered — host secrets never re-leak."""
    env = _run_devshell_step(tmp_path)
    assert "AMBIENT_SHARED" not in env
