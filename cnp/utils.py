import time
from functools import wraps
from rich import print


def timer(func):

    @wraps(func)
    def inner(*args, **kwargs):
        print(f'Execute {func.__name__}'.center(70, "="))
        start = time.monotonic()
        result = func(*args, **kwargs)
        end = time.monotonic()
        delta = end - start
        print(f'Elapsed: {delta: .4f}')
        return result

    return inner