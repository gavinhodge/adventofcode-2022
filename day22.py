import re
from typing import Literal, NamedTuple, NewType
from base import BaseDay


X = NewType('X', int)
Y = NewType('Y', int)


class Coord(NamedTuple):
    x: X
    y: Y


class Grid:
    def __init__(self, coords: dict[Coord, bool]):
        self.coords: dict[Coord, bool] = coords  # True = empty, False = blocked

        self.max_x = max(coord.x for coord in coords)
        self.max_y = max(coord.y for coord in coords)

        # For each y value, the min/max x
        self.y_bounds: list[list[X]] = [[X(1000000), X(0)] for _ in range(self.max_y + 2)]

        # For each x value, the min/max y
        self.x_bounds: list[list[Y]] = [[Y(1000000), Y(0)] for _ in range(self.max_x + 2)]

        for coord in self.coords:
            if coord.x < self.y_bounds[coord.y][0]:
                self.y_bounds[coord.y][0] = coord.x
            if coord.x > self.y_bounds[coord.y][1]:
                self.y_bounds[coord.y][1] = coord.x
            if coord.y < self.x_bounds[coord.x][0]:
                self.x_bounds[coord.x][0] = coord.y
            if coord.y > self.x_bounds[coord.x][1]:
                self.x_bounds[coord.x][1] = coord.y


class Turtle:
    dir_velo = {
        'r': [X(1), Y(0)],
        'l': [X(-1), Y(0)],
        'u': [X(0), Y(-1)],
        'd': [X(0), Y(1)],
    }
    dir_rotations = 'urdl'  # for turning right

    def __init__(self, grid: Grid, start_pos: Coord, start_dir = 'r'):
        self.grid = grid
        self.pos = start_pos
        self.dir = start_dir
        self.velo = self.dir_velo[start_dir]

    def rotate(self, left: bool):
        n = -1 if left else 1
        self.dir = self.dir_rotations[(self.dir_rotations.index(self.dir) + n) % 4]
        self.velo = self.dir_velo[self.dir]

    def move_n(self, distance: int):
        for _ in range(distance):
            dx, dy = self.velo
            peek = Coord(self.pos.x + dx, self.pos.y + dy)
            new_facing = self.dir

            if peek not in self.grid.coords:
                peek, new_facing = self.resolve_wrap(peek, dx, dy)

            value = self.grid.coords.get(peek)

            if value == True:
                self.pos = peek
                self.dir = new_facing
                self.velo = self.dir_velo[new_facing]
                continue

            if value == False:
                # Blocked, stop
                return

    def resolve_wrap(self, peek: Coord, dx: int, dy: int) -> tuple[Coord, str]:
        # If outside the map, need to wrap
        if dx and peek.x < self.grid.y_bounds[peek.y][0]:
            peek = Coord(self.grid.y_bounds[peek.y][1], peek.y)
        elif dx and peek.x > self.grid.y_bounds[peek.y][1]:
            peek = Coord(self.grid.y_bounds[peek.y][0], peek.y)
        elif dy and peek.y < self.grid.x_bounds[peek.x][0]:
            peek = Coord(peek.x, self.grid.x_bounds[peek.x][1])
        elif dy and peek.y > self.grid.x_bounds[peek.x][1]:
            peek = Coord(peek.x, self.grid.x_bounds[peek.x][0])

        return peek, self.dir

