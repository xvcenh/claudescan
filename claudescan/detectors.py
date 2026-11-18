"""Detect project metadata from repositories."""

import json
import os
import subprocess
from collections import Counter
from pathlib import Path

# File extension → language name mapping
EXTENSION_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript (React)",
    ".ts": "TypeScript",
    ".tsx": "TypeScript (React)",
    ".rs": "Rust",
    ".go": "Go",
    ".rb": "Ruby",
    ".php": "PHP",
    ".java": "Java",
    ".kt": "Kotlin",
    ".swift": "Swift",
    ".c": "C",
    ".cpp": "C++",
    ".h": "C/C++ Header",
    ".hpp": "C++ Header",
    ".cs": "C#",
    ".scala": "Scala",
    ".ex": "Elixir",
    ".exs": "Elixir Script",
    ".erl": "Erlang",
    ".hs": "Haskell",
    ".lua": "Lua",
    ".r": "R",
    ".m": "Objective-C",
    ".mm": "Objective-C++",
    ".vue": "Vue",
    ".svelte": "Svelte",
    ".astro": "Astro",
    ".sql": "SQL",
    ".sh": "Shell",
    ".bash": "Bash",
    ".zsh": "Zsh",
    ".fish": "Fish",
    ".ps1": "PowerShell",
    ".toml": "TOML",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".json": "JSON",
    ".xml": "XML",
    ".md": "Markdown",
    ".mdx": "MDX",
    ".css": "CSS",
    ".scss": "SCSS",
    ".less": "Less",
    ".html": "HTML",
    ".dockerfile": "Dockerfile",
    ".tf": "Terraform",
    ".proto": "Protobuf",
    ".graphql": "GraphQL",
    ".gql": "GraphQL",
}

IGNORE_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "env",
    "target", "build", "dist", ".next", ".nuxt", ".cache", ".turbo",
    "coverage", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".tox", ".eggs",
}

# Config file → framework detection
FRAMEWORK_CONFIGS = {
    "package.json": {"name": "Node.js", "ecosystem": "JavaScript/TypeScript"},
    "pyproject.toml": {"name": "Python", "ecosystem": "Python"},
    "requirements.txt": {"name": "Python", "ecosystem": "Python"},
    "setup.py": {"name": "Python", "ecosystem": "Python"},
    "setup.cfg": {"name": "Python", "ecosystem": "Python"},
    "Cargo.toml": {"name": "Rust", "ecosystem": "Rust"},
    "go.mod": {"name": "Go", "ecosystem": "Go"},
    "Gemfile": {"name": "Ruby", "ecosystem": "Ruby"},
    "composer.json": {"name": "PHP", "ecosystem": "PHP"},
    "build.gradle": {"name": "Java/Kotlin (Gradle)", "ecosystem": "JVM"},
    "build.gradle.kts": {"name": "Java/Kotlin (Gradle)", "ecosystem": "JVM"},
    "pom.xml": {"name": "Java (Maven)", "ecosystem": "JVM"},
    "mix.exs": {"name": "Elixir", "ecosystem": "Elixir"},
    "CMakeLists.txt": {"name": "C/C++ (CMake)", "ecosystem": "C/C++"},
    "Makefile": {"name": "Make", "ecosystem": "Generic"},
    "Dockerfile": {"name": "Docker", "ecosystem": "Container"},
    "docker-compose.yml": {"name": "Docker Compose", "ecosystem": "Container"},
}

# Specific framework indicators (check inside config files)
FRAMEWORK_INDICATORS = {
    "package.json": {
        "next": "Next.js",
        "react": "React",
        "vue": "Vue.js",
        "svelte": "Svelte",
        "astro": "Astro",
        "express": "Express",
        "fastify": "Fastify",
        "nestjs": "NestJS",
        "electron": "Electron",
        "tauri": "Tauri",
        "django": "Django",
        "flask": "Flask",
        "fastapi": "FastAPI",
    },
}

