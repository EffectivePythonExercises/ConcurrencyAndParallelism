import random
from rich import print
from cnp.utils import timer
from cnp.use_queue import ClosableQueue, StoppableWorker
from cnp.conway.lockinggrid import LockingGrid
from cnp.conway.grid import (
    ColumnPrinter, game_logic, count_neighbors, set_grid_random_cells_alive
)


def count_neighbors_thread(item):
    y, x, state, get = item
    try:
        neighbors = count_neighbors(y, x, get)
    except Exception as e:
        neighbors = e
    return (y, x, state, neighbors)


def game_logic_thread(item):
    y, x, state, neighbors = item
    if isinstance(neighbors, Exception):
        next_state = neighbors
    else:
        try:
            next_state = game_logic(state, neighbors)
        except Exception as e:
            next_state = e
    return (y, x, next_state)


class SimulationError(Exception):
    ...


def simulate_phased_pipeline(grid, in_queue, logic_queue, out_queue):
    for y in range(grid.height):
        for x in range(grid.width):
            state = grid.get(y, x)
            item = (y, x, state, grid.get)
            in_queue.put(item)

    in_queue.join()
    logic_queue.join()
    out_queue.close()

    next_grid = LockingGrid(grid.height, grid.width)
    for item in out_queue:
        y, x, next_state = item
        if isinstance(next_state, Exception):
            raise SimulationError(y, x) from next_state
        next_grid.set(y, x, next_state)

    return next_grid


@timer
def test_column_printer_with_phased_pipeline():
    columns = ColumnPrinter("Grids Columns with threading")
    simulated_columns = ColumnPrinter("Simulated Grids Columns with threading")

    in_queue = ClosableQueue()
    logic_queue = ClosableQueue()
    out_queue = ClosableQueue()

    threads = []
    for _ in range(5):
        thread = StoppableWorker(count_neighbors_thread, in_queue, logic_queue)
        thread.start()
        threads.append(thread)

    for _ in range(5):
        thread = StoppableWorker(game_logic_thread, logic_queue, out_queue)
        thread.start()
        threads.append(thread)

    for i in range(5):
        grid = LockingGrid(15, 15)
        set_grid_random_cells_alive(grid, random.uniform(0.06, 0.8))
        columns.append(str(grid))
        grid = simulate_phased_pipeline(grid, in_queue, logic_queue, out_queue)
        simulated_columns.append(str(grid))

    print(columns)
    print(simulated_columns)

    for thread in threads:
        in_queue.close()
    for thread in threads:
        logic_queue.close()
    for thread in threads:
        thread.join()
