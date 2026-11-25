# 🔍 claudescan

**Scan any repo → generate perfect AI agent config files in seconds.**

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

`claudescan` analyzes your repository and automatically generates optimized config files for AI coding agents — CLAUDE.md, AGENTS.md, and .cursorrules. No more copy-pasting boilerplate or forgetting to document your build commands.

## ✨ Why claudescan?

AI coding agents (Claude Code, Cursor, Codex, OpenCode) are only as good as their project context. The difference between a confused agent and a superhuman assistant is a well-crafted project config file.

**The problem:** Writing these files by hand is tedious and error-prone. You have to remember every build command, every framework, every convention.

**The solution:** Point `claudescan` at any repo and it figures everything out automatically.

```bash
$ claudescan .
# Preview the three generated configurations in the terminal
```

## 🚀 Quick Start

```bash
# Install
python -m pip install git+https://github.com/xvcenh/claudescan.git

# Scan any project
claudescan /path/to/your-project

# Inspect the detected languages, build commands and test frameworks from a script
claudescan /path/to/your-project --json

# Write config files directly
claudescan /path/to/your-project -w
```

With `-w`, three files appear in your project root, ready for any AI agent.

## 🎯 What It Detects

JavaScript commands follow the declared package manager or its lockfile. The scanner uses build and test scripts only when they exist in the project manifest.

claudescan analyzes your repo and auto-detects:

| Category | Examples |
|----------|----------|
| **Languages** | Python, TypeScript, Rust, Go, JavaScript, +20 more |
| **Frameworks** | Next.js, React, Django, FastAPI, Vue, Svelte, Express... |
| **Build Systems** | npm, Yarn, pnpm, Bun, uv, pip, Poetry, Cargo, Go Modules, Make, CMake |
| **Test Frameworks** | Jest, Vitest, Pytest, Cargo Test, Go Test, PHPUnit, RSpec |
| **Linters** | ESLint, Prettier, Ruff, Mypy, Biome, golangci-lint, Clippy |
| **Git Info** | Default branch, commit count, recent contributors, remotes |

It then generates **language-specific conventions** — PEP 8 for Python, strict TypeScript rules, Rust idioms, and more.

## 📦 Output Formats

### CLAUDE.md
Full project context for Anthropic's Claude Code. Includes build/test commands, code conventions, project structure, and git workflow.

### AGENTS.md
Compact reference for Cursor, Codex, OpenCode, and other agents. Quick-command table + project rules.

### .cursorrules
System prompt for Cursor's AI. Focused tech stack + command reference.

## 🎨 Terminal Output

```
╭────────────────────────────────────────╮
│ claudescan — AI Agent Config Generator │
╰────────────────────────────────────────╯
Scanning: /home/user/my-project

Project: my-awesome-api

  Languages:  Python (72.3%)  TypeScript (18.5%)  CSS (9.2%)
  Frameworks:  Python (FastAPI), Node.js (React)
  Build:  Poetry → `poetry build`
  Test:  Pytest → `pytest`
  Lint:  ESLint, Prettier, Ruff
  Git:  342 commits on main
```

## 🔧 Usage

```
claudescan [PATH] [OPTIONS]

Arguments:
  PATH              Path to project (default: current directory)

Options:
  -o, --output      Output format: claude, agents, cursorrules, or all (default: all)
  -w, --write       Write files to project directory
  --quiet           Raw output only, no formatting
```

## 📂 Supported Projects

claudescan works with **any** codebase, but provides the best results for:

- 🐍 **Python** — Django, Flask, FastAPI, Litestar, pip, Poetry, Pipenv
- 🟦 **TypeScript/JavaScript** — React, Next.js, Vue, Svelte, Express, NestJS
- 🦀 **Rust** — Cargo projects with Clippy
- 🐹 **Go** — Go Modules
- 💎 **Ruby** — Bundler + RSpec
- 🐘 **PHP** — Composer + PHPUnit
- 🐳 **Docker** — Dockerfile + Compose detection
- And any language with recognizable config files

## 🤝 Contributing

```bash
git clone https://github.com/xvcenh/claudescan.git
cd claudescan
pip install -e ".[dev]"
pytest
```

## 📝 License

MIT © [xvcenh](https://github.com/xvcenh)

---

<p align="center">
  <b>⭐ Star this repo</b> if you find it useful!<br>
  <sub>Built in one night with ❤️ + AI</sub>
</p>
