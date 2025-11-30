from pmake import _, dep
from pmake import rm, python, pip, find, uv


# Environment configuration
PROJECT_NAME = _('PROJECT_NAME', 'pmake')
VERSION = _('VERSION', '0.1.0')
PYTHON_VERSION = _('PYTHON_VERSION', '3.12')


def clean():
    """Clean build artifacts, cache files, and test outputs"""
    find(".", "-name", "__pycache__", "-type", "d", "-exec", "rm", "-rf", "{}", "+", _ok_code=[0, 1])

    # Remove .pyc files
    print("Removing .pyc files...")
    find(".", "-name", "*.pyc", "-delete", _ok_code=[0, 1])

    # Remove build directories
    print("Removing build directories...")
    rm("-rf", "build/", "dist/", "*.egg-info/", _ok_code=[0, 1])

    # Remove coverage files
    print("Removing coverage files...")
    rm("-rf", ".coverage", "htmlcov/", _ok_code=[0, 1])

    # Remove pytest cache
    print("Removing pytest cache...")
    rm("-rf", ".pytest_cache/", _ok_code=[0, 1])

    print("Cleanup complete.")


@dep(clean)
def test():
    """Run all tests with coverage reporting"""
    python("-m", "pytest", "tests/", "-v")


@dep(clean)
def test_fast():
    """Run tests without coverage for faster feedback"""
    python("-m", "pytest", "tests/", "-v", "--no-cov")


def install_dev():
    """Install package in development mode"""
    print("Installing package in development mode...")
    pip("install", "-e", ".[dev]")


@dep(clean)
def publish():
    """Publish latest package"""
    uv("build")
    uv("publish")

