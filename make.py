import sh
from sh.contrib import bash


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

