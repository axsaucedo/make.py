# Make.py

Using Makefiles for project command orchestration is becoming more common.

However often writing logic in bash is a pain - make.py allows writing everything in python.

Note: Make.py is not for building CLIs, just a simple way to run orchestration within your project.

## Overview

```python

# Start project within directory (creates Makefile.py)
make.py init

# Run the first command found in your Makefile.py
make.py

# Run specific command
make.py <cmd>

# Passes parameters and overrides any set
make.py <cmd> PARAM=Value

```

# Example:

### Content in Makefile.py

```python
from make import sh, _, bash, dep

DOCKER_REPO = _('DOCKER_REPO')
IMAGE = _('IMAGE')
VERSION = _('VERSION')
DEV_SUFFIX = _('DEV_SUFFIX')

def build_images_local():
    bash("docker build -f ./docker/Dockerfile ."
        f" -t {DOCKER_REPO}/{IMAGE}:{VERSION}-{DEV_SUFFIX}")


def push_images_local():
    sh.docker(f"push {DOCKER_REPO}/{IMAGE}:{VERSION}")


@dep(build_images_local, push_images_local)
def build_and_push():
    pass

```

### Run commands

```bash

# Runs build_images_local
make.py

# Runs build and push cmds
make.py build_and_push

# Runs build and push and overrides push cmds
make.py build_and_push IMAGE="myimage"

