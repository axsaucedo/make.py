"""Error condition test fixture

This makefile contains various error scenarios to test error handling:
1. Missing required environment variables
2. Command execution failures
3. Invalid dependency references
4. Import errors
5. Shell command errors
"""

from pmake import sh, bash, _, dep

# Missing environment variables (no defaults)
REQUIRED_VAR = _('REQUIRED_VAR')  # Will fail if not set
OPTIONAL_VAR = _('OPTIONAL_VAR', 'default_value')  # Has default
MISSING_VAR = _('THIS_VAR_DOES_NOT_EXIST')  # Will fail

def missing_env_task():
    """Task that uses missing environment variable"""
    bash(f"echo 'Using required var: {REQUIRED_VAR}'")
    bash(f"echo 'Using missing var: {MISSING_VAR}'")

# Command execution failures
def failing_command():
    """Task with command that will fail"""
    bash("exit 1")  # This command will fail with exit code 1

def another_failing_command():
    """Task with another type of failure"""
    bash("command_that_does_not_exist")  # Non-existent command

def invalid_shell_syntax():
    """Task with invalid shell syntax"""
    bash("echo 'unclosed quote")  # Invalid shell syntax

# Tasks with invalid dependency references
def nonexistent_dep_reference():
    """This will be redefined with invalid dependency"""
    bash("echo 'Original function'")

@dep(task_that_does_not_exist)  # Invalid dependency reference
def nonexistent_dep_reference():
    """Task that depends on non-existent function"""
    bash("echo 'This depends on non-existent task'")

# Mixed valid and invalid dependencies
def valid_task():
    """Valid task for mixed dependency testing"""
    bash("echo 'Valid task executed'")

@dep(valid_task, another_nonexistent_task)  # One valid, one invalid
def mixed_deps_error():
    """Task with mixed valid/invalid dependencies"""
    bash("echo 'Mixed dependencies task'")

# Task that uses sh proxy with failing command
@dep(valid_task)
def sh_proxy_failure():
    """Task using sh proxy that will fail"""
    sh.false()  # This command always fails with exit code 1

# Task with output capture that fails
def capture_failing_output():
    """Task that tries to capture output from failing command"""
    result = bash("exit 1", capture_output=True)
    bash(f"echo 'Result: {result}'")

# Task with complex shell command that might fail
def complex_shell_failure():
    """Task with complex shell operations that can fail"""
    bash("cd /nonexistent/directory && ls -la")

# Valid tasks for control testing
def control_task():
    """Valid task for control testing"""
    bash("echo 'Control task - should work'")

@dep(control_task)
def dependent_control():
    """Valid dependent task"""
    bash("echo 'Dependent control task - should work'")

# Task that depends on failing task (for cascade failure testing)
@dep(failing_command)
def depends_on_failure():
    """Task that depends on a failing task"""
    bash("echo 'This should not execute if dependency fails'")