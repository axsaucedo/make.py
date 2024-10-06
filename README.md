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
from make import sh, _, dep

DOCKER_REPO = _('DOCKER_REPO')
DJANGO_IMAGE = _('DJANGO_IMAGE')
POSTGRES_IMAGE = _('POSTGRES_IMAGE')
VERSION = _('VERSION')
DEV_SUFFIX = _('DEV_SUFFIX')


def build_images_local():
    sh("docker build -f ./docker/local/django/Dockerfile ."
              f" -t {DOCKER_REPO}/{DJANGO_IMAGE}:{VERSION}-{DEV_SUFFIX}")
    sh("docker build -f ./docker/local/django/Dockerfile ."
              f" -t {DOCKER_REPO}/{DJANGO_IMAGE}:{VERSION}-{DEV_SUFFIX}")


def push_images_local():
    sh.docker(f"push {DOCKER_REPO}/{DJANGO_IMAGE}:{VERSION}")
    sh.docker(f"push {DOCKER_REPO}/{_('POSTGRES_IMAGE')}:{VERSION}")


@dep(build_images_local, push_images_local)
def build_and_push():
    pass

```

