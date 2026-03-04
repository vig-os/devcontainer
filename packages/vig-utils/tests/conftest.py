"""Pytest test-path setup for package-local tests."""

from __future__ import annotations

import sys
from pathlib import Path

vig_utils_src_dir = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(vig_utils_src_dir))
