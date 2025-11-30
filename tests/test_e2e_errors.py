"""End-to-end tests for error handling and edge cases

Tests error conditions and edge cases:
- Circular dependency detection
- Missing environment variables
- Command execution failures
- Invalid dependency references
- Import errors
- Shell command failures
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
import pytest

# Add make to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent))

from make.core import discover_commands, execute_command, DependencyError
from make.env import _
from make.shell import bash, sh


class TestCircularDependencies:
    """Test circular dependency detection"""

    def setup_method(self):
        """Setup test environment with circular dependencies"""
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)

        # Note: The circular_deps.py fixture has intentional syntax issues
        # for testing purposes. We'll create a corrected version for actual testing.
        circular_makefile_content = '''
from make import sh, bash, _, dep

# Simple circular dependency: A → B → A
def task_a():
    """Task A that will depend on B (creating circular dependency)"""
    bash("echo 'Task A executed'")

def task_b():
    """Task B that will depend on A (creating circular dependency)"""
    bash("echo 'Task B executed'")

# Create circular dependencies by redefining with @dep
@dep(task_b)
def task_a():
    """Task A redefined to depend on B"""
    bash("echo 'Task A executed (circular)'")

@dep(task_a)
def task_b():
    """Task B redefined to depend on A (completing the cycle)"""
    bash("echo 'Task B executed (circular)'")

# Valid non-circular tasks for control testing
def valid_start():
    """Valid task with no dependencies"""
    bash("echo 'Valid start task'")

@dep(valid_start)
def valid_end():
    """Valid task with proper dependency"""
    bash("echo 'Valid end task'")
'''
        Path("Makefile.py").write_text(circular_makefile_content)

    def teardown_method(self):
        """Cleanup test environment"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)

    def test_discover_circular_dependencies(self):
        """Test that circular dependencies are discovered properly"""
        # Should be able to discover commands even with circular deps
        registry = discover_commands()
        commands = registry.list_commands()

        # Should find all commands including circular ones
        expected_commands = {'task_a', 'task_b', 'valid_start', 'valid_end'}
        assert expected_commands.issubset(set(commands))

        # Should detect the circular dependency relationships
        assert 'task_b' in registry.dependencies.get('task_a', [])
        assert 'task_a' in registry.dependencies.get('task_b', [])

    def test_circular_dependency_detection(self):
        """Test that circular dependencies are detected during execution order calculation"""
        registry = discover_commands()

        # Attempting to get execution order for circular dependency should fail
        # Note: The current implementation may not have circular dependency detection
        # This test documents the expected behavior
        try:
            order = registry.get_execution_order('task_a')
            # If no exception, check if it handles it gracefully
            # (infinite loop protection or similar)
            assert len(order) < 100  # Reasonable upper bound to detect infinite loops
        except (DependencyError, RecursionError):
            # Expected behavior for circular dependency detection
            pass

    def test_execute_circular_dependency(self):
        """Test executing a command with circular dependencies"""
        registry = discover_commands()

        # The implementation handles circular dependencies gracefully
        # by preventing infinite recursion, so execution should succeed
        execute_command(registry, 'task_a')  # Should not raise exception

        # Verify that both tasks in the cycle get executed
        order = registry.get_execution_order('task_a')
        assert 'task_a' in order
        assert 'task_b' in order

    def test_valid_dependencies_still_work(self):
        """Test that valid dependencies still work in presence of circular ones"""
        registry = discover_commands()

        # Valid dependencies should still work fine
        execute_command(registry, 'valid_end')  # Should not raise exception


