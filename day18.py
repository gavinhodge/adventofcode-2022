from typing import NamedTuple
from base import BaseDay


class Coord(NamedTuple):
    x: int
    y: int
    z: int


class Grid:
    def __init__(self):
        self.coords: set[Coord] = set()
        self.air: set[Coord] = set()


class Day(BaseDay):
    day = 18

    def load_grid(self) -> Grid:
        grid = Grid()

        for line in self.data_lines:
            x, y, z = line.split(',')
            grid.coords.add(Coord(int(x), int(y), int(z)))

        return grid

    def part_1(self):
        grid = self.load_grid()
        total_exposed = 0
        directions = (
            (0, 0, 1), (0, 0, -1),
            (0, 1, 0), (0, -1, 0),
            (1, 0, 0), (-1, 0, 0)
        )
        for coord in grid.coords:
            for dx, dy, dz in directions:
                if Coord(coord.x + dx, coord.y + dy, coord.z + dz) not in grid.coords:
                    total_exposed += 1

        print(total_exposed)

    def fill_air(self, grid: Grid):
        # Start from an edge (which isn't occupied!) and flood in every direction
        # until hitting a coordinate or edge
        bounds = [
            max(coord.x for coord in grid.coords) + 2,
            max(coord.y for coord in grid.coords) + 2,
            max(coord.z for coord in grid.coords) + 2,
        ]

        start = Coord(-1, -1, -1)
        assert start not in grid.coords
        directions = (
            (0, 0, 1), (0, 0, -1),
            (0, 1, 0), (0, -1, 0),
            (1, 0, 0), (-1, 0, 0)
        )
        stack: list[Coord] = [start]

        while stack:
            coord = stack.pop()

            if coord in grid.air:
                # Already processed
                continue

            if coord in grid.coords:
                # It's occupied
                continue

            grid.air.add(coord)

            for dx, dy, dz in directions:
                new_coord = Coord(coord.x + dx, coord.y + dy, coord.z + dz)
                if all(n >= -1 and n <= bounds[idx] for idx, n in enumerate(new_coord)):
                    stack.append(new_coord)

    def part_2(self):
        grid = self.load_grid()
        total_exposed = 0
        directions = (
            (0, 0, 1), (0, 0, -1),
            (0, 1, 0), (0, -1, 0),
            (1, 0, 0), (-1, 0, 0)
        )
        self.fill_air(grid)
        for coord in grid.coords:
            for dx, dy, dz in directions:
                c = Coord(coord.x + dx, coord.y + dy, coord.z + dz)
                if c in grid.air:
                    total_exposed += 1

        print(total_exposed)
        grid = self.load_grid()


Day().execute()
# Day(f'day_{Day.day}_test.txt').execute()

# 2071 too low
