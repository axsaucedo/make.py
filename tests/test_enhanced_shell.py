"""Tests for enhanced shell with automatic environment inheritance"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
import pytest

# Add pmake to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent))

from pmake import sh, _, python, pip


class TestEnhancedShellEnvironment:
    """Test enhanced shell environment inheritance"""

    def setup_method(self):
        """Setup test environment"""
        # Store original environment
        self.original_env = dict(os.environ)

    def teardown_method(self):
        """Cleanup test environment"""
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_current_environment_inheritance(self):
        """Test that sh commands inherit current environment including venv"""
        # Current python executable (should be in venv)
        current_python = sys.executable

        # Test that pmake python command uses same executable
        result = python("-c", "import sys; print(sys.executable)")
        sh_python = result.strip()

        assert current_python == sh_python, f"Expected {current_python}, got {sh_python}"

    def test_environment_variable_inheritance(self):
        """Test that existing environment variables are inherited"""
        # Use an existing environment variable (set before import)
        existing_var = os.environ.get('VIRTUAL_ENV', 'NOT_SET')
        if existing_var == 'NOT_SET':
            pytest.skip("VIRTUAL_ENV not set")

        # Test that shell commands get this variable
        result = python("-c", "import os; print(os.environ.get('VIRTUAL_ENV', 'NOT_FOUND'))")
        shell_var = result.strip()

        assert shell_var == existing_var

    def test_basic_shell_functionality(self):
        """Test that basic shell functionality works"""
        # Test that we can run simple commands
        result = python("-c", "print('Hello from shell')")
        assert "Hello from shell" in result

    def test_virtual_env_variables_inherited(self):
        """Test that VIRTUAL_ENV and related variables are inherited"""
        # Skip if not in a virtual environment
        if 'VIRTUAL_ENV' not in os.environ:
            pytest.skip("Not in a virtual environment")

        virtual_env = os.environ['VIRTUAL_ENV']

        # Test that shell commands see VIRTUAL_ENV
        result = python("-c", "import os; print(os.environ.get('VIRTUAL_ENV', 'NOT_FOUND'))")
        shell_virtual_env = result.strip()

        assert shell_virtual_env == virtual_env, f"Expected {virtual_env}, got {shell_virtual_env}"

    def test_path_variable_inheritance(self):
        """Test that PATH variable is properly inherited"""
        current_path = os.environ.get('PATH', '')

        # Test that shell commands see the same PATH
        result = python("-c", "import os; print(len(os.environ.get('PATH', '')))")
        shell_path_length = int(result.strip())

        # PATH should be non-empty and similar length
        assert shell_path_length > 0, "PATH should not be empty in shell"
        assert abs(len(current_path) - shell_path_length) < 100, "PATH lengths should be similar"

    def test_multiple_commands_work(self):
        """Test that multiple different commands work"""
        # Test python command
        python_result = python("-c", "print('python works')")
        assert "python works" in python_result

        # Test sh.echo command
        echo_result = sh.echo("shell works")
        assert "shell works" in echo_result