#!/usr/bin/env python3
"""Compatibility shim for utilities migrated to vig-utils."""

from __future__ import annotations

from vig_utils.utils import (
    main,
    parse_args,
    sed_inplace,
    substitute_in_file,
    update_version_line,
)

__all__ = [
    "substitute_in_file",
    "sed_inplace",
    "update_version_line",
    "parse_args",
    "main",
]


if __name__ == "__main__":
    main()
