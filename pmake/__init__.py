"""Python Makefile (pmake) - Python-based command orchestration using Makefile.py

This package provides a Python alternative to Makefiles for project command
orchestration. It allows writing build/deployment commands in Python instead
of bash, making them more maintainable and testable.

All shell commands automatically inherit your current environment, including
virtual environments, PATH settings, and any environment variables set through
the _() function.

Usage:
    Create a Makefile.py with your commands:

    ```python
    from pmake import sh, _, dep
    from pmake import docker, git, echo  # Direct command imports

    # Read from env (automatically available to shell commands)
    IMAGE = _('IMAGE')
    VERSION = _('VERSION', '0.0.1')

    def build():
        # Both options automatically inherit your environment (including venv)
        sh.docker("build", "-t", f"{IMAGE}:{VERSION}", ".")
        docker("build", "-t", f"{IMAGE}:{VERSION}", ".")

    def push():
        docker("push", f"{IMAGE}:{VERSION}")

    @dep(build, push)
    def deploy():
        pass
    ```

    Then run from command line:
    ```bash
    pmake                    # Run default command
    pmake build              # Run specific command directly
    pmake deploy IMAGE=myapp # Run with parameter override
    pmake --help             # Show all commands with descriptions and dependencies
    ```

Key Features:
    - Automatic environment inheritance (virtual environments, PATH, etc.)
    - Environment variables set via _() are available to all shell commands
    - Simple, lightweight implementation using sh.bake()
"""

import os
import sh as _sh

# Core pmake exports
from .env import _
from .core import dep

# Environment inheritance: All shell commands automatically inherit os.environ
# This ensures virtual environments, PATH, and other environment variables
# are available to shell commands without complex wrapper classes.
sh = _sh.bake(_env=os.environ)

__version__ = "0.1.0"
__all__ = ["sh", "_", "dep"]


def __getattr__(name: str):
    """Import any command from sh library dynamically with automatic environment inheritance.

    This allows imports like:
        from pmake import docker, git, echo, ls, grep

    All commands are automatically baked with os.environ, ensuring they inherit:
    - Virtual environment settings (VIRTUAL_ENV, PATH)
    - All current environment variables
    - Variables set via the _() function

    Simple implementation using sh.bake(_env=os.environ).
    """
    try:
        return getattr(_sh, name).bake(_env=os.environ)
    except AttributeError:
        # Try to create the command if it exists in PATH
        try:
            return _sh.Command(name).bake(_env=os.environ)
        except Exception:
            raise AttributeError(f"Command '{name}' not found in system PATH")