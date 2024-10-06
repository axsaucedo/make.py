from make import sh, bash, _, dep

DOCKER_REPO = _('DOCKER_REPO')
DJANGO_IMAGE = _('DJANGO_IMAGE')
POSTGRES_IMAGE = _('POSTGRES_IMAGE')
VERSION = _('VERSION')
DEV_SUFFIX = _('DEV_SUFFIX')


def build_images():
    bash("docker build -f ./docker/Dockerfile ."
        f" -t {DOCKER_REPO}/{IMAGE}:{VERSION}-{DEV_SUFFIX}")


def push_images():
    sh.docker(f"push {DOCKER_REPO}/{IMAGE}:{VERSION}")


@dep(build_images, push_images)
def build_and_push():
    pass


