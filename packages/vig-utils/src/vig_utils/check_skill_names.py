#!/usr/bin/env python3
"""Entry point wrapper for packaged check-skill-names shell helper."""

from __future__ import annotations

import sys

from vig_utils.utils import run_packaged_shell


def main() -> int:
    return run_packaged_shell("check-skill-names.sh")


if __name__ == "__main__":
    sys.exit(main())
