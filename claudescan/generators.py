"""Generate AI agent config files (CLAUDE.md, AGENTS.md, .cursorrules)."""

from textwrap import dedent
from typing import Any


def generate_claude_md(data: dict[str, Any]) -> str:
    """Generate a CLAUDE.md file from project metadata."""
    sections = []

    # Header
    name = data.get("project_name", "Project")
    sections.append(f"# {name}\n")

    # Project overview
    sections.append(_build_overview(data))

    # Build & run commands
    sections.append(_build_commands(data))

    # Test commands
    sections.append(_build_test_commands(data))

    # Lint & format
    sections.append(_build_lint_commands(data))

    # Code style & conventions
    sections.append(_build_conventions(data))

    # Project structure
    sections.append(_build_structure(data))

    # Git workflow
    sections.append(_build_git_workflow(data))

    return "\n".join(sections)


def generate_agents_md(data: dict[str, Any]) -> str:
    """Generate an AGENTS.md file (Cursor/Codex format)."""
    sections = []

    name = data.get("project_name", "Project")
    sections.append(f"# {name} — Agent Configuration\n")

    # Tech stack summary
    sections.append(_build_tech_stack(data))

    # Commands quick reference
    sections.append(_build_commands_quickref(data))

    # Project-specific rules
    sections.append(_build_rules(data))

    return "\n".join(sections)


def generate_cursorrules(data: dict[str, Any]) -> str:
    """Generate .cursorrules content."""
    lines = ["You are an expert AI coding assistant working on this project.", ""]

    # Tech stack
    frameworks = data.get("frameworks", [])
    if frameworks:
        fw_names = [f["name"] for f in frameworks]
        lines.append(f"Tech stack: {', '.join(fw_names)}.")
        specific = [f["specific"] for f in frameworks if f.get("specific")]
        if specific:
            lines.append(f"Frameworks: {', '.join(specific)}.")
        lines.append("")

    # Languages
    languages = data.get("languages", [])
    if languages:
        main_lang = languages[0]["name"]
        lines.append(f"Primary language: {main_lang}.")
        lines.append("")

    # Build rules
    build = data.get("build_systems", [])
    if build:
        lines.append(f"Build command: `{build[0]['command']}`")
        lines.append("")

    # Test rules
    tests = data.get("test_frameworks", [])
    if tests:
        lines.append(f"Test command: `{tests[0]['command']}`")
        lines.append("Always run tests before committing changes.")
        lines.append("")

    # Code style
    linters = data.get("lint_tools", [])
    if linters:
        lint_names = [t["name"] for t in linters]
        lines.append(f"Linting/formatting: {', '.join(lint_names)}.")
        lines.append("Follow the existing code style in the project.")
        lines.append("")

    return "\n".join(lines)


def _build_overview(data: dict[str, Any]) -> str:
    """Build project overview section."""
    lines = ["## Overview", ""]

    languages = data.get("languages", [])
    if languages:
        lang_str = ", ".join(
            f"{l['name']} ({l['percentage']}%)"
            for l in languages[:5]
        )
        lines.append(f"- **Languages:** {lang_str}")
    else:
        lines.append("- **Languages:** Not detected")

    frameworks = data.get("frameworks", [])
    if frameworks:
        fw_info = []
        for f in frameworks:
            label = f["name"]
            if f.get("specific"):
                label += f" ({f['specific']})"
            fw_info.append(label)
        lines.append(f"- **Frameworks:** {', '.join(fw_info)}")

    build = data.get("build_systems", [])
    if build:
        lines.append(f"- **Build system:** {build[0]['name']}")

    git = data.get("git_info", {})
    if git.get("is_git_repo"):
        lines.append(f"- **Git:** {git.get('commit_count', 0)} commits on `{git.get('default_branch', 'main')}`")

    lines.append("")
    return "\n".join(lines)


def _build_commands(data: dict[str, Any]) -> str:
    """Build build/run commands section."""
    lines = ["## Commands", ""]

    build = data.get("build_systems", [])
    if build:
        lines.append("### Build & Run")
        lines.append("")
        for b in build:
            lines.append(f"```bash\n{b['command']}\n```")
            lines.append("")

    return "\n".join(lines)


