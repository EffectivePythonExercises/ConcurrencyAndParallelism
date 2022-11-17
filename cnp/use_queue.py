import time
from collections import deque
from queue import Queue
from threading import Lock, Thread

from rich import print
from cnp.utils import timer


class MyQueue:

    def __init__(self):
        self.items = deque()
        self.lock = Lock()

    def put(self, item):
        with self.lock:
            self.items.append(item)

    def get(self):
        with self.lock:
            return self.items.popleft()


class ClosableQueue(Queue):
    SENTINEL = object()

    def close(self):
        self.put(self.SENTINEL)

    def __iter__(self):
        while True:
            item = self.get()
            try:
                if item is self.SENTINEL:
                    return
                    # raise StopIteration
                yield item
            finally:
                self.task_done()


class Worker(Thread):

    def __init__(self, func, in_queue, out_queue):
        super().__init__()
        self.func = func
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.polled_count = 0
        self.work_done = 0

    def run(self):
        while True:
            self.polled_count += 1
            try:
                item = self.in_queue.get()
            except IndexError:
                time.sleep(.01)
            else:
                result = self.func(item)
                self.out_queue.put(result)
                self.work_done += 1


class StoppableWorker(Thread):

    def __init__(self, func, in_queue, out_queue):
        super().__init__()
        self.func = func
        self.in_queue = in_queue
        self.out_queue = out_queue

    def run(self):
        for item in self.in_queue:
            result = self.func(item)
            self.out_queue.put(result)


def download(item):
    # print(f'____downloading {item} ... ')
    time.sleep(.003)


def resize(item):
    # print(f'____resizing {item} ... ')
    time.sleep(.001)


def upload(item):
    # print(f'____uploading {item} ... ')
    time.sleep(.005)


@timer
def commence_task_flow():
    download_queue = MyQueue()
    resize_queue = MyQueue()
    upload_queue = MyQueue()
    done_queue = MyQueue()

    threads = [
        Worker(download, download_queue, resize_queue),
        Worker(resize, resize_queue, upload_queue),
        Worker(upload, upload_queue, done_queue),
    ]

    for thread in threads:
        thread.start()

    for _ in range(1000):
        download_queue.put(object())

    while len(done_queue.items) < 1000:
        print('Waiting for processing...')
        time.sleep(5)

    processed = len(done_queue.items)
    polled = sum(t.polled_count for t in threads)
    print(f'Processed {processed} items after polling {polled} times')


@timer
def commence_task_flow_with_queue():
    download_queue = ClosableQueue()
    resize_queue = ClosableQueue()
    upload_queue = ClosableQueue()
    done_queue = ClosableQueue()

    threads = [
        StoppableWorker(download, download_queue, resize_queue),
        StoppableWorker(resize, resize_queue, upload_queue),
        StoppableWorker(upload, upload_queue, done_queue),
    ]

    for thread in threads:
        thread.start()

    for _ in range(1000):
        download_queue.put(object())

    download_queue.close()
    download_queue.join()
    resize_queue.close()
    resize_queue.join()
    upload_queue.close()
    upload_queue.join()

    print(f'{done_queue.qsize()} items finished')

    for thread in threads:
        thread.join()


def start_threads(count, *args):
    threads = [StoppableWorker(*args) for _ in range(count)]
    for thread in threads:
        thread.start()
    return threads


def stop_threads(closable_queue, threads):
    for _ in threads:
        closable_queue.close()
    closable_queue.join()
    for thread in threads:
        thread.join()


@timer
def commence_task_flow_with_queue_cleaner():
    download_queue = ClosableQueue()
    resize_queue = ClosableQueue()
    upload_queue = ClosableQueue()
    done_queue = ClosableQueue()

    download_thread = start_threads(3, download, download_queue, resize_queue)
    resize_thread = start_threads(4, resize, resize_queue, upload_queue)
    upload_thread = start_threads(5, upload, upload_queue, done_queue)

    for _ in range(1000):
        download_queue.put(object())

    stop_threads(download_queue, download_thread)
    stop_threads(resize_queue, resize_thread)
    stop_threads(upload_queue, upload_thread)

    print(f'{done_queue.qsize()} items finished')
