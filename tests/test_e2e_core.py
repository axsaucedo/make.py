"""End-to-end tests for Make.py core functionality

Tests the fundamental features of Make.py:
- Environment variable handling with _() function
- Shell execution with bash() and sh proxy
- Command discovery from Makefile.py
- Dependency resolution with @dep decorator
- Parameter override functionality
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
import pytest

# Add make to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent))

from pmake.core import discover_commands, execute_command, parse_parameters, get_default_command
from pmake.env import _, set_env, get_env_dict
from pmake.shell import bash, sh


class TestEnvironmentVariables:
    """Test environment variable handling with _() function"""

    def test_env_var_with_default(self):
        """Test _() function with default value"""
        # Test with non-existent var and default
        result = _('NONEXISTENT_VAR', 'default_value')
        assert result == 'default_value'

    def test_env_var_without_default_missing(self):
        """Test _() function without default for missing var"""
        with pytest.raises(ValueError, match="Environment variable 'MISSING_VAR' is required but not set"):
            _('MISSING_VAR')

    def test_env_var_existing(self):
        """Test _() function with existing environment variable"""
        os.environ['TEST_VAR'] = 'test_value'
        try:
            result = _('TEST_VAR')
            assert result == 'test_value'

            # Test that existing var overrides default
            result = _('TEST_VAR', 'default_value')
            assert result == 'test_value'
        finally:
            del os.environ['TEST_VAR']

    def test_set_env_function(self):
        """Test set_env helper function"""
        set_env(TEST_KEY='test_value', ANOTHER_KEY='another_value')

        assert os.environ['TEST_KEY'] == 'test_value'
        assert os.environ['ANOTHER_KEY'] == 'another_value'

        # Cleanup
        del os.environ['TEST_KEY']
        del os.environ['ANOTHER_KEY']


class TestShellExecution:
    """Test shell command execution"""

    def test_bash_simple_command(self):
        """Test bash() with simple command"""
        # Should not raise exception
        bash("echo 'test command'")

    def test_bash_with_capture(self):
        """Test bash() with output capture"""
        result = bash("echo 'captured output'", capture_output=True)
        assert result == 'captured output'

    def test_bash_command_failure(self):
        """Test bash() with failing command"""
        with pytest.raises(Exception):  # subprocess.CalledProcessError
            bash("exit 1")

    def test_bash_command_failure_no_check(self):
        """Test bash() with failing command but check=False"""
        # Should not raise exception
        bash("exit 1", check=False)

    def test_sh_proxy(self):
        """Test sh proxy functionality"""
        # Test simple command
        sh.echo("test sh proxy")

        # Test with arguments
        result = sh.echo("captured", capture_output=True)
        assert "captured" in result

    def test_sh_proxy_with_args(self):
        """Test sh proxy with multiple arguments"""
        result = sh.echo("hello", "world", capture_output=True)
        assert "hello world" in result


class TestCommandDiscovery:
    """Test command discovery functionality"""

    def setup_method(self):
        """Setup test environment"""
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

    def test_discover_commands_basic(self):
        """Test basic command discovery"""
        registry = discover_commands()
        commands = registry.list_commands()

        # Should find all functions from simple_makefile.py
        expected_commands = {
            'hello', 'version', 'test_bash', 'test_sh_proxy', 'greet', 'info',
            'welcome', 'step1', 'step2', 'step3', 'capture_test', 'comprehensive',
            'default_task'
        }

        assert set(commands) == expected_commands

    def test_discover_dependencies(self):
        """Test dependency discovery"""
        registry = discover_commands()

        # Test specific dependency relationships
        assert registry.dependencies.get('greet', []) == ['hello']
        assert set(registry.dependencies.get('info', [])) == {'version', 'test_bash'}
        assert set(registry.dependencies.get('welcome', [])) == {'hello', 'version'}
        assert registry.dependencies.get('step2', []) == ['step1']
        assert registry.dependencies.get('step3', []) == ['step2']

    def test_execution_order(self):
        """Test execution order calculation"""
        registry = discover_commands()

        # Test simple chain
        order = registry.get_execution_order('step3')
        assert order == ['step1', 'step2', 'step3']

        # Test multiple dependencies
        order = registry.get_execution_order('info')
        assert 'version' in order
        assert 'test_bash' in order
        assert 'info' in order
        assert order.index('info') > order.index('version')
        assert order.index('info') > order.index('test_bash')

    def test_get_default_command(self):
        """Test default command selection"""
        registry = discover_commands()
        default = get_default_command(registry)

        # Should return first command in alphabetical order or first defined
        commands = registry.list_commands()
        assert default in commands
        assert default is not None


class TestParameterHandling:
    """Test parameter parsing and override functionality"""

    def test_parse_parameters_no_params(self):
        """Test parameter parsing with no parameters"""
        command, params = parse_parameters(['hello'])
        assert command == 'hello'
        assert params == {}

    def test_parse_parameters_with_params(self):
        """Test parameter parsing with parameters"""
        command, params = parse_parameters(['hello', 'APP_NAME=testapp', 'VERSION=2.0.0'])
        assert command == 'hello'
        assert params == {'APP_NAME': 'testapp', 'VERSION': '2.0.0'}

    def test_parse_parameters_no_command(self):
        """Test parameter parsing with only parameters"""
        command, params = parse_parameters(['APP_NAME=testapp'])
        assert command is None
        assert params == {'APP_NAME': 'testapp'}

    def test_parse_parameters_empty(self):
        """Test parameter parsing with empty args"""
        command, params = parse_parameters([])
        assert command is None
        assert params == {}


class TestCommandExecution:
    """Test end-to-end command execution"""

    def setup_method(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)

        # Copy simple makefile fixture
        fixture_path = Path(__file__).parent / "fixtures" / "simple_makefile.py"
        shutil.copy(fixture_path, Path(self.test_dir) / "Makefile.py")

        # Set up test environment variables
        self.original_env = os.environ.copy()
        os.environ.update({
            'APP_NAME': 'testapp',
            'VERSION': '1.0.0',
            'ENVIRONMENT': 'test'
        })

    def teardown_method(self):
        """Cleanup test environment"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)

        # Restore environment
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_execute_simple_command(self):
        """Test executing a simple command"""
        registry = discover_commands()

        # Should not raise exception
        execute_command(registry, 'hello')

    def test_execute_command_with_dependencies(self):
        """Test executing command with dependencies"""
        registry = discover_commands()

        # Should execute dependencies first, then the command
        execute_command(registry, 'greet')  # depends on 'hello'
        execute_command(registry, 'step3')  # depends on step1 -> step2 -> step3

    def test_execute_command_with_params(self):
        """Test executing command with parameter overrides"""
        registry = discover_commands()

        params = {'APP_NAME': 'overridden_app', 'VERSION': '2.0.0'}
        execute_command(registry, 'hello', params)

        # Environment should be updated with overrides
        assert os.environ['APP_NAME'] == 'overridden_app'
        assert os.environ['VERSION'] == '2.0.0'

    def test_execute_nonexistent_command(self):
        """Test executing non-existent command"""
        registry = discover_commands()

        with pytest.raises(Exception):  # DependencyError
            execute_command(registry, 'nonexistent_command')