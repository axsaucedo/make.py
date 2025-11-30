"""End-to-end tests for Make.py CLI interface

Tests the typer-based CLI functionality:
- Direct command execution (no admin commands)
- Parameter passing with PARAM=value syntax
- Error handling and help output
- Rich formatting and output
- Dynamic command registration
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
import pytest
from typer.testing import CliRunner

# Add make to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent))

from pmake.cli import register_makefile_commands, create_dynamic_command, show_init_guidance
from pmake.core import discover_commands
import typer


class TestCLIDirectCommands:
    """Test direct CLI command functionality"""

    def setup_method(self):
        """Setup test environment"""
        self.runner = CliRunner()
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)

        # Copy simple makefile fixture
        fixture_path = Path(__file__).parent / "fixtures" / "simple_makefile.py"
        shutil.copy(fixture_path, Path(self.test_dir) / "Makefile.py")

        # Set up environment variables
        self.original_env = os.environ.copy()
        os.environ.update({
            'APP_NAME': 'cli_test',
            'VERSION': '1.0.0',
            'ENVIRONMENT': 'test'
        })

        # Create a fresh Typer app with dynamic commands
        self.app = typer.Typer(
            name="pmake",
            help="Python-based command orchestration using Makefile.py",
            no_args_is_help=False
        )

        # Register commands dynamically
        self.registry = discover_commands()
        for cmd_name, func in self.registry.commands.items():
            self._create_dynamic_command(cmd_name, func, self.registry)

    def _create_dynamic_command(self, name: str, func, registry):
        """Create a Typer command for a Makefile.py function."""
        from pmake.core import execute_command, parse_parameters, DependencyError
        from rich.console import Console

        console = Console()
        deps = registry.dependencies.get(name, [])
        help_text = func.__doc__ or f"Run {name} command"

        if deps:
            help_text += f" (depends on: {', '.join(deps)})"

        @self.app.command(name=name, help=help_text)
        def dynamic_command(params: list[str] = typer.Argument(default=None, help="Parameters (PARAM=value)")) -> None:
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

    def teardown_method(self):
        """Cleanup test environment"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_cli_specific_command(self):
        """Test running specific command directly"""
        result = self.runner.invoke(self.app, ["version"])

        assert result.exit_code == 0
        assert "Running: version" in result.stdout
        # Note: Actual command output may not be captured in test environment

    def test_cli_command_with_dependencies(self):
        """Test running command that has dependencies"""
        result = self.runner.invoke(self.app, ["greet"])

        assert result.exit_code == 0
        # Should execute hello first, then greet
        assert "Running: hello" in result.stdout
        assert "Running: greet" in result.stdout

    def test_cli_parameter_override(self):
        """Test parameter override with PARAM=value syntax"""
        result = self.runner.invoke(self.app, ["hello", "APP_NAME=overridden"])

        assert result.exit_code == 0
        assert "Running: hello" in result.stdout

    def test_cli_multiple_parameter_overrides(self):
        """Test multiple parameter overrides"""
        result = self.runner.invoke(self.app, ["version", "VERSION=2.0.0", "ENVIRONMENT=staging"])

        assert result.exit_code == 0
        assert "Running: version" in result.stdout

    def test_cli_complex_dependencies(self):
        """Test command with multiple dependencies"""
        result = self.runner.invoke(self.app, ["welcome"])

        assert result.exit_code == 0
        assert "Running: hello" in result.stdout
        assert "Running: version" in result.stdout
        assert "Running: welcome" in result.stdout

    def test_cli_help(self):
        """Test CLI help output shows all Makefile.py commands"""
        result = self.runner.invoke(self.app, ["--help"])

        assert result.exit_code == 0
        assert "Python-based command orchestration" in result.stdout
        # Should show commands from the simple_makefile.py fixture
        assert "hello" in result.stdout
        assert "version" in result.stdout
        assert "greet" in result.stdout
        assert "Simple greeting task" in result.stdout  # docstring

    def test_cli_help_shows_dependencies(self):
        """Test that help output shows command dependencies"""
        result = self.runner.invoke(self.app, ["--help"])

        assert result.exit_code == 0
        # Should show dependency information
        assert "depends on:" in result.stdout


