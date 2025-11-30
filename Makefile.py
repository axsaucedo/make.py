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
from pmake import rm, python, pip

def _echo(msg):
    """Print message to stdout (private helper)"""
    print(msg)

# Environment configuration
PROJECT_NAME = _('PROJECT_NAME', 'pmake')
VERSION = _('VERSION', '0.1.0')
PYTHON_VERSION = _('PYTHON_VERSION', '3.12')

def help():
    """Show available commands and usage"""
    _echo("📋 Available pmake commands:")
    _echo("")
    _echo("🧪 Testing & Quality:")
    _echo("  pmake test          - Run all tests with coverage")
    _echo("  pmake test_fast     - Run tests without coverage")
    _echo("")
    _echo("🔧 Development:")
    _echo("  pmake install       - Install package in development mode")
    _echo("  pmake clean         - Clean build artifacts and cache")
    _echo("  pmake build         - Build distribution packages")
    _echo("")
    _echo("📦 Package Management:")
    _echo("  pmake deps          - Show dependency information")
    _echo("  pmake check         - Check package metadata and dependencies")
    _echo("")
    _echo("🔄 Workflows:")
    _echo("  pmake qa            - Run quality assurance (clean + test)")
    _echo("  pmake dev           - Setup development environment")
    _echo("")
    _echo("ℹ️  Info:")
    _echo("  pmake info          - Show project information")
    _echo("  pmake help          - Show this help message")
    _echo("  pmake               - Show this help (default)")
    _echo("")
    _echo("💡 Tip: Use 'pmake --help' to see all commands with descriptions and dependencies")

def info():
    """Display project information"""
    _echo(f"📦 Project: {PROJECT_NAME}")
    _echo(f"📋 Version: {VERSION}")
    _echo(f"🐍 Python: {PYTHON_VERSION}")
    _echo("")
    _echo("📁 Structure:")
    # Use bash with proper pipe syntax for complex shell operations
    sh.bash("-c", "find . -name '*.py' -path './pmake/*' | head -5")

def clean():
    """Clean build artifacts, cache files, and test outputs"""
    _echo("🧹 Cleaning build artifacts...")

    # Remove Python cache files
    _echo("  Removing __pycache__ directories...")
    sh.find(".", "-name", "__pycache__", "-type", "d", "-exec", "rm", "-rf", "{}", "+", _ok_code=[0, 1])

    # Remove .pyc files
    _echo("  Removing .pyc files...")
    sh.find(".", "-name", "*.pyc", "-delete", _ok_code=[0, 1])

    # Remove build directories
    _echo("  Removing build directories...")
    rm("-rf", "build/", "dist/", "*.egg-info/", _ok_code=[0, 1])

    # Remove coverage files
    _echo("  Removing coverage files...")
    rm("-rf", ".coverage", "htmlcov/", _ok_code=[0, 1])

    # Remove pytest cache
    _echo("  Removing pytest cache...")
    rm("-rf", ".pytest_cache/", _ok_code=[0, 1])

    _echo("✅ Cleanup complete!")

def test():
    """Run all tests with coverage reporting"""
    _echo("🧪 Running tests with coverage...")
    python("-m", "pytest", "tests/", "-v")

def test_fast():
    """Run tests without coverage for faster feedback"""
    _echo("⚡ Running tests (fast mode - no coverage)...")
    python("-m", "pytest", "tests/", "-v", "--no-cov")

def install():
    """Install package in development mode"""
    _echo("📦 Installing package in development mode...")
    pip("install", "-e", ".[dev]")
    _echo("✅ Development installation complete!")

@dep(clean)
def build():
    """Build distribution packages"""
    _echo("🔨 Building distribution packages...")
    try:
        python("-m", "build")
        _echo("✅ Build complete! Check dist/ directory.")
    except:
        _echo("❌ Build failed - install build tools with: pip install build")
        _echo("   Or use: pip install -e .[dev]")

def check():
    """Check package metadata and dependencies"""
    _echo("🔍 Checking package metadata...")
    try:
        python("-m", "build", "--help")
        _echo("✅ Build tools available")
    except:
        _echo("⚠️  Build tools not available (install with: pip install build)")

    _echo("")
    _echo("🔍 Checking imports...")
    try:
        python("-c", "import pmake; print('✅ pmake imports successfully')")
        python("-c", "from pmake import sh, _, dep; print('✅ Core imports work')")
        _echo("✅ Import checks passed")
    except:
        _echo("❌ Import checks failed")

    _echo("")
    _echo("🔍 Running basic functionality test...")
    try:
        python("-c", "from pmake.core import discover_commands; print('✅ Core functionality works')")
        _echo("✅ All checks passed!")
    except:
        _echo("❌ Functionality check failed")

# Quality assurance workflow
@dep(clean, test)
def qa():
    """Run full quality assurance workflow"""
    _echo("✅ Quality assurance complete!")

# Development workflow
@dep(clean, install, test)
def dev():
    """Development setup workflow"""
    _echo("✅ Development environment ready!")

# Default task - show help (named to be first alphabetically)
def about():
    """Show help and available commands (default task)"""
    help()