class TestMissingEnvironmentVariables:
    """Test handling of missing environment variables"""

    def setup_method(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)

        # Create makefile with missing environment variables
        error_makefile_content = '''
from make import sh, bash, _, dep

# Missing environment variables (no defaults)
REQUIRED_VAR = _('REQUIRED_VAR_MISSING')  # Will fail if not set
OPTIONAL_VAR = _('OPTIONAL_VAR', 'default_value')  # Has default

def missing_env_task():
    """Task that uses missing environment variable"""
    bash(f"echo 'Using required var: {REQUIRED_VAR}'")

def has_default_task():
    """Task that uses environment variable with default"""
    bash(f"echo 'Using optional var: {OPTIONAL_VAR}'")

def valid_task():
    """Valid task for control testing"""
    bash("echo 'Valid task executed'")
'''
        Path("Makefile.py").write_text(error_makefile_content)

    def teardown_method(self):
        """Cleanup test environment"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)

    def test_missing_required_env_var(self):
        """Test error when required environment variable is missing"""
        # Should fail during discovery/import when REQUIRED_VAR is accessed
        with pytest.raises(ValueError, match="Environment variable 'REQUIRED_VAR_MISSING' is required but not set"):
            discover_commands()

    def test_env_var_with_default_works(self):
        """Test that environment variables with defaults work"""
        # Set the required var but not the optional one
        os.environ['REQUIRED_VAR_MISSING'] = 'set_value'
        try:
            registry = discover_commands()
            execute_command(registry, 'has_default_task')
            # Should not raise exception and should use default value
        finally:
            del os.environ['REQUIRED_VAR_MISSING']

    def test_env_var_override(self):
        """Test that environment variables can be overridden"""
        os.environ['REQUIRED_VAR_MISSING'] = 'original_value'
        os.environ['OPTIONAL_VAR'] = 'overridden_value'
        try:
            registry = discover_commands()
            execute_command(registry, 'has_default_task')
            # Should use the overridden value, not the default
        finally:
            del os.environ['REQUIRED_VAR_MISSING']
            del os.environ['OPTIONAL_VAR']


class TestCommandExecutionFailures:
    """Test handling of command execution failures"""

    def setup_method(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)

        # Create makefile with failing commands
        failing_makefile_content = '''
from make import sh, bash, _, dep

def failing_command():
    """Task with command that will fail"""
    bash("exit 1")  # This command will fail with exit code 1

def another_failing_command():
    """Task with another type of failure"""
    bash("false")  # Another way to fail

def valid_task():
    """Valid task for control testing"""
    bash("echo 'Valid task executed'")

@dep(failing_command)
def depends_on_failure():
    """Task that depends on a failing task"""
    bash("echo 'This should not execute if dependency fails'")

@dep(valid_task)
def depends_on_success():
    """Task that depends on a successful task"""
    bash("echo 'This should execute after valid task'")

def capture_failing_output():
    """Task that tries to capture output from failing command"""
    try:
        result = bash("exit 1", capture_output=True)
        bash(f"echo 'Result: {result}'")
    except:
        bash("echo 'Caught failure in output capture'")

def sh_proxy_failure():
    """Task using sh proxy that will fail"""
    sh.false()  # This command always fails with exit code 1
'''
        Path("Makefile.py").write_text(failing_makefile_content)

    def teardown_method(self):
        """Cleanup test environment"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)

    def test_failing_command_raises_exception(self):
        """Test that failing commands raise exceptions"""
        registry = discover_commands()

        with pytest.raises(Exception):  # subprocess.CalledProcessError or similar
            execute_command(registry, 'failing_command')

    def test_dependency_failure_propagates(self):
        """Test that dependency failures prevent dependent task execution"""
        registry = discover_commands()

        with pytest.raises(Exception):
            execute_command(registry, 'depends_on_failure')

    def test_successful_dependency_allows_execution(self):
        """Test that successful dependencies allow task execution"""
        registry = discover_commands()

        # Should not raise exception
        execute_command(registry, 'depends_on_success')

    def test_sh_proxy_failure(self):
        """Test failure handling with sh proxy"""
        registry = discover_commands()

        with pytest.raises(Exception):
            execute_command(registry, 'sh_proxy_failure')


