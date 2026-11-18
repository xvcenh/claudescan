"""Tests for claudescan detectors."""

import json
import tempfile
from pathlib import Path

from claudescan.detectors import (
    detect_build_system,
    detect_framework,
    detect_git_info,
    detect_languages,
    detect_lint_tools,
    detect_test_framework,
    get_project_name,
)


def test_detect_languages_python():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "main.py").write_text("print('hello')")
        (root / "utils.py").write_text("def foo(): pass")
        (root / "config.py").write_text("DEBUG = True")
        (root / "README.md").write_text("# Project")

        result = detect_languages(str(root))
        lang_names = [l["name"] for l in result]

        assert "Python" in lang_names
        assert "Markdown" in lang_names
        py_lang = next(l for l in result if l["name"] == "Python")
        assert py_lang["files"] == 3
        assert py_lang["percentage"] > 50


def test_detect_languages_mixed():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "app.py").write_text("")
        (root / "app.js").write_text("")
        (root / "app.ts").write_text("")
        (root / "lib.rs").write_text("")
        (root / "main.go").write_text("")

        result = detect_languages(str(root))

        lang_names = {l["name"] for l in result}
        assert "Python" in lang_names
        assert "JavaScript" in lang_names
        assert "TypeScript" in lang_names
        assert "Rust" in lang_names
        assert "Go" in lang_names
        # All equal weight
        for l in result:
            assert l["percentage"] == 20.0


def test_detect_languages_ignores_dirs():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "src.py").write_text("")
        (root / "node_modules").mkdir()
        (root / "node_modules" / "lib.js").write_text("")
        (root / "__pycache__").mkdir()
        (root / "__pycache__" / "cache.py").write_text("")

        result = detect_languages(str(root))
        lang_names = {l["name"] for l in result}
        assert lang_names == {"Python"}
        assert result[0]["files"] == 1


def test_detect_framework_python():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "pyproject.toml").write_text("[project]\nname = 'test'\ndependencies = ['fastapi']")
        (root / "requirements.txt").write_text("flask==2.0")

        result = detect_framework(str(root))
        fw_names = [f["name"] for f in result]

        assert "Python" in fw_names


def test_detect_framework_nodejs():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        pkg = {"name": "test-app", "dependencies": {"react": "^18", "next": "^14"}}
        (root / "package.json").write_text(json.dumps(pkg))

        result = detect_framework(str(root))
        fw_names = [f["name"] for f in result]

        assert "Node.js" in fw_names


def test_detect_build_system_npm():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "package.json").write_text("{}")
        (root / "package-lock.json").write_text("")

        result = detect_build_system(str(root))
        assert len(result) == 1
        assert result[0]["name"] == "npm"


def test_detect_build_system_cargo():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "Cargo.toml").write_text("[package]\nname = 'test'")

        result = detect_build_system(str(root))
        assert len(result) == 1
        assert result[0]["name"] == "Cargo"


def test_detect_test_framework_pytest():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "pyproject.toml").write_text("[tool.pytest.ini_options]\nminversion = '6.0'")
        (root / "tests").mkdir()

        result = detect_test_framework(str(root))
        assert len(result) == 1
        assert result[0]["framework"] == "Pytest"


def test_detect_test_framework_jest():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "jest.config.js").write_text("module.exports = {};")

        result = detect_test_framework(str(root))
        assert len(result) == 1
        assert result[0]["framework"] == "Jest"


def test_detect_lint_tools():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / ".eslintrc.json").write_text("{}")
        (root / "ruff.toml").write_text("")

        result = detect_lint_tools(str(root))
        tool_names = {t["name"] for t in result}
        assert "ESLint" in tool_names
        assert "Ruff" in tool_names


def test_get_project_name_pyproject():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "pyproject.toml").write_text('[project]\nname = "my-cool-app"')

        assert get_project_name(str(root)) == "my-cool-app"


def test_get_project_name_package_json():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "package.json").write_text('{"name": "@scope/pkg-name"}')

        assert get_project_name(str(root)) == "@scope/pkg-name"


def test_get_project_name_fallback():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Should use the directory name
        name = get_project_name(str(root))
        assert name == Path(tmpdir).name


def test_detect_git_info_not_git():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = detect_git_info(tmpdir)
        assert result["is_git_repo"] is False
        assert result["commit_count"] == 0


def test_generated_packages_are_pruned(tmp_path: Path) -> None:
    (tmp_path / "src.py").touch()
    for ignored in ("node_modules", "package.egg-info"):
        folder = tmp_path / ignored
        folder.mkdir()
        (folder / "bundle.js").touch()
    assert detect_languages(str(tmp_path)) == [{"name": "Python", "percentage": 100.0, "files": 1}]


def test_node_project_without_lockfile(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text("{}", encoding="utf-8")
    assert detect_build_system(str(tmp_path))[0]["name"] == "npm"


def test_declared_package_manager_and_real_scripts(tmp_path: Path) -> None:
    package = {"packageManager": "pnpm@10.4.0", "scripts": {"build": "vite build", "test": "vitest run"}}
    (tmp_path / "package.json").write_text(json.dumps(package), encoding="utf-8")
    (tmp_path / "package-lock.json").touch()
    (tmp_path / "vitest.config.ts").touch()
    assert detect_build_system(str(tmp_path)) == [{"name": "pnpm", "command": "pnpm run build", "lock": None}]
    assert detect_test_framework(str(tmp_path))[0]["command"] == "pnpm run test"


def test_lockfile_without_build_script_yields_install(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text('{"devDependencies": null}', encoding="utf-8")
    (tmp_path / "bun.lock").touch()
    assert detect_framework(str(tmp_path))[0]["name"] == "Node.js"
    assert detect_build_system(str(tmp_path))[0]["command"] == "bun install"


def test_uv_environment_detection(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").touch()
    (tmp_path / "uv.lock").touch()
    assert detect_build_system(str(tmp_path)) == [{"name": "uv", "command": "uv sync", "lock": "uv.lock"}]


def test_invalid_package_shape_falls_back_to_directory(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text('["name"]', encoding="utf-8")
    assert get_project_name(str(tmp_path)) == tmp_path.name
