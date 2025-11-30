# Python Makefile (pmake)

Using Makefiles for project command orchestration is becoming more common.

However often writing logic in bash is a pain - pmake allows writing everything in Python using the powerful amoffat/sh library.

Note: Python Makefile (pmake) is not for building CLIs, just a simple way to run orchestration within your project.

## Overview

```bash
# Create a Makefile.py in your project directory (see guidance with pmake when no file exists)

# Run the default command from your Makefile.py
pmake

# Run specific command directly
pmake build_images
pmake status
pmake build_and_push

# Pass parameters and override environment variables
pmake build_images IMAGE=myapp VERSION=1.0.0
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
    # Use sh object - automatically inherits environment including venv
    sh.docker("build", "-f", "./docker/Dockerfile", ".",
              "-t", f"{DOCKER_REPO}/{IMAGE}:{VERSION}")

def push_images():
    # Use direct command imports - environment variables from _() automatically available
    docker("push", f"{DOCKER_REPO}/{IMAGE}:{VERSION}")

def status():
    # All commands automatically use your current shell environment
    git("status")
    echo(f"Build completed for {IMAGE} v{VERSION}!")

@dep(build_images, push_images)
def build_and_push():
    pass
```

### Run commands

```bash
# Runs the default command (first alphabetically: build_and_push in this case)
pmake

# Run specific commands directly
pmake build_images
pmake push_images
pmake status

# Runs build_and_push (with dependencies: build_images, push_images)
pmake build_and_push

# Run with parameter overrides
pmake build_and_push IMAGE="myimage" VERSION="2.0.0"

# See all available commands with descriptions and dependencies
pmake --help
```

## Getting Started

### Creating Your First Makefile.py

When you run `pmake` in a directory without a Makefile.py, it will show helpful guidance. Here's a simple starter example:

```python
from pmake import sh, _, dep
from pmake import echo, python, pip

def hello():
    '''Say hello - this will be your default command'''
    echo('Hello from pmake!')

def test():
    '''Run tests'''
    python('-m', 'pytest')

@dep(test)
def deploy():
    '''Deploy after running tests'''
    echo('Deploying application...')
```

Then run:
- `pmake` - Runs default command (hello in this case)
- `pmake test` - Runs test command
- `pmake deploy` - Runs test, then deploy (due to @dep dependency)
- `pmake --help` - Shows all available commands with descriptions and dependencies

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

### Powerful Shell Execution with Automatic Environment Inheritance

pmake uses the amoffat/sh library under the hood with enhanced environment management:
- **Automatic virtual environment inheritance**: Commands use your current venv
- **Environment variable tracking**: Variables accessed via `_()` are automatically available to shell commands
- **Parameter override inheritance**: CLI `PARAM=value` overrides are passed to all shell commands
- Better error handling and superior command composition
- Rich command objects with piping support

**No more `_env=os.environ` needed!** All pmake shell commands automatically include:
- Your current shell environment (including PATH, VIRTUAL_ENV, etc.)
- Any environment variables accessed through `_()` calls
- Any parameter overrides from the command line

### Automatic Environment Inheritance

All shell commands automatically inherit your environment:

```python
from pmake import sh, python, pip, _

# Environment variables accessed via _() are tracked
VENV_PATH = _('VIRTUAL_ENV')
PROJECT_NAME = _('PROJECT_NAME', 'myproject')

def setup_venv():
    # python command automatically uses current virtual environment
    python("-m", "pip", "install", "-e", ".")

    # No need for _env=os.environ - it's automatic!
    pip("install", "pytest", "black", "mypy")

def test():
    # All environment variables from _() calls are available
    python("-c", f"print('Testing {PROJECT_NAME}')")
```

### Both Syntaxes Supported

```python
from pmake import sh, docker

# Option 1: Direct imports (automatically inherit environment)
docker("build", "-t", "myapp", ".")

# Option 2: Through sh object (automatically inherit environment)
sh.docker("build", "-t", "myapp", ".")

# Complex shell operations (with full environment)
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