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

from make import sh, bash, _, dep

# Environment variables with defaults
PROJECT = _('PROJECT', 'testapp')
VERSION = _('VERSION', '1.0.0')
ENVIRONMENT = _('ENVIRONMENT', 'dev')

# Level 3 - Base tasks (no dependencies)
def check_env():
    """Validate environment configuration"""
    bash(f"echo 'Environment check: {PROJECT} v{VERSION} in {ENVIRONMENT}'")

def lint():
    """Run code linting"""
    bash("echo 'Linting code...'")
    bash("echo 'Lint complete: No issues found'")

def unit_tests():
    """Run unit tests"""
    bash("echo 'Running unit tests...'")
    bash("echo 'Unit tests passed: 25/25'")

# Level 2 - Intermediate tasks
@dep(check_env, lint)
def validate():
    """Code validation combining environment check and linting"""
    bash("echo 'Validation: Environment and code quality checks complete'")

@dep(unit_tests)
def test_coverage():
    """Check test coverage"""
    bash("echo 'Checking test coverage...'")
    bash("echo 'Coverage: 95% - Target met'")

# Level 1 - High-level tasks
@dep(validate, test_coverage)
def quality_check():
    """Comprehensive quality assurance"""
    bash("echo 'Quality check: All validation and testing complete'")

@dep(check_env)
def build():
    """Build the application"""
    bash(f"echo 'Building {PROJECT}:{VERSION} for {ENVIRONMENT}'")
    bash("echo 'Build successful'")

# Level 0 - Top level deployment
@dep(quality_check, build)
def deploy():
    """Deploy to target environment"""
    bash(f"echo 'Deploying {PROJECT}:{VERSION} to {ENVIRONMENT}'")
    bash("echo 'Deployment successful'")

# Additional isolated tasks for testing
def standalone_task():
    """Task with no dependencies"""
    bash("echo 'Standalone task executed'")

@dep(standalone_task)
def simple_chain():
    """Simple single-dependency chain"""
    bash("echo 'Simple chain task executed'")