import select
import socket
import time

from threading import Thread, Lock

from rich import print

from cnp.utils import timer


class Counter:

    def __init__(self):
        self.count = 0

    def increment(self, offset):
        self.count += offset


class LockingCounter:

    def __init__(self):
        self.lock = Lock()
        self.count = 0

    def increment(self, offset):
        with self.lock:
            self.count += offset


def worker(sensor_index, how_many, counter):
    for _ in range(how_many):
        # Read from the sensor
        ...
        counter.increment(1)


@timer
def run_thread_counter():
    how_many = 10**5
    counter = Counter()

    threads = []
    for i in range(5):
        thread = Thread(target=worker, args=(i, how_many, counter))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    expected = how_many * 5
    found = counter.count
    print(f'Counter should be {expected}, got {found}')


@timer
def run_thread_locking_counter():
    how_many = 10**5
    counter = LockingCounter()

    threads = []
    for i in range(5):
        thread = Thread(target=worker, args=(i, how_many, counter))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    expected = how_many * 5
    found = counter.count
    print(f'LockingCounter should be {expected}, got {found}')
