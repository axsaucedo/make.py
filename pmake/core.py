"""Core functionality for Python Makefile (pmake)

This module provides command discovery, @dep decorator, and execution orchestration
for function-based commands (Option 1).
"""

import importlib.util
import inspect
import os
import sys
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

from .env import set_env


class DependencyError(Exception):
    """Raised when there are issues with command dependencies."""
    pass


class CommandRegistry:
    """Registry for discovered commands and their dependencies."""

    def __init__(self):
        self.commands: Dict[str, Callable] = {}
        self.dependencies: Dict[str, List[str]] = {}

    def register_command(self, name: str, func: Callable) -> None:
        """Register a command function."""
        self.commands[name] = func

    def register_dependencies(self, name: str, deps: List[str]) -> None:
        """Register dependencies for a command."""
        self.dependencies[name] = deps

    def get_execution_order(self, command: str) -> List[str]:
        """Get the execution order for a command including its dependencies."""
        visited = set()
        result = []

        def visit(cmd: str) -> None:
            if cmd in visited:
                return
            if cmd not in self.commands:
                raise DependencyError(f"Unknown command: {cmd}")

            visited.add(cmd)
            # Execute dependencies first
            for dep in self.dependencies.get(cmd, []):
                visit(dep)
            result.append(cmd)

        visit(command)
        return result

    def list_commands(self) -> List[str]:
        """List all registered commands."""
        return list(self.commands.keys())


# Global command registry
_registry = CommandRegistry()


def dep(*dependencies: Callable) -> Callable:
    """Decorator to specify command dependencies.

    Args:
        *dependencies: Functions that should be executed before this command

    Examples:
        >>> @dep(build_images, push_images)
        ... def build_and_push():
        ...     pass
    """
    def decorator(func: Callable) -> Callable:
        dep_names = [d.__name__ for d in dependencies]
        _registry.register_dependencies(func.__name__, dep_names)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper
    return decorator


def discover_commands(makefile_path: str = "Makefile.py") -> CommandRegistry:
    """Discover commands from a Makefile.py file.

    Args:
        makefile_path: Path to the Makefile.py file

    Returns:
        CommandRegistry with discovered commands

    Raises:
        FileNotFoundError: If Makefile.py doesn't exist
        ImportError: If there are issues importing Makefile.py
    """
    if not os.path.exists(makefile_path):
        raise FileNotFoundError(f"Makefile.py not found at: {makefile_path}")

    # Clear the registry
    global _registry
    _registry = CommandRegistry()

    # Load the Makefile.py module
    spec = importlib.util.spec_from_file_location("makefile", makefile_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load {makefile_path}")

    makefile = importlib.util.module_from_spec(spec)

    # Add current directory to path so imports work
    original_path = sys.path[:]
    sys.path.insert(0, str(Path(makefile_path).parent.absolute()))

    try:
        spec.loader.exec_module(makefile)
    finally:
        # Restore original path
        sys.path[:] = original_path

    # Discover callable functions (excluding private ones)
    for name, obj in inspect.getmembers(makefile):
        if (inspect.isfunction(obj) and
            not name.startswith('_') and
            obj.__module__ == makefile.__name__):
            _registry.register_command(name, obj)

    return _registry


def execute_command(registry: CommandRegistry, command_name: str, params: Optional[Dict[str, str]] = None) -> None:
    """Execute a command and its dependencies.

    Args:
        registry: Command registry
        command_name: Name of command to execute
        params: Parameter overrides from CLI (PARAM=value)

    Raises:
        DependencyError: If command or dependencies are not found
    """
    if params:
        # Set environment variables for parameter overrides
        set_env(**params)

    # Get execution order
    execution_order = registry.get_execution_order(command_name)

    # Execute commands in order
    for cmd_name in execution_order:
        func = registry.commands[cmd_name]
        print(f"Running: {cmd_name}")
        try:
            func()
        except Exception as e:
            print(f"Error in command '{cmd_name}': {e}", file=sys.stderr)
            raise


def parse_parameters(args: List[str]) -> tuple[Optional[str], Dict[str, str]]:
    """Parse command line arguments for command and parameters.

    Args:
        args: Command line arguments

    Returns:
        Tuple of (command_name, parameters_dict)

    Examples:
        >>> parse_parameters(['build_images', 'IMAGE=myapp', 'VERSION=1.0'])
        ('build_images', {'IMAGE': 'myapp', 'VERSION': '1.0'})
    """
    command = None
    params = {}

    for arg in args:
        if '=' in arg:
            key, value = arg.split('=', 1)
            params[key] = value
        elif command is None:
            command = arg
        else:
            # Multiple commands not supported in this simple version
            raise ValueError(f"Unexpected argument: {arg}")

    return command, params


def get_default_command(registry: CommandRegistry) -> Optional[str]:
    """Get the first command as default (matching pmake behavior)."""
    commands = registry.list_commands()
    return commands[0] if commands else None