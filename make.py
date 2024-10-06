import sh


# Adding callable to bash -c
setattr(sh.__class__, "__call__", lambda self, cmd, *args, **kwargs: sh.bash("-c", cmd, *args, **kwargs))


def dep(*func_args):
    def decorator(func):
        def inner():
            for func_arg in func_args:
                func_arg()
            func()
        return inner
    return decorator


class _:
    def __init__(self, _):
        pass

    @staticmethod
    def docker(str): pass

