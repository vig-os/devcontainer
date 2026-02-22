#!/usr/bin/env python3
"""Build Cursor/VS Code nested authority URI for remote devcontainers."""

from __future__ import annotations

import json


def hex_encode(s: str) -> str:
    """Hex-encode a string (UTF-8)."""
    return s.encode().hex()


def build_uri(
    workspace_path: str,
    devcontainer_path: str,
    ssh_host: str,
    container_workspace: str,
) -> str:
    """Build vscode-remote URI for dev-container over SSH.

    Format: vscode-remote://dev-container+{DC_HEX}@ssh-remote+{SSH_SPEC}/{container_workspace}
    """
    spec = {
        "settingType": "config",
        "workspacePath": workspace_path,
        "devcontainerPath": devcontainer_path,
    }
    dc_hex = hex_encode(json.dumps(spec, separators=(",", ":")))
    path = "/" + container_workspace.lstrip("/")
    return f"vscode-remote://dev-container+{dc_hex}@ssh-remote+{ssh_host}{path}"
