import contextlib
from functools import cached_property
from typing import NamedTuple
from base import BaseDay


class Coord(NamedTuple):
    x: int
    y: int


class HaltException(Exception):
    pass


class Grid:
    def __init__(self):
        self.coords: dict[Coord, str] = {}
        self.sand_count = 0

    def add_path(self, pairs: list[tuple[Coord, Coord]]):
        for pair in pairs:
            x_start, x_end = pair[0].x, pair[1].x
            if x_end < x_start:
                x_start, x_end = x_end, x_start

            y_start, y_end = pair[0].y, pair[1].y
            if y_end < y_start:
                y_start, y_end = y_end, y_start

            # Fill path, inclusive
            for x in range(x_start, x_end + 1):
                for y in range(y_start, y_end + 1):
                    self.coords[Coord(x, y)] = '#'

            self.coords[pair[0]] = '#'
            self.coords[pair[1]] = '#'

    @cached_property
    def max_y(self):
        return max(coord.y for coord in self.coords)

    def is_empty(self, coord):
        return coord not in self.coords

    def add_sand(self) -> Coord:
        position = Coord(500, 0)

        while True:
            if position.y > (self.max_y + 10):
                # Sand is falling to infinity
                raise HaltException()

            next_down = Coord(position.x, position.y + 1)
            if self.is_empty(next_down):
                position = next_down
                continue

            next_left = Coord(position.x - 1, position.y + 1)
            if self.is_empty(next_left):
                position = next_left
                continue

            next_right = Coord(position.x + 1, position.y + 1)
            if self.is_empty(next_right):
                position = next_right
                continue

            # Nothing available. We've found a spot
            if position == Coord(500, 0):
                self.coords[position] = 'o'
                self.sand_count += 1
                raise HaltException()

            break

        self.coords[position] = 'o'
        self.sand_count += 1
        return position

    def add_floor(self):
        self.add_path([(Coord(-1000, self.max_y + 2), Coord(1000, self.max_y + 2))])

    def output(self):
        min_x = min(coord.x for coord in self.coords)
        max_x = max(coord.x for coord in self.coords)
        min_y = 0
        max_y = self.max_y

        for y in range(min_y, max_y + 1):
            line = [self.coords.get(Coord(x, y), '.') for x in range(min_x, max_x + 1)]
            print(''.join(line))


class Day(BaseDay):
    day = 14

    def load_grid(self) -> Grid:
        grid = Grid()

        for line in self.data_lines:
            coords = line.split(' -> ')
            pairs = []
            
            for idx, coord in enumerate(coords):
                with contextlib.suppress(IndexError):
                    coord_1x, coord_1y = coord.split(',')
                    coord_2x, coord_2y = coords[idx + 1].split(',')
                    pairs.append((Coord(int(coord_1x), int(coord_1y)), Coord(int(coord_2x), int(coord_2y))))

            grid.add_path(pairs)
        
        return grid

    def part_1(self):
        grid = self.load_grid()
        grid.output()

        with contextlib.suppress(HaltException):
            while True:
                grid.add_sand()

        print()
        grid.output()

        print(grid.sand_count)

    def part_2(self):
        grid = self.load_grid()
        grid.add_floor()
        # grid.output()

        with contextlib.suppress(HaltException):
            while True:
                grid.add_sand()

        # print()
        # grid.output()

        print(grid.sand_count)


Day().execute()
# Day(f'day_{Day.day}_test.txt').execute()
