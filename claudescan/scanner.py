"""Orchestrate the scanning and generation process."""

from pathlib import Path
from typing import Any

from .detectors import (
    detect_build_system,
    detect_framework,
    detect_git_info,
    detect_languages,
    detect_lint_tools,
    detect_test_framework,
    get_project_name,
)
from .generators import generate_agents_md, generate_claude_md, generate_cursorrules


def scan_project(root_path: str) -> dict[str, Any]:
    """Scan a project directory and return all metadata."""
    root = Path(root_path).resolve()
    if not root.exists():
        raise FileNotFoundError(f"Directory not found: {root_path}")
    if not root.is_dir():
        raise NotADirectoryError(f"Not a directory: {root_path}")

    data: dict[str, Any] = {
        "project_name": get_project_name(str(root)),
        "root_path": str(root),
        "languages": detect_languages(str(root)),
        "frameworks": detect_framework(str(root)),
        "build_systems": detect_build_system(str(root)),
        "test_frameworks": detect_test_framework(str(root)),
        "lint_tools": detect_lint_tools(str(root)),
        "git_info": detect_git_info(str(root)),
    }

    return data


def generate_output(data: dict[str, Any], format_type: str = "claude") -> str:
    """Generate the output in the specified format.

    Args:
        data: Project metadata from scan_project()
        format_type: One of 'claude', 'agents', 'cursorrules'

    Returns:
        Generated markdown/text content
    """
    generators = {
        "claude": generate_claude_md,
        "agents": generate_agents_md,
        "cursorrules": generate_cursorrules,
    }

    if format_type not in generators:
        raise ValueError(f"Unknown format: {format_type}. Choose from: {', '.join(generators.keys())}")

    return generators[format_type](data)
