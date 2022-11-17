import random
from rich import print
from cnp.utils import timer
from cnp.use_queue import ClosableQueue, StoppableWorker
from cnp.conway.grid import (
    Grid,
    ColumnPrinter,
    game_logic,
    count_neighbors,
    set_grid_random_cells_alive
)


def game_logic_thread(item):
    y, x, state, neighbors = item
    try:
        next_state = game_logic(state, neighbors)
    except Exception as e:
        next_state = e
    return (y, x, next_state)


class SimulationError(Exception):
    ...


def simulate_pipeline(grid, in_queue, out_queue):
    for y in range(grid.height):
        for x in range(grid.width):
            state = grid.get(y, x)
            neighbors = count_neighbors(y, x, grid.get)
            in_queue.put((y, x, state, neighbors))

    in_queue.join()
    out_queue.close()

    next_grid = Grid(grid.height, grid.width)
    for item in out_queue:
        y, x, next_state = item
        if isinstance(next_state, Exception):
            raise SimulationError(y, x) from next_state
        next_grid.set(y, x, next_state)

    return next_grid


@timer
def test_column_printer_with_queue():
    columns = ColumnPrinter("Grids Columns with threading")
    simulated_columns = ColumnPrinter("Simulated Grids Columns with threading")

    in_queue = ClosableQueue()
    out_queue = ClosableQueue()

    threads = []
    for _ in range(5):
        thread = StoppableWorker(game_logic_thread, in_queue, out_queue)
        thread.start()
        threads.append(thread)

    for i in range(5):
        grid = Grid(15, 15)
        set_grid_random_cells_alive(grid, random.uniform(0.06, 0.8))
        columns.append(str(grid))
        grid = simulate_pipeline(grid, in_queue, out_queue)
        simulated_columns.append(str(grid))

    print(columns)
    print(simulated_columns)

    for thread in threads:
        in_queue.close()
    for thread in threads:
        thread.join()
