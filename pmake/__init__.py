"""Python Makefile (pmake) - Python-based command orchestration using Makefile.py

This package provides a Python alternative to Makefiles for project command
orchestration. It allows writing build/deployment commands in Python instead
of bash, making them more maintainable and testable.

Usage:
    Create a Makefile.py with your commands:

    ```python
    from pmake import sh, bash, _, dep

    # Read from env
    IMAGE = _('IMAGE')
    VERSION = _('VERSION', '0.0.1')

    def build():
        bash(f"docker build -t {IMAGE}:{VERSION} .")

    def push():
        sh.docker(f"push {IMAGE}:{VERSION}")

    @dep(build, push)
    def deploy():
        pass
    ```

    Then run from command line:
    ```bash
    pmake                    # Run first command
    pmake build              # Run specific command
    pmake deploy IMAGE=myapp # Run with parameter override
    ```
"""

from .env import _
from .shell import bash, sh
from .core import dep

__version__ = "0.1.0"
__all__ = ["bash", "sh", "_", "dep"]