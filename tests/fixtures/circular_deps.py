"""Circular dependency test fixture

This makefile intentionally creates circular dependencies to test error detection.

Circular patterns tested:
1. Simple cycle: task_a → task_b → task_a
2. Complex cycle: task_x → task_y → task_z → task_x
3. Self-reference: self_ref → self_ref
"""

from make import sh, bash, _, dep

# Simple circular dependency: A → B → A
def task_b():
    """Task B that depends on A (creating circular dependency)"""
    bash("echo 'Task B executed'")

@dep(task_b)
def task_a():
    """Task A that depends on B (creating circular dependency)"""
    bash("echo 'Task A executed'")

# This creates the circular dependency: task_a depends on task_b
# But task_b is redefined below to depend on task_a
@dep(task_a)
def task_b():
    """Task B redefined to depend on A (completing the cycle)"""
    bash("echo 'Task B executed (circular)'")

# Complex circular dependency: X → Y → Z → X
def task_y():
    """Task Y (part of complex cycle)"""
    bash("echo 'Task Y executed'")

def task_z():
    """Task Z (part of complex cycle)"""
    bash("echo 'Task Z executed'")

@dep(task_y)
def task_x():
    """Task X (part of complex cycle)"""
    bash("echo 'Task X executed'")

# Complete the complex cycle
@dep(task_z)
def task_y():
    """Task Y redefined to depend on Z"""
    bash("echo 'Task Y executed (circular)'")

@dep(task_x)
def task_z():
    """Task Z redefined to depend on X"""
    bash("echo 'Task Z executed (circular)'")

# Self-referencing task (should be detected as circular)
@dep(lambda: self_ref())
def self_ref():
    """Task that depends on itself"""
    bash("echo 'Self-referencing task'")

# Valid non-circular tasks for control testing
def valid_start():
    """Valid task with no dependencies"""
    bash("echo 'Valid start task'")

@dep(valid_start)
def valid_end():
    """Valid task with proper dependency"""
    bash("echo 'Valid end task'")