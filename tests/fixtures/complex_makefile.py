"""Complex multi-level hierarchical dependency test fixture

This makefile demonstrates complex dependency chains with 4 levels:
Level 3 (Base): check_env, lint, unit_tests
Level 2 (Intermediate): validate, test_coverage
Level 1 (High-level): quality_check, build
Level 0 (Top): deploy

Dependency graph:
deploy → quality_check, build
quality_check → validate, test_coverage
validate → check_env, lint
test_coverage → unit_tests
build → check_env
"""

from pmake import sh, _, dep
from pmake import echo

# Environment variables with defaults
PROJECT = _('PROJECT', 'testapp')
VERSION = _('VERSION', '1.0.0')
ENVIRONMENT = _('ENVIRONMENT', 'dev')

# Level 3 - Base tasks (no dependencies)
def check_env():
    """Validate environment configuration"""
    echo(f'Environment check: {PROJECT} v{VERSION} in {ENVIRONMENT}')

def lint():
    """Run code linting"""
    echo('Linting code...')
    echo('Lint complete: No issues found')

def unit_tests():
    """Run unit tests"""
    echo('Running unit tests...')
    echo('Unit tests passed: 25/25')

# Level 2 - Intermediate tasks
@dep(check_env, lint)
def validate():
    """Code validation combining environment check and linting"""
    echo('Validation: Environment and code quality checks complete')

@dep(unit_tests)
def test_coverage():
    """Check test coverage"""
    echo('Checking test coverage...')
    echo('Coverage: 95% - Target met')

# Level 1 - High-level tasks
@dep(validate, test_coverage)
def quality_check():
    """Comprehensive quality assurance"""
    echo('Quality check: All validation and testing complete')

@dep(check_env)
def build():
    """Build the application"""
    echo(f'Building {PROJECT}:{VERSION} for {ENVIRONMENT}')
    echo('Build successful')

# Level 0 - Top level deployment
@dep(quality_check, build)
def deploy():
    """Deploy to target environment"""
    echo(f'Deploying {PROJECT}:{VERSION} to {ENVIRONMENT}')
    echo('Deployment successful')

# Additional isolated tasks for testing
def standalone_task():
    """Task with no dependencies"""
    echo('Standalone task executed')

@dep(standalone_task)
def simple_chain():
    """Simple single-dependency chain"""
    echo('Simple chain task executed')