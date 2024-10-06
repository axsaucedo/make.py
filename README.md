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

def build_images():
    bash("docker build -f ./docker/Dockerfile ."
        f" -t {DOCKER_REPO}/{IMAGE}:{VERSION}")


def push_images():
    sh.docker(f"push {DOCKER_REPO}/{IMAGE}:{VERSION}")


@dep(build_images, push_images)
def build_and_push():
    pass

```

### Run commands

```bash

# Runs build_images
make.py

# Runs build and push cmds
make.py build_and_push

# Runs build and push and overrides push cmds
make.py build_and_push IMAGE="myimage"

```

### Equivallent makefile

```bash

IMAGE ?= $(IMAGE)
DOCKER_REPO ?= $(DOCKER_REPO)
VERSION ?= $(VERSION)

build_images:
    docker build -f ./docker/Dockerfile . \
        -t $(DOCKER_REPO)/$(IMAGE):$(VERSION)


push_images:
    docker push $(DOCKER_REPO)/$(IMAGE):$(VERSION)


build_and_push: build_images, push_images

```