def _build_test_commands(data: dict[str, Any]) -> str:
    """Build test commands section."""
    lines = ["### Testing", ""]

    tests = data.get("test_frameworks", [])
    if tests:
        for t in tests:
            lines.append(f"```bash\n{t['command']}\n```")
            lines.append("")
    else:
        lines.append("No test framework detected.")
        lines.append("")

    return "\n".join(lines)


def _build_lint_commands(data: dict[str, Any]) -> str:
    """Build lint/format commands section."""
    lines = ["### Linting & Formatting", ""]

    linters = data.get("lint_tools", [])
    if linters:
        for l in linters:
            lines.append(f"- **{l['name']}** (`{l.get('config_file', 'N/A')}`)")
        lines.append("")
        # Generate common commands
        lint_names = [l["name"] for l in linters]
        if "ESLint" in lint_names:
            lines.append("```bash\nnpx eslint .\n```")
            lines.append("")
        if "Prettier" in lint_names:
            lines.append("```bash\nnpx prettier --check .\n```")
            lines.append("")
        if "Ruff" in lint_names:
            lines.append("```bash\nruff check .\nruff format --check .\n```")
            lines.append("")
        if "Biome" in lint_names:
            lines.append("```bash\nnpx biome check .\n```")
            lines.append("")
    else:
        lines.append("No linter detected.")
        lines.append("")

    return "\n".join(lines)


def _build_conventions(data: dict[str, Any]) -> str:
    """Build code conventions section with smart defaults."""
    lines = ["## Code Conventions", ""]

    languages = data.get("languages", [])
    if not languages:
        return "\n".join(lines + ["_Add project-specific conventions here._", ""])

    main_lang = languages[0]["name"]
    lines.append(f"### {main_lang} Style")
    lines.append("")

    # Language-specific conventions
    if main_lang == "Python":
        lines.extend([
            "- Follow PEP 8 style guide",
            "- Use type hints for all function signatures",
            "- Docstrings in Google or NumPy style",
            "- Maximum line length: 100 characters",
            "- Use `pathlib.Path` over `os.path`",
            "- Prefer f-strings over `.format()` or `%` formatting",
            "- Use `dataclasses` or `pydantic` for data structures",
            "",
        ])
    elif main_lang in ("TypeScript", "TypeScript (React)"):
        lines.extend([
            "- Use strict TypeScript mode",
            "- Prefer interfaces over type aliases for object shapes",
            "- Use `const` assertions for literal types",
            "- Avoid `any` — use `unknown` when type is uncertain",
            "- Use async/await over raw promises",
            "",
        ])
    elif main_lang in ("JavaScript", "JavaScript (React)"):
        lines.extend([
            "- Use ES6+ syntax (const/let, arrow functions, destructuring)",
            "- Prefer async/await over callbacks",
            "- Use template literals for string interpolation",
            "- Single quotes for strings, semicolons required",
            "",
        ])
    elif main_lang == "Rust":
        lines.extend([
            "- Follow standard Rust style (rustfmt)",
            "- Use `clippy` for linting",
            "- Prefer `&str` over `String` for function parameters",
            "- Use `Result` and `Option` — avoid `unwrap()` in production code",
            "- Derive common traits (`Debug`, `Clone`, `Serialize`, `Deserialize`)",
            "",
        ])
    elif main_lang == "Go":
        lines.extend([
            "- Follow Effective Go guidelines",
            "- Use `gofmt` for formatting",
            "- Handle errors explicitly — never ignore them",
            "- Use interfaces sparingly, prefer concrete types",
            "- Package names should be short and lowercase",
            "",
        ])
    else:
        lines.extend([
            "- Follow the standard style guide for this language",
            "- Keep functions small and focused",
            "- Write self-documenting code with clear variable names",
            "",
        ])

    # General conventions
    lines.extend([
        "### General",
        "",
        "- Keep files under 500 lines when possible",
        "- Write clear commit messages",
        "- Add comments only when necessary (why, not what)",
        "- Break complex logic into smaller, testable functions",
        "- Use meaningful variable and function names",
        "",
    ])

    return "\n".join(lines)


