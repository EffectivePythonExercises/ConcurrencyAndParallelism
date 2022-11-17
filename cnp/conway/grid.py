import time
import random
from rich import print
from cnp.utils import timer

ALIVE = '*'
EMPTY = '-'


class Grid:

    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.rows = []
        for _ in range(self.height):
            self.rows.append([EMPTY] * self.width)

    def get(self, y, x):
        return self.rows[y % self.height][x % self.width]

    def set(self, y, x, state):
        self.rows[y % self.height][x % self.width] = state

    def __str__(self):
        output = ''
        for row in self.rows:
            for cell in row:
                output += cell
            output += '\n'
        return output


def count_neighbors(y, x, get):
    n_ = get(y - 1, x + 0)  # North
    ne = get(y - 1, x + 1)  # Northeast
    e_ = get(y + 0, x + 1)  # East
    se = get(y + 1, x + 1)  # Southeast
    s_ = get(y + 1, x + 0)  # South
    sw = get(y + 1, x - 1)  # Southwest
    w_ = get(y + 0, x - 1)  # West
    nw = get(y - 1, x - 1)  # Northwest
    neighbor_states = [n_, ne, e_, se, s_, sw, w_, nw]
    count = 0

    for state in neighbor_states:
        if state == ALIVE:
            count += 1

    return count


def test_count_neighbors():
    alive = {(9, 5), (9, 6)}
    seen = set()

    def fake_get(y, x):
        position = (y, x)
        seen.add(position)
        return ALIVE if position in alive else EMPTY

    count = count_neighbors(10, 5, fake_get)
    assert count == 2

    expected_seen = {
        (9, 5), (9, 6), (10, 6), (11, 6), (11, 5), (11, 4), (10, 4), (9, 4)
    }
    assert seen == expected_seen


def game_logic(state, neighbors):
    # Blocing I/O Mock
    # if int(random.random() * 1000 // .5) == 222:
    #     raise OSError('Get failed')
    time.sleep(.009)
    if (neighbors == 3 or (neighbors == 2 and state == ALIVE)):
        return ALIVE
    return EMPTY


def test_game_logic():
    assert game_logic(ALIVE, 0) == EMPTY
    assert game_logic(ALIVE, 1) == EMPTY
    assert game_logic(ALIVE, 2) == ALIVE
    assert game_logic(ALIVE, 3) == ALIVE
    assert game_logic(ALIVE, 4) == EMPTY
    assert game_logic(EMPTY, 0) == EMPTY
    assert game_logic(EMPTY, 1) == EMPTY
    assert game_logic(EMPTY, 2) == EMPTY
    assert game_logic(EMPTY, 3) == ALIVE
    assert game_logic(EMPTY, 4) == EMPTY


def step_cell(y, x, get, set):
    state = get(y, x)
    neighbors = count_neighbors(y, x, get)
    next_state = game_logic(state, neighbors)
    set(y, x, next_state)


def test_step_cell():
    alive = {(10, 5), (9, 5), (9, 6)}
    new_state = None

    def fake_get(y, x):
        return ALIVE if (y, x) in alive else EMPTY

    def fake_set(y, x, state):
        nonlocal new_state
        new_state = state

    # Stay alive
    step_cell(10, 5, fake_get, fake_set)
    assert new_state == ALIVE

    # Stay dead
    alive.remove((10, 5))
    step_cell(10, 5, fake_get, fake_set)
    assert new_state == EMPTY

    # Regenerate
    alive.add((10, 6))
    step_cell(10, 5, fake_get, fake_set)
    assert new_state == ALIVE


def simulate(grid):
    next_grid = Grid(grid.height, grid.width)

    for y in range(grid.height):
        for x in range(grid.width):
            step_cell(y, x, grid.get, next_grid.set)
    return next_grid


class ColumnPrinter:

    def __init__(self, title):
        self.title = title
        self.columns = []

    def append(self, data):
        self.columns.append(data)

    def __str__(self):
        row_count = 1
        columns_delimiter = ' | '
        for data in self.columns:
            row_count = max(row_count, len(data.splitlines()) + 1)
        rows = [''] * row_count
        heading = self.title.center(
            len(data.splitlines()[0]) * len(self.columns) +
            len(columns_delimiter) * (len(self.columns) - 1),
            '='
        )
        rows[0] += '\n' + heading + '\n'
        for j in range(row_count):
            for i, data in enumerate(self.columns):
                line = data.splitlines()[max(0, j - 1)]
                if j == 0:
                    rows[j] += str(i).center(len(line), ' ')
                else:
                    rows[j] += line
                if (i + 1) < len(self.columns):
                    rows[j] += columns_delimiter

        return '\n'.join(rows)


def set_grid_random_cells_alive(grid: Grid, ratio: float):
    total_cells_count = grid.height * grid.width
    alive_cells_count = int(total_cells_count * ratio)
    print(f'{alive_cells_count} / {total_cells_count}')

    for _ in range(alive_cells_count):
        y = random.randrange(0, grid.height)
        x = random.randrange(0, grid.width)
        grid.set(y, x, ALIVE)

    print(grid)


@timer
def test_column_printer():
    columns = ColumnPrinter("Grids Columns")
    simulated_columns = ColumnPrinter("Simulated Grids Columns")

    for i in range(5):
        grid = Grid(15, 15)
        set_grid_random_cells_alive(grid, random.uniform(0.06, 0.8))
        columns.append(str(grid))
        grid = simulate(grid)
        simulated_columns.append(str(grid))

    print(columns)
    print(simulated_columns)


if __name__ == '__main__':
    grid = Grid(5, 6)
    grid.set(0, 3, ALIVE)
    grid.set(1, 4, ALIVE)
    grid.set(2, 2, ALIVE)
    grid.set(2, 3, ALIVE)
    grid.set(2, 4, ALIVE)
    print(grid)

    test_count_neighbors()
    test_game_logic()
    # test_step_cell()
    # test_column_printer()
