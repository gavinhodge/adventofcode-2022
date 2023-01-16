import contextlib
import string
from typing import NamedTuple
from base import BaseDay

import networkx


class Coord(NamedTuple):
    x: int
    y: int


class Grid:
    def __init__(self):
        self.coords: dict[Coord, int] = {}  # Coord : height
        self.start = Coord(0, 0)
        self.end = Coord(0, 0)

    def moves_from_coord(self, coord: Coord) -> list[Coord]:
        # Find any neighbours which are a valid move
        directions = [
            [1, 0],
            [-1, 0],
            [0, 1],
            [0, -1]
        ]
        neighbours = [Coord(coord.x + dx, coord.y + dy) for dx, dy in directions]

        return [n for n in neighbours if n in self.coords and self.coords[n] <= (self.coords[coord] + 1)]


class Day(BaseDay):
    day = 12

    def load_grid(self) -> Grid:
        grid = Grid()

        for y, line in enumerate(self.data_lines):
            for x, letter in enumerate(line):
                if letter == 'S':
                    height = 0
                    grid.start = Coord(x, y)
                elif letter == 'E':
                    height = 25
                    grid.end = Coord(x, y)
                else:
                    height = string.ascii_lowercase.index(letter)

                grid.coords[Coord(x, y)] = height

        return grid

    def load_graph(self, grid: Grid):
        edges = []
        for coord in grid.coords.keys():
            edges.extend((coord, neighbour) for neighbour in grid.moves_from_coord(coord))

        g = networkx.DiGraph()
        for coord in grid.coords.keys():
            g.add_node(coord)
        
        g.add_edges_from(edges)
        return g

    def part_1(self):
        grid = self.load_grid()
        g = self.load_graph(grid)

        print(networkx.shortest_path_length(g, source=grid.start, target=grid.end))

    def part_2(self):
        grid = self.load_grid()
        g = self.load_graph(grid)
        step_results = []

        for coord, height in grid.coords.items():
            if height == 0:
                with contextlib.suppress(networkx.NetworkXNoPath):
                    steps = networkx.shortest_path_length(g, source=coord, target=grid.end)
                    step_results.append(steps)

        print(min(step_results))


Day().execute()
# Day('day_12_test.txt').execute()