TEST_FRAMEWORKS = {
    "jest.config.js": {"framework": "Jest", "command": "npx jest"},
    "jest.config.ts": {"framework": "Jest", "command": "npx jest"},
    "vitest.config.js": {"framework": "Vitest", "command": "npx vitest"},
    "vitest.config.ts": {"framework": "Vitest", "command": "npx vitest"},
    "pytest.ini": {"framework": "Pytest", "command": "pytest"},
    "setup.cfg": {"framework": "Pytest", "command": "pytest"},
    "pyproject.toml": {"framework": "Pytest", "command": "pytest"},
    "conftest.py": {"framework": "Pytest", "command": "pytest"},
    "tox.ini": {"framework": "Tox", "command": "tox"},
    "Cargo.toml": {"framework": "Cargo Test", "command": "cargo test"},
    "go.mod": {"framework": "Go Test", "command": "go test ./..."},
    "phpunit.xml": {"framework": "PHPUnit", "command": "phpunit"},
    "rspec": {"framework": "RSpec", "command": "bundle exec rspec"},
    ".rspec": {"framework": "RSpec", "command": "bundle exec rspec"},
}

LINT_TOOLS = {
    ".eslintrc.js": "ESLint",
    ".eslintrc.json": "ESLint",
    ".eslintrc.yaml": "ESLint",
    ".eslintrc.yml": "ESLint",
    ".eslintrc.cjs": "ESLint",
    "eslint.config.js": "ESLint",
    "eslint.config.mjs": "ESLint",
    ".prettierrc": "Prettier",
    ".prettierrc.json": "Prettier",
    ".prettierrc.yaml": "Prettier",
    "prettier.config.js": "Prettier",
    "ruff.toml": "Ruff",
    ".ruff.toml": "Ruff",
    ".flake8": "Flake8",
    ".pylintrc": "Pylint",
    "pylintrc.toml": "Pylint",
    "mypy.ini": "Mypy",
    ".mypy.ini": "Mypy",
    "tsconfig.json": "TypeScript",
    "biome.json": "Biome",
    "biome.jsonc": "Biome",
    ".golangci.yml": "golangci-lint",
    ".golangci.yaml": "golangci-lint",
    "clippy.toml": "Clippy",
    ".clippy.toml": "Clippy",
}


def detect_languages(root_path: str) -> list[dict]:
    """Detect languages used in the project by file extensions."""
    root = Path(root_path)
    counter = Counter()

    for directory, folders, files in os.walk(root):
        folders[:] = [d for d in folders if d not in IGNORE_DIRS and not d.endswith(".egg-info")]
        for filename in files:
            extension = Path(filename).suffix.lower()
            if extension in EXTENSION_MAP and (Path(directory) / filename).is_file():
                counter[EXTENSION_MAP[extension]] += 1

    total = sum(counter.values()) or 1
    return [
        {
            "name": lang,
            "percentage": round(count / total * 100, 1),
            "files": count,
        }
        for lang, count in counter.most_common()
    ]