class TestCLIMissingMakefile:
    """Test CLI behavior when no Makefile.py exists"""

    def setup_method(self):
        """Setup test environment"""
        self.runner = CliRunner()
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)

    def teardown_method(self):
        """Cleanup test environment"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)

    def test_cli_no_makefile_shows_guidance(self):
        """Test that missing Makefile.py shows initialization guidance"""
        # Use the actual CLI entry point to test missing Makefile behavior
        from pmake.cli import cli_entry_point
        from unittest.mock import patch
        import sys
        from io import StringIO

        # Capture output
        captured_output = StringIO()

        with patch('sys.argv', ['pmake']):  # Simulate running just 'pmake'
            with patch('sys.stdout', captured_output):
                try:
                    cli_entry_point()
                except SystemExit:
                    pass  # Expected when no Makefile.py exists

        output = captured_output.getvalue()

        assert "No Makefile.py found" in output
        assert "Create a Makefile.py file" in output
        assert "Example Makefile.py:" in output
        assert "from pmake import" in output
        assert "def hello():" in output

    def test_cli_guidance_content(self):
        """Test the content of initialization guidance"""
        from pmake.cli import show_init_guidance
        from rich.console import Console
        from io import StringIO
        from unittest.mock import patch

        # Capture Rich console output
        console_output = StringIO()
        console = Console(file=console_output, force_terminal=False)

        # Patch the console in the CLI module
        with patch('pmake.cli.console', console):
            show_init_guidance()

        output = console_output.getvalue()

        # Check for key guidance elements
        assert "No Makefile.py found" in output
        assert "Example Makefile.py:" in output
        assert "pmake            # Runs default command" in output
        assert "pmake test       # Runs test command" in output
        assert "pmake --help     # Shows all available commands" in output


class TestCLIErrorHandling:
    """Test CLI error handling scenarios with new dynamic command structure"""

    def setup_method(self):
        """Setup test environment"""
        self.runner = CliRunner()
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)

    def teardown_method(self):
        """Cleanup test environment"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)

    def test_cli_invalid_makefile_syntax(self):
        """Test CLI with syntactically invalid Makefile.py"""
        # Create invalid Makefile.py
        Path("Makefile.py").write_text("invalid python syntax !!!")

        # Try to create an app with this invalid Makefile
        from pmake.cli import register_makefile_commands

        # Should raise or return None when syntax error occurs
        try:
            registry = register_makefile_commands()
            # If no exception, it should return None
            assert registry is None
        except (SyntaxError, ImportError):
            # This is also acceptable - the error is properly propagated
            pass

    def test_cli_makefile_import_error(self):
        """Test CLI with Makefile.py that has import errors"""
        # Create Makefile.py with import error
        makefile_content = """
from nonexistent_module import something
from pmake import echo

def test_task():
    echo('test')
"""
        Path("Makefile.py").write_text(makefile_content)

        # Try to register commands with import error
        from pmake.cli import register_makefile_commands

        registry = register_makefile_commands()
        # Should return None when there are import errors
        assert registry is None

    def test_cli_no_commands_found(self):
        """Test CLI when Makefile.py has no callable functions"""
        # Create Makefile.py with no functions
        makefile_content = """
from pmake import echo

# No functions defined
VARIABLE = "test"
"""
        Path("Makefile.py").write_text(makefile_content)

        # Should still be able to discover (empty) commands
        from pmake.cli import register_makefile_commands

        registry = register_makefile_commands()
        assert registry is not None
        commands = registry.list_commands()
        assert len(commands) == 0

    def test_cli_command_discovery_works(self):
        """Test that command discovery works with valid Makefile.py"""
        # Create a simple Makefile.py
        fixture_path = Path(__file__).parent / "fixtures" / "simple_makefile.py"
        shutil.copy(fixture_path, Path(self.test_dir) / "Makefile.py")

        from pmake.cli import register_makefile_commands

        registry = register_makefile_commands()
        assert registry is not None
        commands = registry.list_commands()
        assert len(commands) > 0
        assert "hello" in commands


