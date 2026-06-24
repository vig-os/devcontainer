"""Dev-shell / image toolchain parity tests for the Nix flake.

These tests are the TDD anchor for the toolchain SSoT (issue #631). The flake
exposes a single ``devTools`` list; this module reads the per-tool *binary
names* straight from the flake (``nix eval .#devShellTools``) so the test can
never drift from the list it is meant to guard.

For every tool in that SSoT it runs ``nix develop -c <bin> <version-flag>`` and
asserts the command exits 0 inside the dev-shell. This guards against
dev-shell / image drift (the ``EXPECTED_VERSIONS`` problem #27 calls out).

The suite is skipped automatically when ``nix`` is not on PATH (e.g. inside the
podman image CI lane) so it never breaks unrelated jobs.

Refs: #631
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

# Repository root (two levels up: tests/ -> repo root).
REPO_ROOT = Path(__file__).resolve().parent.parent

# Tools whose executable name differs from a plain `<tool> --version` call.
# Default version flag is `--version`; override here when a tool differs.
VERSION_FLAG_OVERRIDES: dict[str, list[str]] = {
    # expect is a Tcl interpreter; it has no --version. `-v` prints the version.
    "expect": ["-v"],
    # tmux uses -V (uppercase) to print its version.
    "tmux": ["-V"],
}

pytestmark = pytest.mark.skipif(
    shutil.which("nix") is None,
    reason="nix is not installed; dev-shell parity tests require Nix",
)


def _nix_env() -> dict[str, str]:
    """Environment for nix invocations with flakes enabled and the public cache."""
    env = os.environ.copy()
    env.setdefault(
        "NIX_CONFIG",
        "experimental-features = nix-command flakes\n"
        "extra-substituters = https://vig-os.cachix.org\n"
        "extra-trusted-public-keys = "
        "vig-os.cachix.org-1:yoOYRi3bvnM6ThxO0joLt7vtzhTfkq3r6jykeUMg7Bk=",
    )
    return env


@pytest.fixture(scope="session")
def current_system() -> str:
    """The Nix system double for the host (e.g. x86_64-linux)."""
    result = subprocess.run(
        ["nix", "eval", "--raw", "--impure", "--expr", "builtins.currentSystem"],
        capture_output=True,
        text=True,
        env=_nix_env(),
        timeout=120,
    )
    if result.returncode != 0:
        pytest.fail("Failed to resolve builtins.currentSystem:\n" + result.stderr)
    return result.stdout.strip()


@pytest.fixture(scope="session")
def dev_shell_env() -> dict[str, str]:
    """Environment variables exported by the Nix dev-shell.

    Runs ``nix develop -c env`` once and parses the result so the UV-bootstrap
    assertions below share a single (slow) shell instantiation.
    """
    result = subprocess.run(
        ["nix", "develop", str(REPO_ROOT), "-c", "env"],
        capture_output=True,
        text=True,
        env=_nix_env(),
        timeout=900,
    )
    if result.returncode != 0:
        pytest.fail("Failed to capture the dev-shell environment:\n" + result.stderr)
    env: dict[str, str] = {}
    for line in result.stdout.splitlines():
        key, sep, value = line.partition("=")
        if sep:
            env[key] = value
    return env


def test_devshell_disables_uv_python_downloads(dev_shell_env: dict[str, str]) -> None:
    """The dev-shell must forbid uv from downloading a managed CPython (#683).

    On a NixOS host a downloaded generic CPython is a dynamically-linked ELF the
    host cannot execute out of the box, so ``uv sync`` (``just init``) aborts.
    ``UV_PYTHON_DOWNLOADS=never`` forces uv to resolve a Nix store interpreter
    instead, mirroring the image path.
    """
    assert dev_shell_env.get("UV_PYTHON_DOWNLOADS") == "never", (
        "UV_PYTHON_DOWNLOADS must be 'never' so uv never fetches a generic "
        f"CPython; got {dev_shell_env.get('UV_PYTHON_DOWNLOADS')!r}"
    )


def test_devshell_uv_python_pins_nix_store_interpreter(
    dev_shell_env: dict[str, str],
) -> None:
    """UV_PYTHON must point at a runnable Nix store CPython 3.14 (#683).

    A store interpreter is patched to the store's loader, so it runs on both
    NixOS and FHS hosts — the cross-host fix for the failed ``uv sync``.
    """
    uv_python = dev_shell_env.get("UV_PYTHON")
    assert uv_python, "UV_PYTHON must be set in the dev-shell"
    assert uv_python.startswith("/nix/store/"), (
        f"UV_PYTHON must be a Nix store interpreter, not {uv_python!r}"
    )
    interpreter = Path(uv_python)
    assert interpreter.is_file() and os.access(interpreter, os.X_OK), (
        f"UV_PYTHON does not point at an executable file: {uv_python}"
    )
    proc = subprocess.run(
        [uv_python, "--version"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0 and "3.14" in proc.stdout, (
        f"UV_PYTHON did not report Python 3.14: rc={proc.returncode} "
        f"stdout={proc.stdout!r} stderr={proc.stderr!r}"
    )


@pytest.fixture(scope="session")
def dev_shell_tools(current_system: str) -> list[str]:
    """Binary names of every tool in the flake's ``devTools`` SSoT."""
    result = subprocess.run(
        ["nix", "eval", "--json", f"{REPO_ROOT}#devShellTools.{current_system}"],
        capture_output=True,
        text=True,
        env=_nix_env(),
        timeout=900,
    )
    if result.returncode != 0:
        pytest.fail("Failed to read devShellTools from the flake:\n" + result.stderr)
    tools = json.loads(result.stdout)
    assert isinstance(tools, list) and tools, "devShellTools must be a non-empty list"
    return tools


def test_devshell_tools_is_superset_of_agent_toolkit(
    dev_shell_tools: list[str],
) -> None:
    """The SSoT must absorb issue #545's agent-CLI toolkit plus claude."""
    required = {
        "rg",
        "fd",
        "bat",
        "eza",
        "delta",
        "lazygit",
        "zoxide",
        "starship",
        "freeze",
        "expect",
        "nvim",
        "claude",
    }
    missing = required - set(dev_shell_tools)
    assert not missing, f"devTools is missing agent-toolkit tools: {sorted(missing)}"


def test_each_tool_runs_in_devshell(dev_shell_tools: list[str]) -> None:
    """Every tool in ``devTools`` is runnable inside ``nix develop``."""
    failures: list[str] = []
    for tool in dev_shell_tools:
        flag = VERSION_FLAG_OVERRIDES.get(tool, ["--version"])
        cmd = ["nix", "develop", str(REPO_ROOT), "-c", tool, *flag]
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=_nix_env(),
            timeout=900,
        )
        if proc.returncode != 0:
            failures.append(
                f"{tool} ({' '.join(flag)}) exited {proc.returncode}: "
                f"{proc.stderr.strip()[:200]}"
            )
    assert not failures, "Tools failed inside nix develop:\n" + "\n".join(failures)
