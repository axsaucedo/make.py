from make import sh, bash, _, dep

# Read from env
DOCKER_REPO = _('DOCKER_REPO')
IMAGE = _('IMAGE')
VERSION = _('VERSION', "0.0.1") # Default value


def build_images():
    bash("docker build -f ./docker/Dockerfile ."
        f" -t {DOCKER_REPO}/{IMAGE}:{VERSION}")


def push_images():
    sh.docker(f"push {DOCKER_REPO}/{IMAGE}:{VERSION}")


@dep(build_images, push_images)
def build_and_push():
    pass


