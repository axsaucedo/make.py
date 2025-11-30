"""Wide dependency tree test fixture

Tests a makefile with wide dependency trees where single tasks depend on many others.
Also tests multiple independent chains and convergent dependencies.

Dependency patterns:
- Wide fan-out: setup_all → [setup_a, setup_b, setup_c, setup_d]
- Convergent: final → [process_a, process_b], both processes depend on setup_all
- Independent chains: chain1_start → chain1_end, chain2_start → chain2_end
"""

from pmake import sh, bash, _, dep

# Environment variables
WORKERS = _('WORKERS', '4')
CONFIG = _('CONFIG', 'default')

# Wide fan-out pattern - single task with many dependencies
def setup_a():
    """Setup component A"""
    bash("echo 'Setting up component A'")

def setup_b():
    """Setup component B"""
    bash("echo 'Setting up component B'")

def setup_c():
    """Setup component C"""
    bash("echo 'Setting up component C'")

def setup_d():
    """Setup component D"""
    bash("echo 'Setting up component D'")

@dep(setup_a, setup_b, setup_c, setup_d)
def setup_all():
    """Initialize all components"""
    bash(f"echo 'All components initialized with {WORKERS} workers'")

# Convergent pattern - multiple paths to same dependencies
@dep(setup_all)
def process_a():
    """Process data stream A"""
    bash("echo 'Processing data stream A'")

@dep(setup_all)
def process_b():
    """Process data stream B"""
    bash("echo 'Processing data stream B'")

@dep(process_a, process_b)
def final():
    """Final processing step"""
    bash("echo 'Final processing complete'")

# Independent chains for testing isolation
def chain1_start():
    """Start of independent chain 1"""
    bash("echo 'Chain 1 started'")

@dep(chain1_start)
def chain1_end():
    """End of independent chain 1"""
    bash("echo 'Chain 1 completed'")

def chain2_start():
    """Start of independent chain 2"""
    bash("echo 'Chain 2 started'")

@dep(chain2_start)
def chain2_end():
    """End of independent chain 2"""
    bash("echo 'Chain 2 completed'")

# Complex mixed dependencies
@dep(setup_a, chain1_end)
def mixed_deps():
    """Task with dependencies from different chains"""
    bash("echo 'Mixed dependencies task executed'")

# Task that uses sh proxy instead of bash
@dep(setup_c)
def sh_proxy_test():
    """Test sh proxy functionality"""
    sh.echo("Testing sh proxy with echo command")
    sh.echo(f"Config: {CONFIG}")