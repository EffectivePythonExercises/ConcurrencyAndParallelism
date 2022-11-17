import asyncio
import random
from typing import TypeVar, Callable, Any

from cnp.utils import timer

_T = TypeVar("_T")


def copy_signature(f: _T) -> Callable[[Any], _T]:
    return lambda x: x


class AsyncConnectionBase:

    def __init__(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        self.reader = reader
        self.writer = writer

    async def send(self, command):
        line = command + '\n'
        data = line.encode()
        self.writer.write(data)
        await self.writer.drain()

    async def receive(self):
        line = await self.reader.readline()
        if not line:
            raise EOFError('Connection closed')
        return line[:-1].decode()


class UnknownCommandError(Exception):
    ...


WARMER = 'Warmer'
COLDER = 'Colder'
UNSURE = 'Unsure'
CORRECT = 'Correct'


class AsyncSession(AsyncConnectionBase):

    @copy_signature(AsyncConnectionBase.__init__)
    def __init__(self, *args):
        super(AsyncSession, self).__init__(*args)
        self._clear_state(None, None)

    def _clear_state(self, lower, upper):
        self.lower = lower
        self.upper = upper
        self.secret = None
        self.guesses = []

    async def loop(self):
        while command := await self.receive():
            parts = command.split(' ')
            if parts[0] == 'PARAMS':
                self.set_params(parts)
            elif parts[0] == 'NUMBER':
                await self.send_number()
            elif parts[0] == 'REPORT':
                self.receive_report(parts)
            else:
                raise UnknownCommandError(command)

    def set_params(self, parts):
        assert len(parts) == 3
        lower = int(parts[1])
        upper = int(parts[2])
        self._clear_state(lower, upper)

    def next_guess(self):
        if self.secret is not None:
            return self.secret

        while True:
            guess = random.randint(self.lower, self.upper)
            if guess not in self.guesses:
                return guess

    async def send_number(self):
        guess = self.next_guess()
        self.guesses.append(guess)
        await self.send(format(guess))

    def receive_report(self, parts):
        assert len(parts) == 2
        decision = parts[1]

        last = self.guesses[-1]
        if decision == CORRECT:
            self.secret = last

        print(f'Server: {last} is {decision}')


import contextlib
import math


class AsyncClient(AsyncConnectionBase):

    @copy_signature(AsyncConnectionBase.__init__)
    def __init__(self, *args):
        super().__init__(*args)
        self._clear_state()

    def _clear_state(self):
        self.secret = None
        self.last_distance = None

    @contextlib.asynccontextmanager
    async def session(self, lower, upper, secret):
        print(
            f'Guess a number between {lower} and {upper}!'
            f' Shhhhh, it\'s {secret}'
        )
        self.secret = secret
        await self.send(f'PARAMS {lower} {upper}')
        try:
            yield
        finally:
            self._clear_state()
            await self.send('PARAMS 0 -1')

    async def request_numbers(self, count):
        for _ in range(count):
            await self.send('NUMBER')
            data = await self.receive()
            yield int(data)
            if self.last_distance == 0:
                return

    async def report_outcome(self, number):
        new_distance = math.fabs(number - self.secret)
        decision = UNSURE

        if new_distance == 0:
            decision = CORRECT
        elif self.last_distance is None:
            pass
        elif new_distance < self.last_distance:
            decision = WARMER
        elif new_distance > self.last_distance:
            decision = COLDER

        self.last_distance = new_distance
        await self.send(f'REPORT {decision}')
        return decision


async def handle_async_connection(reader, writer):
    session = AsyncSession(reader, writer)
    try:
        await session.loop()
    except EOFError:
        pass


async def run_async_server(host, port):
    server = await asyncio.start_server(handle_async_connection, host, port)
    async with server:
        await server.serve_forever()


async def run_async_client(host, port):
    # Wait for the server to listen before trying to connect
    

    streams = await asyncio.open_connection(host, port)
    reader, writer = streams
    client = AsyncClient(reader, writer)

    async with client.session(lower=1, upper=5, secret=3):
        results = [
            (x, await client.report_outcome(x))
            async for x in client.request_numbers(5)
        ]

    async with client.session(lower=1, upper=200, secret=103):
        async for number in client.request_numbers(5):
            outcome = await client.report_outcome(number)
            results.append((number, outcome))

    writer.close()
    await writer.wait_closed()

    return results


async def main_async():
    host = '127.0.0.1'
    port = 4321

    server = run_async_server(host, port)
    asyncio.create_task(server)

    await asyncio.sleep(0.1)

    results = await run_async_client(host, port)
    for number, outcome in results:
        print(f'Client: {number} is {outcome}')


@timer
def run_main_async():
    asyncio.run(main_async())


if __name__ == "__main__":
    run_main_async()
