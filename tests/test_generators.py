"""Tests for claudescan generators."""

from claudescan.generators import generate_agents_md, generate_claude_md, generate_cursorrules


SAMPLE_DATA = {
    "project_name": "test-project",
    "root_path": "/tmp/test-project",
    "languages": [
        {"name": "Python", "percentage": 80.0, "files": 40},
        {"name": "TypeScript", "percentage": 20.0, "files": 10},
    ],
    "frameworks": [
        {"name": "Python", "ecosystem": "Python", "config_file": "pyproject.toml", "specific": "FastAPI"},
        {"name": "Node.js", "ecosystem": "JavaScript/TypeScript", "config_file": "package.json", "specific": "React"},
    ],
    "build_systems": [
        {"name": "Poetry", "command": "poetry build", "lock": "poetry.lock"},
    ],
    "test_frameworks": [
        {"framework": "Pytest", "command": "pytest", "config_file": "pyproject.toml"},
    ],
    "lint_tools": [
        {"name": "Ruff", "config_file": "ruff.toml"},
        {"name": "ESLint", "config_file": ".eslintrc.json"},
    ],
    "git_info": {
        "is_git_repo": True,
        "default_branch": "main",
        "recent_contributors": ["Alice <alice@example.com>", "Bob <bob@example.com>"],
        "commit_count": 150,
        "last_commit_message": "feat: add user authentication",
        "remotes": ["https://github.com/user/repo.git"],
    },
}


def test_generate_claude_md():
    result = generate_claude_md(SAMPLE_DATA)

    # Should contain project name
    assert "# test-project" in result

    # Should contain language info
    assert "Python (80.0%)" in result
    assert "TypeScript (20.0%)" in result

    # Should contain framework info
    assert "FastAPI" in result

    # Should contain build command
    assert "poetry build" in result

    # Should contain test command
    assert "pytest" in result

    # Should contain lint tools
    assert "Ruff" in result
    assert "ESLint" in result

    # Should contain git info
    assert "150 commits" in result
    assert "feat: add user authentication" in result

    # Should contain conventions
    assert "PEP 8" in result
    assert "type hints" in result


def test_generate_agents_md():
    result = generate_agents_md(SAMPLE_DATA)

    # Should contain tech stack
    assert "Python" in result
    assert "FastAPI" in result

    # Should contain command table
    assert "poetry build" in result
    assert "pytest" in result

    # Should contain rules
    assert "Write tests for new features" in result


def test_generate_cursorrules():
    result = generate_cursorrules(SAMPLE_DATA)

    # Should contain system prompt style
    assert "expert AI coding assistant" in result

    # Should contain tech stack
    assert "FastAPI" in result

    # Should contain commands
    assert "poetry build" in result
    assert "pytest" in result

    # Should contain lint tools
    assert "ESLint" in result
    assert "Ruff" in result


def test_generate_claude_md_minimal():
    minimal_data = {
        "project_name": "minimal",
        "root_path": "/tmp/minimal",
        "languages": [],
        "frameworks": [],
        "build_systems": [],
        "test_frameworks": [],
        "lint_tools": [],
        "git_info": {"is_git_repo": False},
    }

    result = generate_claude_md(minimal_data)

    # Should still generate valid output
    assert "# minimal" in result
    assert "Not detected" in result
    assert "No linter detected" in result
    assert "Not a git repository" in result
