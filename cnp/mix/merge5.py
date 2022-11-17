"""
Item 63: Avoid Blocking the asyncio Event Loop to Maximize Responsiveness

"""

import asyncio
import collections
import os
import random
import string
import time
from io import BufferedReader
from tempfile import TemporaryDirectory
from threading import Thread
from typing import Callable

from rich import print


class NoNewData(Exception):
    ...


async def slow_coroutine():
    time.sleep(.5)  # Simulating slow IO


asyncio.run(slow_coroutine(), debug=True)


def readline(handle: BufferedReader):
    offset = handle.tell()
    handle.seek(0, 2)
    length = handle.tell()

    if length == offset:
        raise NoNewData

    handle.seek(offset, 0)
    return handle.readline()


# Asyncified
async def tail_async(
    handle: BufferedReader, interval: int, write_func: Callable[[bytes], None]
):
    loop = asyncio.get_event_loop()

    while not handle.closed:
        try:
            line: bytes = await loop.run_in_executor(None, readline, handle)
        except NoNewData:
            await asyncio.sleep(interval)
        else:
            await write_func(line)


def tail_file(
    handle: BufferedReader, interval: int, write_func: Callable[[bytes], None]
):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def write_async(data: bytes):
        write_func(data)

    coro = tail_async(handle, interval, write_async)
    loop.run_until_complete(coro)


class WriteThread(Thread):

    def __init__(self, output_path):
        super().__init__()
        self.output_path = output_path
        self.output = None
        self.loop = asyncio.new_event_loop()

    def run(self):
        asyncio.set_event_loop(self.loop)
        with open(self.output_path, 'wb') as self.output:
            self.loop.run_forever()

        self.loop.run_until_complete(asyncio.sleep(0))

    async def real_write(self, data):
        self.output.write(data)

    async def write(self, data):
        coro = self.real_write(data)
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        await asyncio.wrap_future(future)

    async def real_stop(self):
        self.loop.stop()

    async def stop(self):
        coro = self.real_stop()
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        await asyncio.wrap_future(future)

    async def __aenter__(self):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.start)
        return self

    async def __aexit__(self, *_):
        await self.stop()


async def run_fully_async(
    handles: list[BufferedReader], interval: int, output_path
):
    async with WriteThread(output_path) as output:
        tasks = []
        for handle in handles:
            coro = tail_async(handle, interval, output.write)
            task = asyncio.create_task(coro)
            tasks.append(task)

        await asyncio.gather(*tasks)


def confirm_merge(input_paths: list[str], output_path: str):
    found = collections.defaultdict(list)
    with open(output_path, 'rb') as f:
        for line in f:
            for path in input_paths:
                if line.find(path.encode()) == 0:
                    found[path].append(line)

    expected = collections.defaultdict(list)
    for path in input_paths:
        with open(path, 'rb') as f:
            expected[path].extend(f.readlines())

    for key, expected_lines in expected.items():
        found_lines = found[key]
        assert expected_lines == found_lines, \
            f'{expected_lines!r} == \n{found_lines!r}'


def setup(
) -> tuple[TemporaryDirectory[str], list[str], list[BufferedReader], str]:
    tmpdir = TemporaryDirectory()
    input_paths = start_write_threads(tmpdir.name, 5)

    handles = []
    for path in input_paths:
        handle = open(path, 'rb')
        handles.append(handle)

    Thread(target=close_all, args=(handles, )).start()

    output_path = os.path.join(tmpdir.name, 'merged')

    return tmpdir, input_paths, handles, output_path


def close_all(handles: list[BufferedReader]):
    time.sleep(3)
    for handle in handles:
        handle.close()


def start_write_threads(directory: str, file_count: int):
    paths = []
    for i in range(file_count):
        path = os.path.join(directory, str(i))
        with open(path, 'w'):
            # Make sure the file at this path will exist when
            # the reading thread tries to poll it.
            pass
        paths.append(path)
        args = (path, 10, 0.5)
        thread = Thread(target=write_random_data, args=args)
        thread.start()

    return paths


def write_random_data(path: str, write_count: int, interval: int):
    with open(path, 'wb') as f:
        for i in range(write_count):
            time.sleep(random.random() * interval)
            letters = random.choices(string.ascii_letters, k=10)
            data = f'{path}-{i:02}-{"".join(letters)}\n'
            print(data.strip())
            f.write(data.encode())
            f.flush()


if __name__ == "__main__":
    input_paths = ...
    handles = ...
    output_path = ...

    tmpdir, input_paths, handles, output_path = setup()

    asyncio.run(run_fully_async(handles, 0.5, output_path))

    confirm_merge(input_paths, output_path)

    tmpdir.cleanup()
