"""CLI interface for Make.py using Typer

Provides the main entry point for the make.py command line tool.
"""

import sys
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

from .core import (
    discover_commands,
    execute_command,
    get_default_command,
    parse_parameters,
    CommandRegistry,
    DependencyError
)

console = Console()
app = typer.Typer(
    name="make.py",
    help="Python-based command orchestration using Makefile.py",
    no_args_is_help=False  # Allow running without args to use default command
)


@app.command()
def main(
    args: List[str] = typer.Argument(
        default=None,
        help="Command name and parameters (PARAM=value)"
    )
) -> None:
    """Main entry point for make.py CLI.

    Examples:
        make.py                    # Run first command
        make.py build_images       # Run specific command
        make.py build IMAGE=myapp  # Run with parameter override
    """
    try:
        # Discover commands from Makefile.py
        registry = discover_commands()

        if not registry.list_commands():
            console.print("[red]Error:[/red] No commands found in Makefile.py")
            raise typer.Exit(1)

        # Parse command and parameters
        command_name, params = parse_parameters(args or [])

        # Use default command if none specified
        if command_name is None:
            command_name = get_default_command(registry)
            if command_name is None:
                console.print("[red]Error:[/red] No default command available")
                raise typer.Exit(1)
            console.print(f"[dim]Running default command: {command_name}[/dim]")

        # Validate command exists
        if command_name not in registry.commands:
            console.print(f"[red]Error:[/red] Command '{command_name}' not found")
            console.print("\nAvailable commands:")
            _show_commands(registry)
            raise typer.Exit(1)

        # Execute the command
        execute_command(registry, command_name, params)

    except FileNotFoundError:
        console.print("[red]Error:[/red] Makefile.py not found in current directory")
        console.print("\n[dim]Create a Makefile.py file with your commands.[/dim]")
        console.print("[dim]Example:[/dim]")
        console.print("```python")
        console.print("from make import bash, _")
        console.print("")
        console.print("def hello():")
        console.print("    bash('echo Hello World')")
        console.print("```")
        raise typer.Exit(1)

    except ImportError as e:
        console.print(f"[red]Error:[/red] Could not import Makefile.py: {e}")
        raise typer.Exit(1)

    except DependencyError as e:
        console.print(f"[red]Dependency Error:[/red] {e}")
        raise typer.Exit(1)

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Execution Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def init() -> None:
    """Initialize a new Makefile.py in the current directory."""
    makefile_content = '''from make import sh, bash, _, dep

# Read from env
DOCKER_REPO = _('DOCKER_REPO')
IMAGE = _('IMAGE')
VERSION = _('VERSION', "0.0.1")  # Default value


def build_images():
    bash("docker build -f ./docker/Dockerfile ."
        f" -t {DOCKER_REPO}/{IMAGE}:{VERSION}")


def push_images():
    sh.docker(f"push {DOCKER_REPO}/{IMAGE}:{VERSION}")


@dep(build_images, push_images)
def build_and_push():
    pass
'''

    try:
        with open("Makefile.py", "x") as f:
            f.write(makefile_content)
        console.print("[green]✓[/green] Created Makefile.py")
        console.print("\n[dim]You can now run:[/dim]")
        console.print("  make.py                  # Run first command")
        console.print("  make.py build_images     # Run specific command")
        console.print("  make.py --help           # Show help")

    except FileExistsError:
        console.print("[yellow]Warning:[/yellow] Makefile.py already exists")
        raise typer.Exit(1)


@app.command()
def list() -> None:
    """List available commands from Makefile.py."""
    try:
        registry = discover_commands()
        console.print("\n[bold]Available commands:[/bold]")
        _show_commands(registry)

    except FileNotFoundError:
        console.print("[red]Error:[/red] Makefile.py not found")
        console.print("Run '[bold]make.py init[/bold]' to create one.")
        raise typer.Exit(1)

    except ImportError as e:
        console.print(f"[red]Error:[/red] Could not import Makefile.py: {e}")
        raise typer.Exit(1)


def _show_commands(registry: CommandRegistry) -> None:
    """Display commands in a formatted table."""
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Command")
    table.add_column("Dependencies")

    for command in sorted(registry.list_commands()):
        deps = registry.dependencies.get(command, [])
        deps_str = ", ".join(deps) if deps else "[dim]none[/dim]"
        table.add_row(command, deps_str)

    console.print(table)


def cli_entry_point() -> None:
    """Entry point for the CLI when installed via pip."""
    # Handle the case where no arguments are provided
    if len(sys.argv) == 1:
        # Run with default behavior (no args)
        main([])
    else:
        # Let typer handle the arguments
        app()


if __name__ == "__main__":
    cli_entry_point()