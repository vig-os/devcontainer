#!/usr/bin/env python3
"""Generate documentation from narrative sources and just help output."""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

import jinja2


def get_just_help():
    """Extract just --list output."""
    try:
        result = subprocess.run(
            ["just", "--list"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error getting just help: {e}", file=sys.stderr)
        return ""


def get_version_from_changelog():
    """Extract version from CHANGELOG.md."""
    changelog = Path(__file__).parent.parent / "CHANGELOG.md"
    if changelog.exists():
        with changelog.open() as f:
            for line in f:
                if line.startswith("## ["):
                    # Extract version from "## [X.Y]" format
                    version = line.split("[")[1].split("]")[0]
                    return version
    return "dev"


def get_image_size():
    """Get approximate image size from Containerfile notes."""
    return "~920 MB"


def generate_docs():
    """Generate documentation from templates."""
    docs_dir = Path(__file__).parent
    root_dir = docs_dir.parent

    # Set up Jinja2 environment
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(docs_dir / "templates"),
        keep_trailing_newline=True,
    )

    # Register helper for including narrative files
    def include_narrative(filename):
        """Include a narrative markdown file."""
        narrative_file = docs_dir / "narrative" / filename
        if narrative_file.exists():
            return narrative_file.read_text()
        return f"<!-- Missing: {filename} -->"

    env.globals["include_narrative"] = include_narrative

    # Context for templates
    context = {
        "project_name": "vigOS Development Environment",
        "just_help_output": get_just_help(),
        "version": get_version_from_changelog(),
        "image_size": get_image_size(),
        "build_date": datetime.now().isoformat(timespec="seconds"),
    }

    # Generate each template
    templates_to_generate = [
        ("README.md.j2", "README.md"),
        ("CONTRIBUTE.md.j2", "CONTRIBUTE.md"),
        ("TESTING.md.j2", "TESTING.md"),
    ]

    for template_name, output_name in templates_to_generate:
        template_path = docs_dir / "templates" / template_name
        if not template_path.exists():
            print(f"Skipping {template_name} (template not found)", file=sys.stderr)
            continue

        try:
            template = env.get_template(template_name)
            output = template.render(**context)

            output_path = root_dir / output_name
            output_path.write_text(output)
            print(f"Generated: {output_name}")
        except Exception as e:
            print(f"Error generating {output_name}: {e}", file=sys.stderr)
            return False

    return True


if __name__ == "__main__":
    success = generate_docs()
    sys.exit(0 if success else 1)
