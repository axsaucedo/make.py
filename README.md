# Python Makefile (pmake)

Using Makefiles for project command orchestration is becoming more common.

However often writing logic in bash is a pain - pmake allows writing everything in Python using the powerful amoffat/sh library.

Note: Python Makefile (pmake) is not for building CLIs, just a simple way to run orchestration within your project.

## Overview

```bash
# Start project within directory (creates Makefile.py)
pmake init

# Run the first command found in your Makefile.py
pmake

# Run specific command
pmake <cmd>

# Passes parameters and overrides any set
pmake <cmd> PARAM=Value
```

# Example:

### Content in Makefile.py

```python
from pmake import sh, _, dep
from pmake import docker, git, echo  # Direct command imports

# Read from env
DOCKER_REPO = _('DOCKER_REPO')
IMAGE = _('IMAGE')
VERSION = _('VERSION', "0.0.1")  # Default value

def build_images():
    # Option 1: Use sh object (amoffat/sh)
    sh.docker("build", "-f", "./docker/Dockerfile", ".",
              "-t", f"{DOCKER_REPO}/{IMAGE}:{VERSION}")

def push_images():
    # Option 2: Use direct command imports
    docker("push", f"{DOCKER_REPO}/{IMAGE}:{VERSION}")

def status():
    # Direct command imports work for any command
    git("status")
    echo("Build process completed!")

@dep(build_images, push_images)
def build_and_push():
    pass
```

### Run commands

```bash
# Runs build_images
pmake

# Runs build and push cmds
pmake build_and_push

# Runs build and push with parameter override
pmake build_and_push IMAGE="myimage"
```

## Features

### Universal Command Imports

Import any shell command directly from pmake:

```python
from pmake import docker, git, echo, ls, grep, curl, wget, find
# Equivalent to: from sh import docker, git, echo, ls, grep, curl, wget, find

# Use them directly
docker("build", "-t", "myapp", ".")
git("commit", "-m", "Update")
echo("Hello World")
```

### Powerful Shell Execution

pmake uses the amoffat/sh library under the hood, providing:
- Better error handling
- Superior command composition
- Automatic environment variable inheritance
- Rich command objects with piping support

### Both Syntaxes Supported

```python
from pmake import sh, docker

# Option 1: Direct imports
docker("build", "-t", "myapp", ".")

# Option 2: Through sh object
sh.docker("build", "-t", "myapp", ".")

# Complex shell operations
sh.bash("-c", "docker build . | grep 'Successfully built'")
```

### Equivalent makefile

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

## Migration from bash()

The old `bash()` function has been removed in favor of direct command usage:

```python
# OLD (removed)
bash("echo hello")
bash("docker build -t myapp .")

# NEW - Direct imports
from pmake import echo, docker
echo("hello")
docker("build", "-t", "myapp", ".")

# NEW - sh object
from pmake import sh
sh.echo("hello")
sh.docker("build", "-t", "myapp", ".")
```