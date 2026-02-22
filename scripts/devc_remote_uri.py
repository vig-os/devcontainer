#!/usr/bin/env python3
"""
Stub for devcontainer remote URI construction.

Returns a placeholder URI for testing. Full implementation in sibling sub-issue.
Accepts --ssh-host and --path.
"""

import argparse
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ssh-host", required=True)
    parser.add_argument("--path", required=True)
    args = parser.parse_args()
    # Placeholder URI for orchestration flow testing
    uri = f"vscode-remote://dev-container+placeholder@ssh-remote+{args.ssh_host}/{args.path}"
    print(uri)
    return 0


if __name__ == "__main__":
    sys.exit(main())
