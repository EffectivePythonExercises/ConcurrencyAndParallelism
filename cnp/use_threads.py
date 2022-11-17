import select
import socket
import time

from threading import Thread

from rich import print


class FactorizeThread(Thread):

    def __init__(self, number):
        super().__init__()
        self.number = number

    def run(self):
        self.factors = list(factorize(self.number))


def factorize(n: int):
    for i in range(1, n + 1):
        if n % i == 0:
            yield i


numbers = [2156432, 1214756, 151637, 1852285, 8949844, 9435465]


def test_vanilla_elapsed_factorize():

    start = time.time()

    for number in numbers:
        list(factorize(number))

    end = time.time()
    delta = end - start
    print(f'Time elapsed: {delta: .3f}')


def test_threaded_elapsed_factorize():

    start = time.time()

    threads = []
    for number in numbers:
        thread = FactorizeThread(number)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    end = time.time()
    delta = end - start
    print(f'Time elapsed: {delta: .3f}')


def slow_systemcall():
    select.select([socket.socket()], [], [], 1)


def call_slow_systemcall():
    start = time.time()

    for _ in range(10):
        slow_systemcall()

    end = time.time()
    delta = end - start
    print(f'Multiple `slow_systemcall`, Time elapsed: {delta: .3f}')