def _package_data(root: Path) -> dict:
    try:
        value = json.loads((root / "package.json").read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _node_manager(root: Path, package: dict) -> tuple[str, str | None]:
    locks = {
        "npm": ("npm-shrinkwrap.json", "package-lock.json"),
        "yarn": ("yarn.lock",),
        "pnpm": ("pnpm-lock.yaml",),
        "bun": ("bun.lock", "bun.lockb"),
    }
    configured = package.get("packageManager")
    preferred = configured.split("@", 1)[0] if isinstance(configured, str) else None
    for manager in ([preferred] if preferred in locks else locks):
        for filename in locks[manager]:
            if (root / filename).is_file():
                return manager, filename
    return (preferred if preferred in locks else "npm"), None


def _has_script(package: dict, name: str) -> bool:
    scripts = package.get("scripts")
    return isinstance(scripts, dict) and isinstance(scripts.get(name), str) and bool(scripts[name].strip())


def detect_framework(root_path: str) -> list[dict]:
    """Detect frameworks used in the project."""
    root = Path(root_path)
    frameworks = []

    for config_file, info in FRAMEWORK_CONFIGS.items():
        config_path = root / config_file
        if config_path.exists():
            fw = {"name": info["name"], "ecosystem": info["ecosystem"], "config_file": config_file}

            if config_file in FRAMEWORK_INDICATORS:
                package = _package_data(root)
                deps = set()
                for field in ("dependencies", "devDependencies", "peerDependencies"):
                    group = package.get(field)
                    if isinstance(group, dict):
                        deps.update(group)
                for key, fw_name in FRAMEWORK_INDICATORS[config_file].items():
                    if key in deps:
                        fw["specific"] = fw_name
                        break

            frameworks.append(fw)

            # For pyproject.toml, try to detect specific Python framework
            if config_file == "pyproject.toml":
                try:
                    content = config_path.read_text(encoding="utf-8-sig")
                    # Simple string check for framework names
                    for fw_check in ["django", "flask", "fastapi", "litestar"]:
                        if fw_check in content.lower():
                            fw["specific"] = fw_check.title()
                            break
                except UnicodeDecodeError:
                    pass

    return frameworks


def detect_build_system(root_path: str) -> list[dict]:
    """Detect build systems and package managers."""
    root = Path(root_path)
    if (root / "package.json").is_file():
        package = _package_data(root)
        manager, lock = _node_manager(root, package)
        task = "run build" if _has_script(package, "build") else "install"
        name = {"yarn": "Yarn", "bun": "Bun"}.get(manager, manager)
        return [{"name": name, "command": f"{manager} {task}", "lock": lock}]

    systems = []
    build_checks = {
        "pyproject.toml": [
            (root / "uv.lock", {"name": "uv", "command": "uv sync", "lock": "uv.lock"}),
            (root / "poetry.lock", {"name": "Poetry", "command": "poetry build", "lock": "poetry.lock"}),
            (root / "Pipfile.lock", {"name": "Pipenv", "command": "pipenv sync", "lock": "Pipfile.lock"}),
            (None, {"name": "pip", "command": "pip install -e .", "lock": None}),
        ],
        "requirements.txt": [
            (None, {"name": "pip", "command": "pip install -r requirements.txt", "lock": None}),
        ],
        "Cargo.toml": [
            (None, {"name": "Cargo", "command": "cargo build --release", "lock": "Cargo.lock"}),
        ],
        "go.mod": [
            (None, {"name": "Go Modules", "command": "go build ./...", "lock": "go.sum"}),
        ],
        "Makefile": [
            (None, {"name": "Make", "command": "make", "lock": None}),
        ],
        "CMakeLists.txt": [
            (None, {"name": "CMake", "command": "cmake --build build", "lock": None}),
        ],
    }

    for config_file, checks in build_checks.items():
        config_path = root / config_file
        if config_path.exists():
            for lock_path, info in checks:
                if lock_path is None or lock_path.exists():
                    systems.append(info)
                    break
            break  # Only detect primary build system

    return systems


def detect_test_framework(root_path: str) -> list[dict]:
    """Detect test frameworks."""
    root = Path(root_path)
    found = []

    for config_file, info in TEST_FRAMEWORKS.items():
        config_path = root / config_file
        if config_path.exists():
            # For pyproject.toml, check if it has pytest config
            if config_file == "pyproject.toml":
                try:
                    content = config_path.read_text(encoding="utf-8-sig")
                    if "[tool.pytest" not in content and "[tool.coverage" not in content:
                        continue
                except UnicodeDecodeError:
                    continue
            # Deduplicate
            if not any(f["framework"] == info["framework"] for f in found):
                found.append(info)

    package = _package_data(root)
    if _has_script(package, "test"):
        manager, _ = _node_manager(root, package)
        command = f"{manager} run test"
        node_tests = [test for test in found if test["framework"] in ("Jest", "Vitest")]
        found = [dict(test, command=command) if test in node_tests else test for test in found]
        if not node_tests:
            found.append({"framework": "JavaScript", "command": command, "config_file": "package.json"})

    # Check for test directories as fallback
    test_dirs = ["tests", "test", "__tests__", "spec"]
    for td in test_dirs:
        if (root / td).is_dir():
            if not found:
                found.append({"framework": "Unknown", "command": f"run tests in '{td}/'", "config_file": None})
            break

    return found


def detect_lint_tools(root_path: str) -> list[dict]:
    """Detect linting and formatting tools."""
    root = Path(root_path)
    tools = []

    for config_file, tool_name in LINT_TOOLS.items():
        config_path = root / config_file
        if config_path.exists():
            if not any(t["name"] == tool_name for t in tools):
                tools.append({"name": tool_name, "config_file": config_file})

    return tools


def detect_git_info(root_path: str) -> dict:
    """Get git repository information."""
    info = {
        "is_git_repo": False,
        "default_branch": "main",
        "recent_contributors": [],
        "commit_count": 0,
        "last_commit_message": "",
        "remotes": [],
    }

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True, text=True, cwd=root_path, timeout=5
        )
        if result.returncode != 0:
            return info
        info["is_git_repo"] = True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return info

    # Default branch
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, cwd=root_path, timeout=5
        )
        if result.returncode == 0:
            info["default_branch"] = result.stdout.strip()
    except subprocess.TimeoutExpired:
        pass

    # Recent contributors
    try:
        result = subprocess.run(
            ["git", "shortlog", "-sne", "HEAD", "--", ":/"],
            capture_output=True, text=True, cwd=root_path, timeout=5
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n")[:5]:
                if line.strip():
                    # Parse: "  42 Author Name <email>"
                    parts = line.strip().split("\t")
                    if len(parts) == 2:
                        info["recent_contributors"].append(parts[1].strip())
    except subprocess.TimeoutExpired:
        pass

    # Commit count
    try:
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            capture_output=True, text=True, cwd=root_path, timeout=5
        )
        if result.returncode == 0:
            info["commit_count"] = int(result.stdout.strip())
    except (subprocess.TimeoutExpired, ValueError):
        pass

    # Last commit
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--pretty=%s"],
            capture_output=True, text=True, cwd=root_path, timeout=5
        )
        if result.returncode == 0:
            info["last_commit_message"] = result.stdout.strip()
    except subprocess.TimeoutExpired:
        pass

    # Remotes
    try:
        result = subprocess.run(
            ["git", "remote", "-v"],
            capture_output=True, text=True, cwd=root_path, timeout=5
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if "(fetch)" in line:
                    url = line.split()[1]
                    info["remotes"].append(url)
    except subprocess.TimeoutExpired:
        pass

    return info


def get_project_name(root_path: str) -> str:
    """Determine the project name from config files or directory name."""
    root = Path(root_path)

    # Check pyproject.toml
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text(encoding="utf-8-sig")
            for line in content.split("\n"):
                line = line.strip()
                if line.startswith("name") and "=" in line:
                    name = line.split("=", 1)[1].strip().strip('"').strip("'")
                    return name
        except UnicodeDecodeError:
            pass

    # Check package.json
    package_name = _package_data(root).get("name")
    if isinstance(package_name, str) and package_name.strip():
        return package_name.strip()

    # Check Cargo.toml
    cargo_toml = root / "Cargo.toml"
    if cargo_toml.exists():
        try:
            content = cargo_toml.read_text(encoding="utf-8-sig")
            for line in content.split("\n"):
                line = line.strip()
                if line.startswith("name") and "=" in line:
                    name = line.split("=", 1)[1].strip().strip('"').strip("'")
                    return name
        except UnicodeDecodeError:
            pass

    # Check go.mod
    go_mod = root / "go.mod"
    if go_mod.exists():
        try:
            content = go_mod.read_text(encoding="utf-8-sig")
            for line in content.split("\n"):
                line = line.strip()
                if line.startswith("module "):
                    return line.split()[1]
        except UnicodeDecodeError:
            pass

    # Fall back to directory name
    return root.resolve().name
