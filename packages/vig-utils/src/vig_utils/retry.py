#!/usr/bin/env python3
"""Retry CLI for transient command failures with bounded exponential backoff.

Use `uv run retry -- ...` on bare runners that execute within the repository's
Python environment, or `retry -- ...` in devcontainer jobs where the command is
already available on PATH.
"""

from __future__ import annotations

import subprocess
import sys
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


def _execution_error_exit_code(error: OSError) -> int:
    if isinstance(error, FileNotFoundError):
        return 127
    if isinstance(error, PermissionError):
        return 126
    return 1


def _parse_positive_int(value: str, option_name: str) -> int:
    if not value.isdigit() or int(value) <= 0:
        raise ValueError(f"retry: {option_name} must be a positive integer")
    return int(value)


def parse_cli(argv: Sequence[str]) -> tuple[int, int, int, list[str]]:
    """Parse retry options and command from argv (without program name)."""
    retries = 3
    backoff = 5
    max_backoff = 60
    command_start = None
    i = 0

    while i < len(argv):
        arg = argv[i]
        if arg == "--":
            command_start = i + 1
            break
        if arg == "--retries":
            if i + 1 >= len(argv):
                raise ValueError("retry: missing value for '--retries'")
            retries = _parse_positive_int(argv[i + 1], "--retries")
            i += 2
            continue
        if arg == "--backoff":
            if i + 1 >= len(argv):
                raise ValueError("retry: missing value for '--backoff'")
            backoff = _parse_positive_int(argv[i + 1], "--backoff")
            i += 2
            continue
        if arg == "--max-backoff":
            if i + 1 >= len(argv):
                raise ValueError("retry: missing value for '--max-backoff'")
            max_backoff = _parse_positive_int(argv[i + 1], "--max-backoff")
            i += 2
            continue
        raise ValueError(f"retry: unknown option '{arg}'")

    if command_start is None or command_start >= len(argv):
        raise ValueError("retry: missing command after '--'")

    return retries, backoff, max_backoff, list(argv[command_start:])


def retry_command(
    command: list[str],
    *,
    retries: int,
    backoff: int,
    max_backoff: int,
) -> int:
    """Run command with bounded exponential retry."""
    command_display = " ".join(command)
    exit_code = 0
    for attempt in range(1, retries + 1):
        try:
            result = subprocess.run(
                command,
                stdin=sys.stdin,
                stdout=sys.stdout,
                stderr=sys.stderr,
                check=False,
            )
        except OSError as error:
            print(
                f"retry: failed to execute command: {command_display} ({error})",
                file=sys.stderr,
            )
            return _execution_error_exit_code(error)
        if result.returncode == 0:
            return 0
        exit_code = result.returncode

        if attempt == retries:
            print(
                f"Command failed after {retries}/{retries} attempts (exit: {exit_code})",
                file=sys.stderr,
            )
            return exit_code

        wait_seconds = min(backoff * (1 << (attempt - 1)), max_backoff)
        print(
            f"Attempt {attempt}/{retries} failed (exit: {exit_code}); retrying in {wait_seconds}s...",
            file=sys.stderr,
        )
        time.sleep(wait_seconds)
    return exit_code


def main() -> int:
    try:
        retries, backoff, max_backoff, command = parse_cli(sys.argv[1:])
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2

    return retry_command(
        command,
        retries=retries,
        backoff=backoff,
        max_backoff=max_backoff,
    )


if __name__ == "__main__":
    sys.exit(main())