class TestCLIRichFormatting:
    """Test CLI Rich formatting and output"""

    def setup_method(self):
        """Setup test environment"""
        self.runner = CliRunner()
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)

        # Copy simple makefile fixture
        fixture_path = Path(__file__).parent / "fixtures" / "simple_makefile.py"
        shutil.copy(fixture_path, Path(self.test_dir) / "Makefile.py")

        # Create dynamic CLI app
        self.app = typer.Typer(name="pmake", help="Test CLI", no_args_is_help=False)
        from pmake.core import discover_commands
        registry = discover_commands()
        for cmd_name, func in registry.commands.items():
            self._create_dynamic_command(cmd_name, func, registry)

    def _create_dynamic_command(self, name: str, func, registry):
        """Create a Typer command for a Makefile.py function."""
        from pmake.core import execute_command, parse_parameters, DependencyError
        from rich.console import Console

        console = Console()
        deps = registry.dependencies.get(name, [])
        help_text = func.__doc__ or f"Run {name} command"

        if deps:
            help_text += f" (depends on: {', '.join(deps)})"

        @self.app.command(name=name, help=help_text)
        def dynamic_command(params: list[str] = typer.Argument(default=None)) -> None:
            try:
                _, param_dict = parse_parameters(params or [])
                execute_command(registry, name, param_dict)
            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")
                raise typer.Exit(1)

    def teardown_method(self):
        """Cleanup test environment"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)

    def test_cli_rich_output_contains_commands(self):
        """Test Rich formatting shows commands properly"""
        result = self.runner.invoke(self.app, ["--help"])

        assert result.exit_code == 0
        # Should show commands with Rich formatting
        assert "hello" in result.stdout
        assert "version" in result.stdout
        assert "Commands" in result.stdout or "commands" in result.stdout

    def test_cli_rich_dependency_display(self):
        """Test Rich formatting shows dependencies"""
        result = self.runner.invoke(self.app, ["--help"])

        assert result.exit_code == 0
        # Should show dependency information in help
        assert "depends on:" in result.stdout


class TestCLIEntryPoint:
    """Test CLI entry point functionality"""

    def test_cli_entry_point_import(self):
        """Test that CLI entry point can be imported"""
        # Should not raise exception
        from pmake.cli import cli_entry_point
        assert callable(cli_entry_point)

    def test_cli_functions_importable(self):
        """Test that key CLI functions are importable"""
        from pmake.cli import register_makefile_commands, show_init_guidance
        assert callable(register_makefile_commands)
        assert callable(show_init_guidance)


class TestCLIParameterValidation:
    """Test CLI parameter validation and edge cases"""

    def setup_method(self):
        """Setup test environment"""
        self.runner = CliRunner()
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)

        # Copy simple makefile fixture
        fixture_path = Path(__file__).parent / "fixtures" / "simple_makefile.py"
        shutil.copy(fixture_path, Path(self.test_dir) / "Makefile.py")

        # Create dynamic CLI app
        self.app = typer.Typer(name="pmake", help="Test CLI", no_args_is_help=False)
        from pmake.core import discover_commands
        registry = discover_commands()
        for cmd_name, func in registry.commands.items():
            self._create_dynamic_command(cmd_name, func, registry)

    def _create_dynamic_command(self, name: str, func, registry):
        """Create a Typer command for a Makefile.py function."""
        from pmake.core import execute_command, parse_parameters
        from rich.console import Console

        console = Console()

        @self.app.command(name=name)
        def dynamic_command(params: list[str] = typer.Argument(default=None)) -> None:
            try:
                _, param_dict = parse_parameters(params or [])
                execute_command(registry, name, param_dict)
            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")
                raise typer.Exit(1)

    def teardown_method(self):
        """Cleanup test environment"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)

    def test_cli_parameter_with_equals_in_value(self):
        """Test parameter with equals sign in value"""
        result = self.runner.invoke(self.app, ["hello", "APP_NAME=app=with=equals"])

        assert result.exit_code == 0
        assert "Running: hello" in result.stdout

    def test_cli_parameter_with_spaces(self):
        """Test parameter with spaces (should be quoted properly)"""
        result = self.runner.invoke(self.app, ["hello", "APP_NAME=app with spaces"])

        assert result.exit_code == 0
        assert "Running: hello" in result.stdout

    def test_cli_empty_parameter_value(self):
        """Test parameter with empty value"""
        result = self.runner.invoke(self.app, ["hello", "APP_NAME="])

        assert result.exit_code == 0
        assert "Running: hello" in result.stdout
        # Should handle empty value gracefully