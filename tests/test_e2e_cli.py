"""End-to-end tests for Make.py CLI interface

Tests the typer-based CLI functionality:
- Main command execution (default and specific commands)
- Subcommands (init, list)
- Parameter passing with PARAM=value syntax
- Error handling and help output
- Rich formatting and output
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

from make.cli import app, cli_entry_point
from make.core import discover_commands


class TestCLIMainCommand:
    """Test main CLI command functionality"""

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

    def teardown_method(self):
        """Cleanup test environment"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_cli_default_command(self):
        """Test running CLI with no arguments (default command)"""
        result = self.runner.invoke(app, ["main"])

        assert result.exit_code == 0
        # Should execute first command and show default command message
        assert "Running default command:" in result.stdout
        assert "capture_test" in result.stdout

    def test_cli_specific_command(self):
        """Test running specific command"""
        result = self.runner.invoke(app, ["main", "version"])

        assert result.exit_code == 0
        assert "Running: version" in result.stdout

    def test_cli_command_with_dependencies(self):
        """Test running command that has dependencies"""
        result = self.runner.invoke(app, ["main", "greet"])

        assert result.exit_code == 0
        # Should execute hello first, then greet
        assert "Running: hello" in result.stdout
        assert "Running: greet" in result.stdout

    def test_cli_parameter_override(self):
        """Test parameter override with PARAM=value syntax"""
        result = self.runner.invoke(app, ["main", "hello", "APP_NAME=overridden"])

        assert result.exit_code == 0
        assert "Running: hello" in result.stdout

    def test_cli_multiple_parameter_overrides(self):
        """Test multiple parameter overrides"""
        result = self.runner.invoke(app, ["main", "version", "VERSION=2.0.0", "ENVIRONMENT=staging"])

        assert result.exit_code == 0
        assert "Running: version" in result.stdout

    def test_cli_nonexistent_command(self):
        """Test running non-existent command"""
        result = self.runner.invoke(app, ["main", "nonexistent"])

        assert result.exit_code == 1
        assert "Command 'nonexistent' not found" in result.stdout
        assert "Available commands:" in result.stdout

    def test_cli_help(self):
        """Test CLI help output"""
        result = self.runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "Python-based command orchestration" in result.stdout


class TestCLISubcommands:
    """Test CLI subcommands (init, list)"""

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

    def test_cli_init_command(self):
        """Test make.py init command"""
        result = self.runner.invoke(app, ["init"])

        assert result.exit_code == 0
        assert "Created Makefile.py" in result.stdout

        # Verify Makefile.py was created
        assert Path("Makefile.py").exists()

        # Verify content is correct
        content = Path("Makefile.py").read_text()
        assert "from make import sh, bash, _, dep" in content
        assert "def build_images():" in content

    def test_cli_init_command_existing_file(self):
        """Test make.py init when Makefile.py already exists"""
        # Create existing Makefile.py
        Path("Makefile.py").write_text("# existing file")

        result = self.runner.invoke(app, ["init"])

        assert result.exit_code == 1
        assert "Makefile.py already exists" in result.stdout

    def test_cli_list_command(self):
        """Test make.py list command"""
        # Copy simple makefile fixture
        fixture_path = Path(__file__).parent / "fixtures" / "simple_makefile.py"
        shutil.copy(fixture_path, "Makefile.py")

        result = self.runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "Available commands:" in result.stdout

        # Should show commands from simple_makefile
        expected_commands = [
            "hello", "version", "greet", "welcome", "step1", "step2", "step3",
            "capture_test", "comprehensive", "default_task"
        ]

        for cmd in expected_commands:
            assert cmd in result.stdout

        # Should show dependency information
        assert "Dependencies" in result.stdout

    def test_cli_list_command_no_makefile(self):
        """Test make.py list when no Makefile.py exists"""
        result = self.runner.invoke(app, ["list"])

        assert result.exit_code == 1
        assert "Makefile.py not found" in result.stdout
        assert "make.py init" in result.stdout

    def test_cli_list_command_with_dependencies(self):
        """Test make.py list showing dependency relationships"""
        # Copy complex makefile fixture
        fixture_path = Path(__file__).parent / "fixtures" / "complex_makefile.py"
        shutil.copy(fixture_path, "Makefile.py")

        # Set required environment variables
        os.environ.update({
            'PROJECT': 'test',
            'VERSION': '1.0.0',
            'ENVIRONMENT': 'test'
        })

        result = self.runner.invoke(app, ["list"])

        assert result.exit_code == 0

        # Should show dependency relationships
        # Look for specific dependency patterns (may vary based on table format)
        assert "deploy" in result.stdout
        assert "quality_check" in result.stdout or "build" in result.stdout


