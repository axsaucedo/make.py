"""End-to-end tests for complex hierarchical dependencies

Tests complex dependency scenarios:
- Multi-level hierarchical dependency chains (4+ levels deep)
- Wide dependency trees (single task with many dependencies)
- Convergent dependencies (multiple paths to same task)
- Complex execution order validation
- Mixed dependency patterns
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
import pytest
from io import StringIO
from contextlib import redirect_stdout

# Add make to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent))

from make.core import discover_commands, execute_command


class TestComplexHierarchicalDependencies:
    """Test complex multi-level dependency hierarchies"""

    def setup_method(self):
        """Setup test environment with complex makefile"""
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)

        # Copy complex makefile fixture
        fixture_path = Path(__file__).parent / "fixtures" / "complex_makefile.py"
        shutil.copy(fixture_path, Path(self.test_dir) / "Makefile.py")

        # Set up environment variables
        self.original_env = os.environ.copy()
        os.environ.update({
            'PROJECT': 'complex_test',
            'VERSION': '2.0.0',
            'ENVIRONMENT': 'production'
        })

    def teardown_method(self):
        """Cleanup test environment"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_discover_complex_commands(self):
        """Test discovery of complex makefile commands"""
        registry = discover_commands()
        commands = registry.list_commands()

        expected_commands = {
            'check_env', 'lint', 'unit_tests', 'validate', 'test_coverage',
            'quality_check', 'build', 'deploy', 'standalone_task', 'simple_chain'
        }
        assert set(commands) == expected_commands

    def test_complex_dependency_relationships(self):
        """Test complex dependency relationships are correctly discovered"""
        registry = discover_commands()

        # Level 2 dependencies
        assert set(registry.dependencies.get('validate', [])) == {'check_env', 'lint'}
        assert registry.dependencies.get('test_coverage', []) == ['unit_tests']

        # Level 1 dependencies
        assert set(registry.dependencies.get('quality_check', [])) == {'validate', 'test_coverage'}
        assert registry.dependencies.get('build', []) == ['check_env']

        # Top level dependencies
        assert set(registry.dependencies.get('deploy', [])) == {'quality_check', 'build'}

        # Simple chain
        assert registry.dependencies.get('simple_chain', []) == ['standalone_task']

    def test_four_level_execution_order(self):
        """Test execution order for 4-level deep dependencies"""
        registry = discover_commands()

        # Test the deepest task - deploy
        order = registry.get_execution_order('deploy')

        # Verify all required tasks are included
        required_tasks = {
            'check_env', 'lint', 'unit_tests', 'validate', 'test_coverage',
            'quality_check', 'build', 'deploy'
        }
        assert set(order) == required_tasks

        # Verify execution order constraints
        assert order.index('check_env') < order.index('validate')
        assert order.index('lint') < order.index('validate')
        assert order.index('unit_tests') < order.index('test_coverage')
        assert order.index('validate') < order.index('quality_check')
        assert order.index('test_coverage') < order.index('quality_check')
        assert order.index('quality_check') < order.index('deploy')
        assert order.index('build') < order.index('deploy')

    def test_convergent_dependencies(self):
        """Test convergent dependencies (multiple paths to same task)"""
        registry = discover_commands()

        # Both 'build' and 'validate' depend on 'check_env'
        # 'deploy' depends on both 'build' and 'quality_check'
        # 'quality_check' depends on 'validate'
        # This creates multiple paths to 'check_env'

        order = registry.get_execution_order('deploy')

        # check_env should appear only once despite multiple dependency paths
        check_env_occurrences = order.count('check_env')
        assert check_env_occurrences == 1

        # Verify check_env runs before all its dependents
        check_env_index = order.index('check_env')
        assert check_env_index < order.index('validate')
        assert check_env_index < order.index('build')

    def test_execute_complex_hierarchy(self):
        """Test executing the full complex hierarchy"""
        registry = discover_commands()

        # Capture output to verify execution
        output = StringIO()
        with redirect_stdout(output):
            execute_command(registry, 'deploy')

        output_text = output.getvalue()

        # Verify execution order through Running messages
        assert 'Running: check_env' in output_text
        assert 'Running: lint' in output_text
        assert 'Running: validate' in output_text
        assert 'Running: unit_tests' in output_text
        assert 'Running: test_coverage' in output_text
        assert 'Running: quality_check' in output_text
        assert 'Running: build' in output_text
        assert 'Running: deploy' in output_text

    def test_intermediate_task_execution(self):
        """Test executing intermediate level tasks"""
        registry = discover_commands()

        # Test quality_check (Level 1)
        output = StringIO()
        with redirect_stdout(output):
            execute_command(registry, 'quality_check')

        output_text = output.getvalue()

        # Should include all dependencies but not build/deploy
        assert 'Running: check_env' in output_text
        assert 'Running: lint' in output_text
        assert 'Running: unit_tests' in output_text
        assert 'Running: validate' in output_text
        assert 'Running: test_coverage' in output_text
        assert 'Running: quality_check' in output_text

        # Should not include build or deploy
        assert 'Running: build' not in output_text
        assert 'Running: deploy' not in output_text

    def test_isolated_chains(self):
        """Test isolated dependency chains"""
        registry = discover_commands()

        # Test simple isolated chain
        order = registry.get_execution_order('simple_chain')
        assert order == ['standalone_task', 'simple_chain']

        # Test standalone task
        order = registry.get_execution_order('standalone_task')
        assert order == ['standalone_task']


