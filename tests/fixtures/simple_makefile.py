"""Simple makefile for basic functionality testing

This makefile contains straightforward tasks to test core functionality:
- Environment variable handling
- Basic shell execution
- Simple dependency chains
- Parameter override testing
"""

from pmake import sh, bash, _, dep

# Environment variables for testing
APP_NAME = _('APP_NAME', 'myapp')
VERSION = _('VERSION', '1.0.0')
ENVIRONMENT = _('ENVIRONMENT', 'test')

def hello():
    """Simple greeting task"""
    bash(f"echo 'Hello from {APP_NAME}!'")

def version():
    """Display version information"""
    bash(f"echo 'Version: {VERSION}'")
    bash(f"echo 'Environment: {ENVIRONMENT}'")

def test_bash():
    """Test bash function with various operations"""
    bash("echo 'Testing bash function'")
    bash("echo 'Current directory:' && pwd")
    bash("echo 'Environment variables:' && env | grep -E '^(APP_NAME|VERSION|ENVIRONMENT)=' || true")

def test_sh_proxy():
    """Test sh proxy functionality"""
    sh.echo("Testing sh proxy")
    sh.echo(f"App: {APP_NAME}")
    sh.date()

@dep(hello)
def greet():
    """Greeting with dependency"""
    bash("echo 'Greetings after hello!'")

@dep(version, test_bash)
def info():
    """Display comprehensive info"""
    bash("echo 'All information displayed'")

@dep(hello, version)
def welcome():
    """Welcome message with multiple dependencies"""
    bash(f"echo 'Welcome to {APP_NAME} v{VERSION}!'")

# Chain of dependencies for testing execution order
def step1():
    """First step in chain"""
    bash("echo 'Step 1 completed'")

@dep(step1)
def step2():
    """Second step in chain"""
    bash("echo 'Step 2 completed'")

@dep(step2)
def step3():
    """Third step in chain"""
    bash("echo 'Step 3 completed'")

# Task with output capture
def capture_test():
    """Test output capture functionality"""
    result = bash("echo 'captured output'", capture_output=True)
    bash(f"echo 'Captured: {result}'")

# Task that uses all environment variables
@dep(capture_test)
def comprehensive():
    """Comprehensive task using all features"""
    bash(f"echo 'Comprehensive test for {APP_NAME} v{VERSION} in {ENVIRONMENT}'")
    sh.echo("Using sh proxy in comprehensive test")
    bash("echo 'Comprehensive test completed'")

# Task with no dependencies for default execution testing
def default_task():
    """Default task (first in file) for testing default command selection"""
    bash("echo 'This is the default task'")
    bash(f"echo 'Running {APP_NAME} default task'")