class Turtle3D(Turtle):

    def resolve_wrap(self, peek: Coord, dx: int, dy: int) -> tuple[Coord, str]:
        if self.grid.max_x < 150:
            raise ValueError("Only implemented for the full data shape")

        if dy and 51 <= peek.x <= 100 and peek.y == 0:  # Top of front
            coord = Coord(X(1), Y(peek.x + 100))
            facing = 'r'
        elif dx and 1 <= peek.y <=  50 and peek.x == 50:  # Left of front
            coord = Coord(X(1), Y(151 - peek.y))
            facing = 'r'
        elif dy and 101 <= peek.x <= 150 and peek.y == 0:  # Top of right
            coord = Coord(X(peek.x - 100), Y(200))
            facing = 'u'
        elif dx and 1 <= peek.y <= 50 and peek.x == 151:  # Right of right
            coord = Coord(X(100), Y(151 - peek.y))
            facing = 'l'
        elif dy and 101 <= peek.x <= 150 and peek.y == 51:  # Down of right
            coord = Coord(X(100), Y(peek.x - 50))
            facing = 'l'
        elif dx and 51 <= peek.y <= 100 and peek.x == 50:  # Left of bottom
            coord = Coord(X(peek.y - 50), Y(101))
            facing = 'd'
        elif dx and 51 <= peek.y <= 100 and peek.x == 101:  # Right of bottom
            coord = Coord(X(peek.y + 50), Y(50))
            facing = 'u'
        elif dx and 101 <= peek.y <= 150 and peek.x == 101:  # Right of back
            coord = Coord(X(150), Y(151 - peek.y))
            facing = 'l'
        elif dy and 51 <= peek.x <= 100 and peek.y == 151:  # Below back
            coord = Coord(X(50), Y(peek.x + 100))
            facing = 'l'
        elif dx and 151 <= peek.y <= 200 and peek.x == 51:  # Right of top
            coord = Coord(X(peek.y - 100), Y(150))
            facing = 'u'
        elif dy and 1 <= peek.x <= 50 and peek.y == 201:  # Bottom of top
            coord = Coord(X(peek.x + 100), Y(1))
            facing = 'd'
        elif dx and 151 <= peek.y <= 200 and peek.x == 0:  # Left of top
            coord = Coord(X(peek.y - 100), Y(1))
            facing = 'd'
        elif dx and 101 <= peek.y <= 150 and peek.x == 0:  # Left of left
            coord = Coord(X(51), Y(151 - peek.y))
            facing = 'r'
        elif dy and 1 <= peek.x <= 50 and peek.y == 100:  # Top of left
            coord = Coord(X(51), Y(peek.x + 50))
            facing = 'r'
        else:
            raise ValueError(f"No rule to handle this edge. ({peek=}, {dx=}, {dy=})")

        assert coord in self.grid.coords
        return coord, facing

class Day(BaseDay):
    day = 22

    def parse_lines(self) -> tuple[dict[Coord, bool], list[str]]:
        coords = {}
        for y, line in enumerate(self.data_lines):
            if line == '':
                break

            for x, letter in enumerate(line):
                if letter != ' ':
                    coords[Coord(X(x + 1), Y(y + 1))] = (letter == '.')

        moves = re.findall('[0-9]+|L|R', self.data_lines[-1])

        return coords, moves

    def part_1(self):
        coords, moves = self.parse_lines()
        grid = Grid(coords)
        start_pos = Coord(grid.y_bounds[1][0], Y(1))
        turtle = Turtle(grid, start_pos, 'r')

        for move in moves:
            if move in ('L', 'R'):
                turtle.rotate(move == 'L')
            else:
                turtle.move_n(int(move))

        scores = {
            'r': 0, 'd': 1, 'l': 2, 'u': 3
        }

        print(turtle.pos)
        print(turtle.dir)
        print(f'Score is {1000 * turtle.pos.y + 4 * turtle.pos.x + scores[turtle.dir]}')

    def part_2(self):
        coords, moves = self.parse_lines()
        grid = Grid(coords)
        start_pos = Coord(grid.y_bounds[1][0], Y(1))
        turtle = Turtle3D(grid, start_pos, 'r')

        for move in moves:
            if move in ('L', 'R'):
                turtle.rotate(move == 'L')
            else:
                turtle.move_n(int(move))

        scores = {
            'r': 0, 'd': 1, 'l': 2, 'u': 3
        }

        print(turtle.pos)
        print(turtle.dir)
        print(f'Score is {1000 * turtle.pos.y + 4 * turtle.pos.x + scores[turtle.dir]}')

Day().execute()
# Day(f'day_{Day.day}_test.txt').execute()

# 34541 too low

# 7225 too low
# 50386 too low
# 130262 too high