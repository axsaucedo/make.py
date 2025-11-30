"""Shell execution for Python Makefile (pmake)

This module provides bash() function and sh proxy object using standard library subprocess.
Basic UV integration - users manually call bash("uv sync") etc. in their functions.
"""

import subprocess
import sys
from typing import Any, Optional


def bash(command: str, check: bool = True, capture_output: bool = False) -> Optional[str]:
    """Execute a bash command using subprocess.

    Args:
        command: The bash command to execute
        check: If True, raises exception on non-zero exit code
        capture_output: If True, returns command output instead of printing it

    Returns:
        Command output if capture_output=True, otherwise None

    Raises:
        subprocess.CalledProcessError: If check=True and command fails

    Examples:
        >>> bash("docker build -t myapp:latest .")
        >>> bash("uv sync")  # Basic UV integration
        >>> output = bash("git rev-parse HEAD", capture_output=True)
    """
    try:
        if capture_output:
            result = subprocess.run(
                command,
                shell=True,
                check=check,
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        else:
            subprocess.run(command, shell=True, check=check)
            return None
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {command}", file=sys.stderr)
        print(f"Exit code: {e.returncode}", file=sys.stderr)
        if e.stderr:
            print(f"Error: {e.stderr}", file=sys.stderr)
        raise


class ShellProxy:
    """Proxy object for structured shell command execution using subprocess.

    Supports the syntax: sh.docker("push myrepo/myimage:v1.0")
    """

    def __init__(self, command_parts: list[str] = None):
        self._command_parts = command_parts or []

    def __getattr__(self, name: str) -> "ShellProxy":
        """Add command part when accessing attribute."""
        return ShellProxy(self._command_parts + [name.replace('_', '-')])

    def __call__(self, *args: Any, check: bool = True, capture_output: bool = False) -> Optional[str]:
        """Execute the built command with arguments.

        Args:
            *args: Command arguments
            check: If True, raises exception on non-zero exit code (default: True)
            capture_output: If True, returns output (default: False)

        Returns:
            Command output if capture_output=True, otherwise None

        Examples:
            >>> sh.docker(f"push {DOCKER_REPO}/{IMAGE}:{VERSION}")
            >>> sh.git("status")
            >>> output = sh.git("rev-parse HEAD", capture_output=True)
        """
        # Build the full command
        command_parts = self._command_parts[:]

        # Add arguments
        for arg in args:
            command_parts.append(str(arg))

        command = ' '.join(command_parts)
        return bash(command, check=check, capture_output=capture_output)


# Create the global sh instance
sh = ShellProxy()