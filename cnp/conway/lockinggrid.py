import io
import random
import contextlib
from threading import Lock, Thread
from rich import print
from cnp.utils import timer
from cnp.conway.grid import (
    Grid, ColumnPrinter, step_cell, set_grid_random_cells_alive
)


class LockingGrid(Grid):

    def __init__(self, height, width):
        super().__init__(height, width)
        self.lock = Lock()

    def get(self, y, x):
        with self.lock:
            return super().get(y, x)

    def set(self, y, x, state):
        with self.lock:
            return super().set(y, x, state)

    def __str__(self):
        with self.lock:
            return super().__str__()


def simulate_threading(grid):
    next_grid = LockingGrid(grid.height, grid.width)

    threads = []
    for y in range(grid.height):
        for x in range(grid.width):
            args = (y, x, grid.get, next_grid.set)
            thread = Thread(target=step_cell, args=args)
            thread.start()
            threads.append(thread)
    print(f'Thread count: {len(threads)}')
    for thread in threads:
        thread.join()

    return next_grid


def simulate_threading_with_redirection(grid):
    next_grid = LockingGrid(grid.height, grid.width)

    threads = []
    fake_stderr = io.StringIO()
    with contextlib.redirect_stderr(fake_stderr):
        for y in range(grid.height):
            for x in range(grid.width):
                args = (y, x, grid.get, next_grid.set)
                thread = Thread(target=step_cell, args=args)
                thread.start()
                threads.append(thread)
        print(f'Thread count: {len(threads)}')
        for thread in threads:
            thread.join()
    print(fake_stderr.getvalue())

    return next_grid


@timer
def test_column_printer_with_threading(err_redirection=False):
    columns = ColumnPrinter("Grids Columns with threading")
    simulated_columns = ColumnPrinter("Simulated Grids Columns with threading")

    if err_redirection:
        simulate_function = simulate_threading_with_redirection
    else:
        simulate_function = simulate_threading
    for i in range(5):
        grid = Grid(15, 15)
        set_grid_random_cells_alive(grid, random.uniform(0.06, 0.8))
        columns.append(str(grid))
        grid = simulate_function(grid)
        simulated_columns.append(str(grid))

    print(columns)
    print(simulated_columns)
