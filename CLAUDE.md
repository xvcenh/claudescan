# claudescan

## Overview

- **Languages:** Python (75.0%), Markdown (8.3%), TOML (8.3%), YAML (8.3%)
- **Frameworks:** Python
- **Build system:** pip
- **Git:** 0 commits on `main`

## Commands

### Build & Run

```bash
pip install -e .
```

### Testing

```bash
run tests in 'tests/'
```

### Linting & Formatting

No linter detected.

## Code Conventions

### Python Style

- Follow PEP 8 style guide
- Use type hints for all function signatures
- Docstrings in Google or NumPy style
- Maximum line length: 100 characters
- Use `pathlib.Path` over `os.path`
- Prefer f-strings over `.format()` or `%` formatting
- Use `dataclasses` or `pydantic` for data structures

### General

- Keep files under 500 lines when possible
- Write clear commit messages
- Add comments only when necessary (why, not what)
- Break complex logic into smaller, testable functions
- Use meaningful variable and function names

## Project Structure

```
claudescan/
├── src/           # Source code
├── tests/         # Test files
├── docs/          # Documentation
├── scripts/       # Utility scripts
├── pyproject.toml    # Project configuration
└── README.md
```

_Run `claudescan --structure` to see the actual directory tree._

## Git Workflow

- Default branch: `main`
- Create feature branches from `{branch}`
- Use conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- Keep PRs small and focused
- Squash merges preferred for feature branches