class TestCLIErrorHandling:
    """Test CLI error handling scenarios"""

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

    def test_cli_no_makefile(self):
        """Test CLI when no Makefile.py exists"""
        result = self.runner.invoke(app, ["main"])

        assert result.exit_code == 1
        assert "Makefile.py not found" in result.stdout
        assert "Create a Makefile.py file" in result.stdout

    def test_cli_invalid_makefile_syntax(self):
        """Test CLI with syntactically invalid Makefile.py"""
        # Create invalid Makefile.py
        Path("Makefile.py").write_text("invalid python syntax !!!")

        result = self.runner.invoke(app, ["main"])

        assert result.exit_code == 1
        assert "Execution Error" in result.stdout

    def test_cli_makefile_import_error(self):
        """Test CLI with Makefile.py that has import errors"""
        # Create Makefile.py with import error
        makefile_content = """
from nonexistent_module import something
from make import bash

def test_task():
    bash("echo 'test'")
"""
        Path("Makefile.py").write_text(makefile_content)

        result = self.runner.invoke(app, ["main"])

        assert result.exit_code == 1
        assert "Could not import Makefile.py" in result.stdout

    def test_cli_no_commands_found(self):
        """Test CLI when Makefile.py has no callable functions"""
        # Create Makefile.py with no functions
        makefile_content = """
from make import bash

# No functions defined
VARIABLE = "test"
"""
        Path("Makefile.py").write_text(makefile_content)

        result = self.runner.invoke(app, ["main"])

        assert result.exit_code == 1
        assert "No commands found" in result.stdout


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

    def teardown_method(self):
        """Cleanup test environment"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)

    def test_cli_rich_error_formatting(self):
        """Test Rich error formatting"""
        result = self.runner.invoke(app, ["main", "nonexistent"])

        assert result.exit_code == 1
        # Rich formatting may include ANSI codes or be stripped in test
        # Just check that error message is present
        assert "Command 'nonexistent' not found" in result.stdout

    def test_cli_rich_success_formatting(self):
        """Test Rich success formatting (init command when file exists)"""
        result = self.runner.invoke(app, ["init"])

        assert result.exit_code == 1
        # Should show warning that file exists
        assert "Makefile.py already exists" in result.stdout

    def test_cli_rich_table_formatting(self):
        """Test Rich table formatting (list command)"""
        result = self.runner.invoke(app, ["list"])

        assert result.exit_code == 0
        # Table headers should be present
        assert "Command" in result.stdout
        assert "Dependencies" in result.stdout


class TestCLIEntryPoint:
    """Test CLI entry point functionality"""

    def test_cli_entry_point_import(self):
        """Test that CLI entry point can be imported"""
        # Should not raise exception
        from make.cli import cli_entry_point
        assert callable(cli_entry_point)

    def test_cli_entry_point_app_structure(self):
        """Test that CLI app has expected structure"""
        from make.cli import app

        # Should have registered commands
        assert len(app.registered_commands) >= 3
        # Should be a typer app
        assert hasattr(app, 'registered_commands')


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

    def teardown_method(self):
        """Cleanup test environment"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)

    def test_cli_parameter_with_equals_in_value(self):
        """Test parameter with equals sign in value"""
        result = self.runner.invoke(app, ["main", "hello", "APP_NAME=app=with=equals"])

        assert result.exit_code == 0
        assert "Running: hello" in result.stdout

    def test_cli_parameter_with_spaces(self):
        """Test parameter with spaces (should be quoted properly)"""
        result = self.runner.invoke(app, ["main", "hello", "APP_NAME=app with spaces"])

        assert result.exit_code == 0
        assert "Running: hello" in result.stdout

    def test_cli_empty_parameter_value(self):
        """Test parameter with empty value"""
        result = self.runner.invoke(app, ["main", "hello", "APP_NAME="])

        assert result.exit_code == 0
        # Should handle empty value gracefully