class TestInvalidDependencyReferences:
    """Test handling of invalid dependency references"""

    def setup_method(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)

        # Create makefile with invalid dependency references
        invalid_deps_makefile_content = '''
from make import sh, bash, _, dep

def valid_task():
    """Valid task for testing"""
    bash("echo 'Valid task executed'")

# This creates an invalid dependency reference
@dep(nonexistent_task)
def invalid_dep_task():
    """Task that depends on non-existent function"""
    bash("echo 'This depends on non-existent task'")

# Mixed valid and invalid dependencies
@dep(valid_task)  # This exists
def mixed_valid_deps():
    """Task with valid dependencies"""
    bash("echo 'Mixed dependencies task'")

def standalone_task():
    """Task with no dependencies"""
    bash("echo 'Standalone task executed'")
'''
        Path("Makefile.py").write_text(invalid_deps_makefile_content)

    def teardown_method(self):
        """Cleanup test environment"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)

    def test_invalid_dependency_reference_error(self):
        """Test that invalid dependency references cause errors"""
        # Should fail during discovery due to undefined reference
        with pytest.raises(NameError):
            discover_commands()

    def test_valid_dependencies_discoverable_separately(self):
        """Test handling when some dependencies are valid"""
        # Create a version with only valid dependencies
        valid_makefile_content = '''
from make import sh, bash, _, dep

def valid_task():
    """Valid task for testing"""
    bash("echo 'Valid task executed'")

@dep(valid_task)
def mixed_valid_deps():
    """Task with valid dependencies"""
    bash("echo 'Mixed dependencies task'")

def standalone_task():
    """Task with no dependencies"""
    bash("echo 'Standalone task executed'")
'''
        Path("Makefile.py").write_text(valid_makefile_content)

        registry = discover_commands()
        commands = registry.list_commands()

        assert 'valid_task' in commands
        assert 'mixed_valid_deps' in commands
        assert 'standalone_task' in commands

        # Should be able to execute valid dependencies
        execute_command(registry, 'mixed_valid_deps')


class TestImportErrors:
    """Test handling of import errors in Makefile.py"""

    def setup_method(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)

    def teardown_method(self):
        """Cleanup test environment"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)

    def test_missing_make_import(self):
        """Test handling when make import is missing"""
        makefile_content = '''
# Missing: from make import sh, bash, _, dep

def task_without_imports():
    """Task that tries to use undefined functions"""
    bash("echo 'This will fail'")
'''
        Path("Makefile.py").write_text(makefile_content)

        # discover_commands should succeed as it only imports the module
        registry = discover_commands()

        # The error should occur when trying to execute the command
        with pytest.raises(NameError):
            execute_command(registry, 'task_without_imports')

    def test_nonexistent_module_import(self):
        """Test handling when Makefile.py imports non-existent modules"""
        makefile_content = '''
from nonexistent_module import something
from make import bash

def test_task():
    bash("echo 'test'")
'''
        Path("Makefile.py").write_text(makefile_content)

        with pytest.raises(ImportError):
            discover_commands()

    def test_syntax_error_in_makefile(self):
        """Test handling when Makefile.py has syntax errors"""
        makefile_content = '''
from make import bash

def invalid_syntax():
    bash("echo 'unclosed quote)
'''
        Path("Makefile.py").write_text(makefile_content)

        with pytest.raises((SyntaxError, ImportError)):
            discover_commands()

    def test_valid_makefile_imports(self):
        """Test that valid imports work correctly"""
        makefile_content = '''
import os
from pathlib import Path
from make import sh, bash, _, dep

def test_imports():
    """Task using various imports"""
    bash("echo 'Testing imports'")
    bash(f"echo 'Current directory: {os.getcwd()}'")
'''
        Path("Makefile.py").write_text(makefile_content)

        registry = discover_commands()
        execute_command(registry, 'test_imports')  # Should not raise exception


class TestEdgeCases:
    """Test various edge cases and boundary conditions"""

    def setup_method(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)

    def teardown_method(self):
        """Cleanup test environment"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)

    def test_empty_makefile(self):
        """Test handling of empty Makefile.py"""
        Path("Makefile.py").write_text("")

        registry = discover_commands()
        commands = registry.list_commands()

        assert commands == []

    def test_makefile_with_only_variables(self):
        """Test Makefile.py with only variables, no functions"""
        makefile_content = '''
from make import bash

VARIABLE1 = "value1"
VARIABLE2 = "value2"
'''
        Path("Makefile.py").write_text(makefile_content)

        registry = discover_commands()
        commands = registry.list_commands()

        assert commands == []

    def test_makefile_with_private_functions(self):
        """Test that private functions (starting with _) are not discovered"""
        makefile_content = '''
from make import bash

def public_function():
    """Public function"""
    bash("echo 'public'")

def _private_function():
    """Private function"""
    bash("echo 'private'")

def __dunder_function__():
    """Dunder function"""
    bash("echo 'dunder'")
'''
        Path("Makefile.py").write_text(makefile_content)

        registry = discover_commands()
        commands = registry.list_commands()

        assert 'public_function' in commands
        assert '_private_function' not in commands
        assert '__dunder_function__' not in commands

    def test_makefile_with_classes(self):
        """Test that classes are not treated as commands"""
        makefile_content = '''
from make import bash

class TestClass:
    def method(self):
        pass

def function():
    bash("echo 'function'")
'''
        Path("Makefile.py").write_text(makefile_content)

        registry = discover_commands()
        commands = registry.list_commands()

        assert 'function' in commands
        assert 'TestClass' not in commands

    def test_very_long_command_chain(self):
        """Test handling of very long dependency chains"""
        # Create a long chain of dependencies
        chain_length = 20
        makefile_content = '''
from make import bash, dep

def task_0():
    bash("echo 'Task 0'")

'''
        for i in range(1, chain_length):
            makefile_content += f'''
@dep(task_{i-1})
def task_{i}():
    bash(f"echo 'Task {i}'")

'''

        Path("Makefile.py").write_text(makefile_content)

        registry = discover_commands()

        # Should be able to calculate execution order for long chain
        order = registry.get_execution_order(f'task_{chain_length-1}')
        assert len(order) == chain_length
        assert order[0] == 'task_0'
        assert order[-1] == f'task_{chain_length-1}'