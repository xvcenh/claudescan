"""Command-line interface for claudescan."""

import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from .scanner import generate_output, scan_project

console = Console()


def main():
    parser = argparse.ArgumentParser(
        prog="claudescan",
        description="Scan any repo and auto-generate optimized AI agent config files",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the project to scan (default: current directory)",
    )
    parser.add_argument(
        "-o", "--output",
        choices=["claude", "agents", "cursorrules", "all"],
        default="all",
        help="Output format (default: all)",
    )
    parser.add_argument(
        "-w", "--write",
        action="store_true",
        help="Write files to the project directory (CLAUDE.md, AGENTS.md, .cursorrules)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Output raw content only (no formatting)",
    )

    args = parser.parse_args()

    # Resolve path
    root = Path(args.path).resolve()

    # Show scanning header
    if not args.quiet:
        console.print()
        console.print(
            Panel.fit(
                Text("claudescan — AI Agent Config Generator", style="bold cyan"),
                border_style="cyan",
            )
        )
        console.print(f"[dim]Scanning: {root}[/dim]")
        console.print()

    try:
        data = scan_project(str(root))
    except (FileNotFoundError, NotADirectoryError) as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

    # Show summary
    if not args.quiet:
        _print_summary(data)

    # Generate outputs
    formats = ["claude", "agents", "cursorrules"] if args.output == "all" else [args.output]
    file_map = {
        "claude": "CLAUDE.md",
        "agents": "AGENTS.md",
        "cursorrules": ".cursorrules",
    }

    for fmt in formats:
        content = generate_output(data, fmt)

        if args.write:
            filepath = root / file_map[fmt]
            filepath.write_text(content)
            if not args.quiet:
                console.print(f"[green]✓[/green] Wrote [bold]{file_map[fmt]}[/bold]")
        else:
            if not args.quiet:
                console.print(
                    Panel(
                        content,
                        title=f"[bold]{file_map[fmt]}[/bold]",
                        border_style="green",
                        title_align="left",
                    )
                )
                console.print()
            else:
                console.print(content)
                if fmt != formats[-1]:
                    print("\n---\n")

    # Final message
    if args.write and not args.quiet:
        console.print()
        console.print("[green bold]Done![/green bold] Files written to project directory.")
        console.print()
        for fmt in formats:
            console.print(f"  [cyan]{file_map[fmt]}[/cyan]")
        console.print()
    elif not args.quiet:
        console.print(
            "[dim]Tip: Use [bold]claudescan -w[/bold] to write files to the project directory.[/dim]"
        )
        console.print()


def _print_summary(data: dict):
    """Print a formatted summary of the scan results."""
    name = data["project_name"]
    console.print(f"[bold]Project:[/bold] {name}")
    console.print()

    # Languages
    languages = data.get("languages", [])
    if languages:
        lang_text = "  ".join(
            f"[cyan]{l['name']}[/cyan] [dim]({l['percentage']}%)[/dim]"
            for l in languages[:5]
        )
        console.print(f"  [bold]Languages:[/bold] {lang_text}")

    # Frameworks
    frameworks = data.get("frameworks", [])
    if frameworks:
        fw_parts = []
        for f in frameworks:
            label = f["name"]
            if f.get("specific"):
                label += f" [dim]({f['specific']})[/dim]"
            fw_parts.append(label)
        console.print(f"  [bold]Frameworks:[/bold] {', '.join(fw_parts)}")

    # Build
    build = data.get("build_systems", [])
    if build:
        console.print(f"  [bold]Build:[/bold] {build[0]['name']} → [dim]`{build[0]['command']}`[/dim]")

    # Tests
    tests = data.get("test_frameworks", [])
    if tests:
        console.print(f"  [bold]Test:[/bold] {tests[0]['framework']} → [dim]`{tests[0]['command']}`[/dim]")

    # Lint
    linters = data.get("lint_tools", [])
    if linters:
        lint_names = [l["name"] for l in linters]
        console.print(f"  [bold]Lint:[/bold] {', '.join(lint_names)}")

    # Git
    git = data.get("git_info", {})
    if git.get("is_git_repo"):
        commits = git.get("commit_count", 0)
        branch = git.get("default_branch", "main")
        console.print(f"  [bold]Git:[/bold] {commits} commits on [dim]{branch}[/dim]")

    console.print()


if __name__ == "__main__":
    main()
