import asyncio
import random
from rich import print
from cnp.utils import timer
from cnp.conway.grid import (
    Grid, ColumnPrinter, count_neighbors, set_grid_random_cells_alive
)

ALIVE = '*'
EMPTY = '-'


async def game_logic(state, neighbors):
    # Blocing I/O Mock
    if int(random.random() * 1000 // 0.5) == 222:
        raise OSError('Get failed')
    await asyncio.sleep(.006)
    if (neighbors == 3 or (neighbors == 2 and state == ALIVE)):
        return ALIVE
    return EMPTY


async def step_cell(y, x, get, set):
    state = get(y, x)
    neighbors = count_neighbors(y, x, get)
    next_state = await game_logic(state, neighbors)
    set(y, x, next_state)


async def simulate(grid):
    next_grid = Grid(grid.height, grid.width)

    tasks = []
    for y in range(grid.height):
        for x in range(grid.width):
            task = step_cell(y, x, grid.get, next_grid.set)
            tasks.append(task)

    await asyncio.gather(*tasks)

    return next_grid


@timer
def test_column_printer_with_asyncio():
    columns = ColumnPrinter("Grids Columns")
    simulated_columns = ColumnPrinter("Simulated Grids Columns")

    for i in range(5):
        grid = Grid(15, 15)
        set_grid_random_cells_alive(grid, random.uniform(0.06, 0.8))
        columns.append(str(grid))
        grid = asyncio.run(simulate(grid))
        simulated_columns.append(str(grid))

    print(columns)
    print(simulated_columns)
