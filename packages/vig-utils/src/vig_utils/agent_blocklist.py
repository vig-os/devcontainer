"""Compatibility imports for agent blocklist helpers.

Canonical implementation lives in vig_utils.utils.
"""

from vig_utils.utils import contains_agent_fingerprint, load_blocklist

__all__ = ["load_blocklist", "contains_agent_fingerprint"]