class TestWideDependencyTrees:
    """Test wide dependency tree patterns"""

    def setup_method(self):
        """Setup test environment with wide dependencies makefile"""
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)

        # Copy wide dependencies fixture
        fixture_path = Path(__file__).parent / "fixtures" / "wide_dependencies.py"
        shutil.copy(fixture_path, Path(self.test_dir) / "Makefile.py")

        # Set up environment variables
        self.original_env = os.environ.copy()
        os.environ.update({
            'WORKERS': '8',
            'CONFIG': 'wide_test_config'
        })

    def teardown_method(self):
        """Cleanup test environment"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_wide_fan_out_dependencies(self):
        """Test wide fan-out dependency pattern"""
        registry = discover_commands()

        # setup_all should depend on all 4 setup tasks
        deps = set(registry.dependencies.get('setup_all', []))
        expected_deps = {'setup_a', 'setup_b', 'setup_c', 'setup_d'}
        assert deps == expected_deps

    def test_wide_execution_order(self):
        """Test execution order for wide dependencies"""
        registry = discover_commands()

        order = registry.get_execution_order('setup_all')

        # All setup tasks should execute before setup_all
        setup_all_index = order.index('setup_all')
        assert order.index('setup_a') < setup_all_index
        assert order.index('setup_b') < setup_all_index
        assert order.index('setup_c') < setup_all_index
        assert order.index('setup_d') < setup_all_index

        # setup_all should be last
        assert order[-1] == 'setup_all'

    def test_convergent_wide_dependencies(self):
        """Test convergent dependencies in wide tree"""
        registry = discover_commands()

        # Both process_a and process_b depend on setup_all
        # final depends on both processes
        order = registry.get_execution_order('final')

        # setup_all should appear only once
        assert order.count('setup_all') == 1

        # Verify execution constraints
        setup_all_index = order.index('setup_all')
        process_a_index = order.index('process_a')
        process_b_index = order.index('process_b')
        final_index = order.index('final')

        assert setup_all_index < process_a_index
        assert setup_all_index < process_b_index
        assert process_a_index < final_index
        assert process_b_index < final_index

    def test_independent_chains_in_wide_tree(self):
        """Test independent chains within wide dependency tree"""
        registry = discover_commands()

        # Test independent chain 1
        order1 = registry.get_execution_order('chain1_end')
        assert order1 == ['chain1_start', 'chain1_end']

        # Test independent chain 2
        order2 = registry.get_execution_order('chain2_end')
        assert order2 == ['chain2_start', 'chain2_end']

        # Test mixed dependencies
        order_mixed = registry.get_execution_order('mixed_deps')
        assert 'setup_a' in order_mixed
        assert 'chain1_start' in order_mixed
        assert 'chain1_end' in order_mixed
        assert order_mixed.index('setup_a') < order_mixed.index('mixed_deps')
        assert order_mixed.index('chain1_end') < order_mixed.index('mixed_deps')

    def test_execute_wide_dependencies(self):
        """Test executing wide dependency pattern"""
        registry = discover_commands()

        output = StringIO()
        with redirect_stdout(output):
            execute_command(registry, 'final')

        output_text = output.getvalue()

        # Verify execution order through Running messages
        assert 'Running: setup_a' in output_text
        assert 'Running: setup_b' in output_text
        assert 'Running: setup_c' in output_text
        assert 'Running: setup_d' in output_text
        assert 'Running: setup_all' in output_text
        assert 'Running: process_a' in output_text
        assert 'Running: process_b' in output_text
        assert 'Running: final' in output_text

    def test_sh_proxy_in_wide_dependencies(self):
        """Test sh proxy functionality in complex dependencies"""
        registry = discover_commands()

        output = StringIO()
        with redirect_stdout(output):
            execute_command(registry, 'sh_proxy_test')

        output_text = output.getvalue()

        # Should include setup_c dependency and sh_proxy_test execution
        assert 'Running: setup_c' in output_text
        assert 'Running: sh_proxy_test' in output_text