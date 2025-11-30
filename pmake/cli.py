"""CLI interface for Python Makefile (pmake) using Typer

Provides direct access to Makefile.py commands without admin subcommands.
All commands from Makefile.py are registered dynamically at startup.
"""

import sys
from typing import List, Optional, Callable

import typer
from rich.console import Console

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
    name="pmake",
    help="Python-based command orchestration using Makefile.py",
    no_args_is_help=False,  # Allow running without args to use default command
    rich_markup_mode="rich",
    add_completion=False
)


def show_init_guidance() -> None:
    """Show helpful guidance when no Makefile.py exists."""
    console.print("[yellow]No Makefile.py found in current directory[/yellow]")
    console.print("\n[dim]Create a Makefile.py file to get started:[/dim]")

    console.print("""
[bold]Example Makefile.py:[/bold]
```python
from pmake import sh, _, dep
from pmake import echo, python, pip

def hello():
    '''Say hello - this will be your default command'''
    echo('Hello from pmake!')

def test():
    '''Run tests'''
    python('-m', 'pytest')

@dep(test)
def deploy():
    '''Deploy after running tests'''
    echo('Deploying application...')
```

[dim]Then run:[/dim]
  pmake            # Runs default command (hello)
  pmake test       # Runs test command
  pmake deploy     # Runs test, then deploy
  pmake --help     # Shows all available commands
""")


def create_dynamic_command(name: str, func: Callable, registry: CommandRegistry) -> None:
    """Create a Typer command for a Makefile.py function."""
    deps = registry.dependencies.get(name, [])
    help_text = func.__doc__ or f"Run {name} command"

    if deps:
        help_text += f" [red](depends on: {', '.join(deps)})[/red]"

    @app.command(name=name, help=help_text)
    def dynamic_command(
        params: List[str] = typer.Argument(
            default=None,
            help="Parameters (PARAM=value)"
        )
    ) -> None:
        try:
            _, param_dict = parse_parameters(params or [])
            execute_command(registry, name, param_dict)
        except DependencyError as e:
            console.print(f"[red]Dependency Error:[/red] {e}")
            raise typer.Exit(1)
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"[red]Execution Error:[/red] {e}")
            raise typer.Exit(1)


def register_makefile_commands() -> Optional[CommandRegistry]:
    """Discover and register all Makefile.py commands as Typer commands."""
    try:
        registry = discover_commands()

        # Register each command dynamically
        for cmd_name, func in registry.commands.items():
            create_dynamic_command(cmd_name, func, registry)

        return registry
    except FileNotFoundError:
        return None
    except ImportError as e:
        console.print(f"[red]Error importing Makefile.py:[/red] {e}")
        return None


def cli_entry_point() -> None:
    """Entry point for the CLI when installed via pip."""
    # Try to register Makefile.py commands
    registry = register_makefile_commands()

    if registry is None:
        # No Makefile.py found or import error - show initialization guidance
        show_init_guidance()
        return

    # Handle the case where no arguments are provided
    if len(sys.argv) == 1:
        # Try to run default command
        default_cmd = get_default_command(registry)
        if default_cmd:
            try:
                console.print(f"[dim]Running default command: {default_cmd}[/dim]")
                execute_command(registry, default_cmd)
            except Exception as e:
                console.print(f"[red]Error executing default command:[/red] {e}")
                raise typer.Exit(1)
        else:
            # No default command - show help
            app()
    else:
        # Let typer handle the arguments
        app()


if __name__ == "__main__":
    cli_entry_point()
