"""Environment variable handling for Python Makefile (pmake)

This module provides the `_()` function for accessing environment variables
with optional default values, as used in Makefile.py.
"""

import os
from typing import Optional, Any


def _(name: str, default: Optional[Any] = None) -> str:
    """Get environment variable with optional default value.

    Args:
        name: Environment variable name
        default: Default value if environment variable is not set

    Returns:
        Environment variable value or default

    Examples:
        >>> DOCKER_REPO = _('DOCKER_REPO')
        >>> VERSION = _('VERSION', '0.0.1')  # With default
    """
    value = os.environ.get(name)
    if value is None:
        if default is None:
            raise ValueError(f"Environment variable '{name}' is required but not set")
        return str(default)
    return value


def set_env(**kwargs) -> None:
    """Set environment variables for testing or parameter overrides.

    Args:
        **kwargs: Environment variables to set

    Examples:
        >>> set_env(VERSION='1.0.0', IMAGE='myapp')
    """
    for key, value in kwargs.items():
        os.environ[key] = str(value)


def get_env_dict() -> dict[str, str]:
    """Get all environment variables as a dictionary.

    Returns:
        Dictionary of all environment variables
    """
    return dict(os.environ)