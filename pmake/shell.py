"""Shell execution for Python Makefile (pmake) using amoffat/sh

This module exposes the amoffat/sh library as the main shell interface.
All shell commands are executed through the powerful amoffat/sh library,
providing superior command handling, piping, and process management.
"""

import sh as _sh

# Expose amoffat/sh as the main sh object
sh = _sh
