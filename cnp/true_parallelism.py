"""
Item 64: Consider concurrent.futures for True Parallelism

Find out the difference between:
    multiprocessing.pool.ThreadPool
    concurrent.futures.ThreadPoolExecutor
"""


def gcd(pair):
    a, b = pair
    low = min(a, b)
    for i in range(low, 0, -1):
        if a % i == 0 and b % i == 0:
            return i
    assert False, 'Not reacheable'


import os
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor

from rich import print

CPU_COUNT = os.cpu_count()
print(f'{CPU_COUNT=}')

NUMBERS = [
    (1963309, 2265973), (2030677, 3814172),
    (1551645, 2229620), (2039045, 2020802),
    (1823712, 1924928), (2293129, 1020491),
    (1281238, 2273782), (3823812, 4237281),
    (3812741, 4729139), (1292391, 2123811),
    (1963309, 2265973), (2030677, 3814172),
    (1551645, 2229620), (2039045, 2020802),
    (1823712, 1924928), (2293129, 1020491),
    (1281238, 2273782), (3823812, 4237281),
    (3812741, 4729139), (1292391, 2123811),
    (1963309, 2265973), (2030677, 3814172),
    (1551645, 2229620), (2039045, 2020802),
    (1823712, 1924928), (2293129, 1020491),
    (1281238, 2273782), (3823812, 4237281),
    (3812741, 4729139), (1292391, 2123811),
    (1963309, 2265973), (2030677, 3814172),
    (1551645, 2229620), (2039045, 2020802),
    (1823712, 1924928), (2293129, 1020491),
    (1281238, 2273782), (3823812, 4237281),
    (3812741, 4729139), (1292391, 2123811),
]  # yapf: disable


def main():
    start = time.time()

    results = list(map(gcd, NUMBERS))
    end = time.time()
    delta = end - start
    print(f'{results=}')
    print(f'Took {delta:.3f} seconds')


def main_tpe():
    start = time.time()

    pool = ThreadPoolExecutor(max_workers=CPU_COUNT)
    results = list(pool.map(gcd, NUMBERS))

    end = time.time()
    delta = end - start
    print(f'{results=}')
    print(f'Took {delta:.3f} seconds')


def main_ppe():
    start = time.time()

    pool = ProcessPoolExecutor(max_workers=CPU_COUNT)
    results = list(pool.map(gcd, NUMBERS))

    end = time.time()
    delta = end - start
    print(f'{results=}')
    print(f'Took {delta:.3f} seconds')


if __name__ == "__main__":
    main()
    main_tpe()
    main_ppe()
