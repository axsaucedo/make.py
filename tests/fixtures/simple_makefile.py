"""Simple makefile for basic functionality testing

This makefile contains straightforward tasks to test core functionality:
- Environment variable handling
- Basic shell execution using amoffat/sh
- Simple dependency chains
- Parameter override testing
"""

from pmake import sh, _, dep
from pmake import echo, pwd, env, grep

# Environment variables for testing
APP_NAME = _('APP_NAME', 'myapp')
VERSION = _('VERSION', '1.0.0')
ENVIRONMENT = _('ENVIRONMENT', 'test')

def hello():
    """Simple greeting task"""
    echo(f"Hello from {APP_NAME}!")

def version():
    """Display version information"""
    echo(f"Version: {VERSION}")
    echo(f"Environment: {ENVIRONMENT}")

def test_sh_commands():
    """Test various sh commands"""
    echo("Testing sh commands")
    echo("Current directory:")
    pwd()
    echo("Environment variables:")
    # Use sh.bash for complex shell operations that need shell features
    sh.bash("-c", f"env | grep -E '^(APP_NAME|VERSION|ENVIRONMENT)=' || true")

def test_sh_proxy():
    """Test sh proxy functionality"""
    sh.echo("Testing sh proxy")
    sh.echo(f"App: {APP_NAME}")
    sh.date()

@dep(hello)
def greet():
    """Greeting with dependency"""
    echo("Greetings after hello!")

@dep(version, test_sh_commands)
def info():
    """Display comprehensive info"""
    echo("All information displayed")

@dep(hello, version)
def welcome():
    """Welcome message with multiple dependencies"""
    echo(f"Welcome to {APP_NAME} v{VERSION}!")

# Chain of dependencies for testing execution order
def step1():
    """First step in chain"""
    echo("Step 1 completed")

@dep(step1)
def step2():
    """Second step in chain"""
    echo("Step 2 completed")

@dep(step2)
def step3():
    """Third step in chain"""
    echo("Step 3 completed")

# Task with output capture
def capture_test():
    """Test output capture functionality"""
    result = str(echo("captured output")).strip()
    echo(f"Captured: {result}")

# Task that uses all environment variables
@dep(capture_test)
def comprehensive():
    """Comprehensive task using all features"""
    echo(f"Comprehensive test for {APP_NAME} v{VERSION} in {ENVIRONMENT}")
    sh.echo("Using sh proxy in comprehensive test")
    echo("Comprehensive test completed")

# Task with no dependencies for default execution testing
def default_task():
    """Default task (first in file) for testing default command selection"""
    echo("This is the default task")
    echo(f"Running {APP_NAME} default task")