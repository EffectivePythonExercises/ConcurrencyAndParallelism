import asyncio
import collections
import os
import random
import string
import time
from io import BufferedReader
from tempfile import TemporaryDirectory
from threading import Lock, Thread
from typing import Callable

from rich import print


class NoNewData(Exception):
    ...


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


def run_threads(handles: list[BufferedReader], interval: int, output_path):
    with open(output_path, 'wb') as output:
        lock = Lock()

        def write(data: bytes):
            with lock:
                output.write(data)

        threads = []
        for handle in handles:
            args = (handle, interval, write)
            thread = Thread(target=tail_file, args=args)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()


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
            f'{expected_lines!r} == {found_lines!r}'


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

    run_threads(handles, 0.5, output_path)

    confirm_merge(input_paths, output_path)

    tmpdir.cleanup()
