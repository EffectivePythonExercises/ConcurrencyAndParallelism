from concurrent.futures import ThreadPoolExecutor

import random
from rich import print
from cnp.utils import timer
from cnp.use_queue import ClosableQueue, StoppableWorker
from cnp.conway.lockinggrid import LockingGrid
from cnp.conway.grid import (
    ColumnPrinter,
    game_logic,
    step_cell,
    count_neighbors,
    set_grid_random_cells_alive
)


def simulate_pool(pool, grid):
    next_grid = LockingGrid(grid.height, grid.width)

    futures = []
    for y in range(grid.height):
        for x in range(grid.width):
            args = (y, x, grid.get, next_grid.set)
            future = pool.submit(step_cell, *args)
            futures.append(future)
    for future in futures:
        future.result()

    return next_grid


@timer
def test_column_printer_with_pool():
    columns = ColumnPrinter("Grids Columns with threading")
    simulated_columns = ColumnPrinter("Simulated Grids Columns with threading")

    with ThreadPoolExecutor(max_workers=20) as pool:
        for i in range(5):
            grid = LockingGrid(15, 15)
            set_grid_random_cells_alive(grid, random.uniform(0.06, 0.8))
            columns.append(str(grid))
            grid = simulate_pool(pool, grid)
            simulated_columns.append(str(grid))

    print(columns)
    print(simulated_columns)
