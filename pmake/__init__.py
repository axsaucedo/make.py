"""Python Makefile (pmake) - Python-based command orchestration using Makefile.py

This package provides a Python alternative to Makefiles for project command
orchestration. It allows writing build/deployment commands in Python instead
of bash, making them more maintainable and testable.

Usage:
    Create a Makefile.py with your commands:

    ```python
    from pmake import sh, _, dep
    from pmake import docker, git, echo  # Direct command imports

    # Read from env
    IMAGE = _('IMAGE')
    VERSION = _('VERSION', '0.0.1')

    def build():
        # Option 1: Use sh object
        sh.docker("build", "-t", f"{IMAGE}:{VERSION}", ".")

        # Option 2: Use direct imports
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
"""

import sh as _sh

# Core pmake exports
from .env import _
from .core import dep

# Expose amoffat/sh as sh
sh = _sh

__version__ = "0.1.0"
__all__ = ["sh", "_", "dep"]


def __getattr__(name: str):
    """Import any command from sh library dynamically.

    This allows imports like:
        from pmake import docker, git, echo, ls, grep

    Which is equivalent to:
        from sh import docker, git, echo, ls, grep
    """
    try:
        return getattr(_sh, name)
    except AttributeError:
        # Try to create the command if it exists in PATH
        try:
            cmd = _sh.Command(name)
            # Test if command exists by attempting to get help
            # This will raise an exception if command doesn't exist
            return cmd
        except Exception:
            raise AttributeError(f"Command '{name}' not found in system PATH")