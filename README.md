# Make.py

```python

# Start project
make.py init

# Run first command
make.py

# Run specific command
make.py <cmd>

```

## Example Makefile.py:

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