def _build_structure(data: dict[str, Any]) -> str:
    """Build project structure section."""
    lines = ["## Project Structure", ""]
    lines.append("```")
    lines.append(f"{data.get('project_name', 'project')}/")
    lines.append("├── src/           # Source code")
    lines.append("├── tests/         # Test files")
    lines.append("├── docs/          # Documentation")
    lines.append("├── scripts/       # Utility scripts")

    frameworks = data.get("frameworks", [])
    for fw in frameworks:
        if fw.get("config_file"):
            lines.append(f"├── {fw['config_file']}    # Project configuration")

    lines.append("└── README.md")
    lines.append("```")
    lines.append("")
    lines.append("_Run `claudescan --structure` to see the actual directory tree._")
    lines.append("")

    return "\n".join(lines)


def _build_git_workflow(data: dict[str, Any]) -> str:
    """Build git workflow section."""
    lines = ["## Git Workflow", ""]

    git = data.get("git_info", {})
    if not git.get("is_git_repo"):
        lines.append("Not a git repository.")
        lines.append("")
        return "\n".join(lines)

    branch = git.get("default_branch", "main")
    lines.extend([
        f"- Default branch: `{branch}`",
        "- Create feature branches from `{branch}`",
        "- Use conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`",
        "- Keep PRs small and focused",
        "- Squash merges preferred for feature branches",
        "",
    ])

    contributors = git.get("recent_contributors", [])
    if contributors:
        lines.append("### Contributors")
        lines.append("")
        for c in contributors[:3]:
            lines.append(f"- {c}")
        lines.append("")

    last_commit = git.get("last_commit_message", "")
    if last_commit:
        lines.append(f"**Latest commit:** _{last_commit}_")
        lines.append("")

    return "\n".join(lines)


def _build_tech_stack(data: dict[str, Any]) -> str:
    """Build tech stack section for AGENTS.md."""
    lines = ["## Tech Stack", ""]

    languages = data.get("languages", [])
    if languages:
        lang = languages[0]["name"]
        lines.append(f"- **Language:** {lang}")
        if len(languages) > 1:
            others = ", ".join(l["name"] for l in languages[1:3])
            lines.append(f"- **Other:** {others}")

    frameworks = data.get("frameworks", [])
    if frameworks:
        fw_names = [f.get("specific") or f["name"] for f in frameworks]
        lines.append(f"- **Frameworks:** {', '.join(fw_names)}")

    build = data.get("build_systems", [])
    if build:
        lines.append(f"- **Build:** {build[0]['name']} → `{build[0]['command']}`")

    lines.append("")
    return "\n".join(lines)


def _build_commands_quickref(data: dict[str, Any]) -> str:
    """Build commands quick reference for AGENTS.md."""
    lines = ["## Commands", ""]
    lines.append("| Task | Command |")
    lines.append("|------|---------|")

    build = data.get("build_systems", [])
    if build:
        lines.append(f"| Build | `{build[0]['command']}` |")

    tests = data.get("test_frameworks", [])
    if tests:
        lines.append(f"| Test | `{tests[0]['command']}` |")

    linters = data.get("lint_tools", [])
    if linters and linters[0]["name"] == "ESLint":
        lines.append(f"| Lint | `npx eslint .` |")
    elif linters and linters[0]["name"] == "Ruff":
        lines.append(f"| Lint | `ruff check .` |")

    lines.append("")
    return "\n".join(lines)


def _build_rules(data: dict[str, Any]) -> str:
    """Build project-specific rules for AGENTS.md."""
    lines = ["## Rules", ""]

    languages = data.get("languages", [])
    main_lang = languages[0]["name"] if languages else ""

    rules = ["- Write tests for new features", "- Follow existing code style"]

    if main_lang == "Python":
        rules.append("- Use type hints on all new functions")
        rules.append("- Import order: stdlib → third-party → local")
    elif main_lang in ("TypeScript", "TypeScript (React)"):
        rules.append("- Use strict TypeScript — no `any`")
        rules.append("- Prefer functional components with hooks")
    elif main_lang == "Rust":
        rules.append("- Handle all `Result` and `Option` variants")
        rules.append("- Run `cargo clippy` before committing")

    for rule in rules:
        lines.append(rule)

    lines.append("")
    return "\n".join(lines)
