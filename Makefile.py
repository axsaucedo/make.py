"""Makefile.py - Repository administration commands

This file contains all the admin commands for managing the pmake repository.
It demonstrates real-world usage of pmake for project orchestration.

Usage:
    pmake            # Run default task (help)
    pmake test       # Run tests
    pmake lint       # Run linting (if configured)
    pmake clean      # Clean build artifacts
    pmake install    # Install in development mode
    pmake build      # Build package
"""

from pmake import sh, _, dep
from pmake import rm, python, pip, find


# Environment configuration
PROJECT_NAME = _('PROJECT_NAME', 'pmake')
VERSION = _('VERSION', '0.1.0')
PYTHON_VERSION = _('PYTHON_VERSION', '3.12')

def clean():
    """Clean build artifacts, cache files, and test outputs"""
    # Remove Python cache files
    print("  Removing __pycache__ directories...")
    find(".", "-name", "__pycache__", "-type", "d", "-exec", "rm", "-rf", "{}", "+", _ok_code=[0, 1])

    # Remove .pyc files
    print("  Removing .pyc files...")
    find(".", "-name", "*.pyc", "-delete", _ok_code=[0, 1])

    # Remove build directories
    print("  Removing build directories...")
    rm("-rf", "build/", "dist/", "*.egg-info/", _ok_code=[0, 1])

    # Remove coverage files
    print("  Removing coverage files...")
    rm("-rf", ".coverage", "htmlcov/", _ok_code=[0, 1])

    # Remove pytest cache
    print("  Removing pytest cache...")
    rm("-rf", ".pytest_cache/", _ok_code=[0, 1])

    print("✅ Cleanup complete!")


def which():
    """Show Python executable path and verify virtual environment"""
    print("🐍 Python executable location:")
    python_path = sh.which("python")
    print(python_path)
    print()

    print("🔍 PATH analysis:")
    path_result = python("-c", "import os; path = os.environ.get('PATH', ''); print('First PATH entry:', path.split(':')[0] if path else 'NO PATH')")
    print(path_result.strip())

    venv_bin_check = python("-c", "import os; path = os.environ.get('PATH', ''); venv_bin = '/Users/asaucedo/Programming/make.py/.venv/bin'; print('Virtual env bin in PATH:', venv_bin in path)")
    print(venv_bin_check.strip())
    print()

    print("🔍 Virtual environment check:")
    result = python("-c", "import os; print('VIRTUAL_ENV:', os.environ.get('VIRTUAL_ENV', 'NOT SET'))")
    print("Environment variable result:", result.strip())
    print()
    result2 = python("-c", "import sys; print('Python executable:', sys.executable)")
    print("Executable check:", result2.strip())


def test():
    """Run all tests with coverage reporting"""
    print("🧪 Running tests with coverage...")
    python("-m", "pytest", "tests/", "-v")


def test_fast():
    """Run tests without coverage for faster feedback"""
    print("⚡ Running tests (fast mode - no coverage)...")
    python("-m", "pytest", "tests/", "-v", "--no-cov")


def install():
    """Install package in development mode"""
    print("📦 Installing package in development mode...")
    pip("install", "-e", ".[dev]")
    print("✅ Development installation complete!")

@dep(clean)
def build():
    """Build distribution packages"""
    print("🔨 Building distribution packages...")
    try:
        python("-m", "build")
        print("✅ Build complete! Check dist/ directory.")
    except:
        print("❌ Build failed - install build tools with: pip install build")
        print("   Or use: pip install -e .[dev]")

def check():
    """Check package metadata and dependencies"""
    print("🔍 Checking package metadata...")
    try:
        python("-m", "build", "--help")
        print("✅ Build tools available")
    except:
        print("⚠️  Build tools not available (install with: pip install build)")

    print("")
    print("🔍 Checking imports...")
    try:
        python("-c", "import pmake; print('✅ pmake imports successfully')")
        python("-c", "from pmake import sh, _, dep; print('✅ Core imports work')")
        print("✅ Import checks passed")
    except:
        print("❌ Import checks failed")

    print("")
    print("🔍 Running basic functionality test...")
    try:
        python("-c", "from pmake.core import discover_commands; print('✅ Core functionality works')")
        print("✅ All checks passed!")
    except:
        print("❌ Functionality check failed")

# Quality assurance workflow
@dep(clean, test)
def qa():
    """Run full quality assurance workflow"""
    print("✅ Quality assurance complete!")

# Development workflow
@dep(clean, install, test)
def dev():
    """Development setup workflow"""
    print("✅ Development environment ready!")

# Default task - show help (named to be first alphabetically)
def about():
    """Show help and available commands (default task)"""
    help()
