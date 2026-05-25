"""Typer CLI entrypoint for Scribe."""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from .analyzer import RepoAnalyzer
from .generator import GenerationEvent, ReadmeGenerator
from .llm import DEFAULT_MODEL, ModelNotPulledError, OllamaClient, OllamaUnavailableError
from .prompts import SECTION_ORDER

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode="rich",
    help="📝 Local-LLM-powered README generator.",
)

console = Console()
err_console = Console(stderr=True, style="bold red")


# --------------------------- generate ----------------------------------- #


@app.command()
def generate(
    path: Path = typer.Argument(
        ..., exists=True, file_okay=False, dir_okay=True, resolve_path=True,
        help="Path to the repository to document.",
    ),
    output: Path = typer.Option(
        None, "--output", "-o", help="Write the README to this file (default: print to stdout)."
    ),
    model: str = typer.Option(DEFAULT_MODEL, "--model", "-m", help="Ollama model tag."),
    stream: bool = typer.Option(
        True, "--stream/--no-stream",
        help="Stream tokens as they arrive (only effective when --output is given alongside).",
    ),
    only: list[str] = typer.Option(
        None, "--only",
        help="Generate only these sections (comma- or repeat-separated).",
    ),
    temperature: float = typer.Option(0.2, "--temperature", "-t", min=0.0, max=2.0),
):
    """Analyze REPO and generate a README.md."""
    logging.basicConfig(level=logging.WARNING, format="%(message)s")

    sections = _resolve_sections(only)
    facts = _analyze_or_die(path)

    client = OllamaClient(model=model)
    ok, msg = client.ready()
    if not ok:
        err_console.print(msg)
        raise typer.Exit(code=2)

    generator = ReadmeGenerator(client)

    if stream and output is not None:
        # Stream-to-file with live preview on stderr.
        with output.open("w") as fp:
            _stream_to_file(generator, facts, sections, temperature, fp)
        console.print(f"\n[green]✓[/green] README written to [bold]{output}[/bold]")
    else:
        readme = generator.generate(facts, sections=sections, temperature=temperature)
        if output is None:
            console.print(readme)
        else:
            output.write_text(readme)
            console.print(f"[green]✓[/green] README written to [bold]{output}[/bold]")


def _stream_to_file(
    generator: ReadmeGenerator,
    facts,
    sections,
    temperature: float,
    fp,
) -> None:
    current_section = ""
    pieces: list[str] = []
    for event in generator.stream(facts, sections=sections, temperature=temperature):
        if event.status == "start" and event.section != current_section:
            current_section = event.section
            console.print(f"\n[bold cyan]▸ {event.section}[/bold cyan]")
        if event.status == "delta":
            console.print(event.payload, end="", soft_wrap=True)
            pieces.append(event.payload)
        if event.status == "done" and event.section in {"badges", "project_structure"}:
            # Deterministic chunks emitted as a single "done"
            console.print(f"\n[bold cyan]▸ {event.section}[/bold cyan]")
            console.print(event.payload)
            pieces.append("\n\n" + event.payload)
        if event.status == "done" and event.section not in {"badges", "project_structure"}:
            pieces.append("\n\n")
    fp.write("".join(pieces).strip() + "\n")


# --------------------------- analyze ------------------------------------ #


@app.command()
def analyze(
    path: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, resolve_path=True),
    json_out: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
):
    """Print the structured RepoFacts the analyzer would feed to the LLM."""
    facts = _analyze_or_die(path)
    if json_out:
        console.print_json(facts.to_json())
        return
    _print_facts(facts)


def _print_facts(facts) -> None:
    console.print(Panel.fit(
        Text.assemble(
            ("Name: ", "dim"), (facts.name, "bold"),
            ("\nPath: ", "dim"), (facts.path, "italic"),
        ),
        title="Repository",
    ))

    if facts.description:
        console.print(Panel(facts.description, title="Existing description"))

    if facts.languages:
        t = Table(title="Languages (by file count)", show_lines=False)
        t.add_column("Language", style="cyan")
        t.add_column("Files", justify="right")
        for lang, count in facts.languages.items():
            t.add_row(lang, str(count))
        console.print(t)

    if facts.frameworks:
        console.print(Panel(", ".join(facts.frameworks), title="Frameworks"))

    if facts.dependencies:
        console.print(Panel(", ".join(facts.dependencies), title="Dependencies"))

    if facts.entry_points or facts.npm_scripts:
        rows = list(facts.python_scripts.items()) + list(facts.npm_scripts.items())
        t = Table(title="Entry points / scripts")
        t.add_column("Name", style="cyan")
        t.add_column("Command", style="dim")
        for k, v in rows[:20]:
            t.add_row(k, str(v))
        console.print(t)

    if facts.file_tree:
        console.print(Panel(Syntax(facts.file_tree, "text", theme="monokai", line_numbers=False),
                           title="File tree"))


# --------------------------- status ------------------------------------- #


@app.command()
def status(model: str = typer.Option(DEFAULT_MODEL, "--model", "-m")):
    """Check that Ollama is running and the chosen model is pulled."""
    client = OllamaClient(model=model)
    ok, msg = client.ready()
    if ok:
        console.print(f"[green]✓[/green] {msg}")
        raise typer.Exit(code=0)
    err_console.print(msg)
    raise typer.Exit(code=2)


# --------------------------- ui ----------------------------------------- #


@app.command()
def ui(port: int = typer.Option(8501, "--port"), open_browser: bool = typer.Option(True, "--open/--no-open")):
    """Launch the Streamlit web UI."""
    ui_path = Path(__file__).with_name("ui.py")
    cmd = [
        sys.executable, "-m", "streamlit", "run", str(ui_path),
        "--server.port", str(port),
        "--browser.gatherUsageStats", "false",
    ]
    if not open_browser:
        cmd.extend(["--server.headless", "true"])
    console.print(f"[cyan]Starting Streamlit UI on http://localhost:{port}/ ...[/cyan]")
    raise typer.Exit(code=subprocess.call(cmd))


# --------------------------- helpers ----------------------------------- #


def _analyze_or_die(path: Path):
    try:
        return RepoAnalyzer(path).analyze()
    except FileNotFoundError as exc:
        err_console.print(str(exc))
        raise typer.Exit(code=2) from exc


def _resolve_sections(only: list[str] | None) -> list[str] | None:
    if not only:
        return None
    flat: list[str] = []
    for chunk in only:
        flat.extend(s.strip() for s in chunk.split(",") if s.strip())
    unknown = [s for s in flat if s not in SECTION_ORDER]
    if unknown:
        err_console.print(f"Unknown section(s): {unknown}. Known: {list(SECTION_ORDER)}")
        raise typer.Exit(code=2)
    return flat


# --------------------------- entry point ------------------------------- #


def main():  # pragma: no cover - thin shim
    try:
        app()
    except (OllamaUnavailableError, ModelNotPulledError) as exc:
        err_console.print(str(exc))
        sys.exit(2)


if __name__ == "__main__":  # pragma: no cover
    main()
