"""Load and check content against AI agent identity blocklist.

Single source of truth: .github/agent-blocklist.toml
Refs: #163
"""

from __future__ import annotations

import re
from pathlib import Path  # noqa: TC003 - Path used at runtime in path.open()


def load_blocklist(path: Path) -> dict:
    """Load blocklist from TOML file. Returns dict with keys: trailers, names, emails."""
    import tomllib

    with path.open("rb") as f:
        data = tomllib.load(f)
    patterns = data.get("patterns", {})
    return {
        "trailers": [re.compile(p) for p in patterns.get("trailers", [])],
        "names": [s.lower() for s in patterns.get("names", [])],
        "emails": [s.lower() for s in patterns.get("emails", [])],
    }


def contains_agent_fingerprint(
    content: str,
    blocklist: dict,
    *,
    check_trailers: bool = True,
) -> str | None:
    """Check if content contains any blocklisted pattern.

    Returns the first matching pattern string if found, else None.
    """
    content_lower = content.lower()
    for name in blocklist.get("names", []):
        if name in content_lower:
            return name
    for email in blocklist.get("emails", []):
        if email in content_lower:
            return email
    if check_trailers:
        for line in content.splitlines():
            for pattern_re in blocklist.get("trailers", []):
                if pattern_re.match(line.strip()):
                    return line.strip()
    return None
