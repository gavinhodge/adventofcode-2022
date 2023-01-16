from dataclasses import dataclass
from functools import cached_property
import math
from typing import Generator, NamedTuple
from base import BaseDay


class Coord(NamedTuple):
    x: int
    y: int


@dataclass
class Tree:
    height: int
    coord: Coord
    visible: bool = False


class Forest:
    def __init__(self):
        self.trees: dict[Coord, Tree] = {}

    @cached_property
    def max_coord(self) -> Coord:
        return Coord(
            max(coord.x for coord in self.trees.keys()),
            max(coord.y for coord in self.trees.keys())
        )

    def determine_visibility(self):
        for tree in self.trees.values():
            for path in self.get_neighbours(tree):
                if not path or all(tree.height > other.height for other in path):
                    tree.visible = True
    
    def get_neighbours(self, tree) -> Generator[list[Tree], None, None]:
        # Left
        yield [self.trees[Coord(x, tree.coord.y)] for x in range(tree.coord.x - 1, -1, -1)]

        # Right
        yield [self.trees[Coord(x, tree.coord.y)] for x in range(tree.coord.x + 1, self.max_coord.x + 1)]

        # Up
        yield [self.trees[Coord(tree.coord.x, y)] for y in range(tree.coord.y - 1, -1, -1)]

        # Down
        yield [self.trees[Coord(tree.coord.x, y)] for y in range(tree.coord.y + 1, self.max_coord.y + 1)]


class Day(BaseDay):
    day = 8

    def load_forest(self) -> Forest:
        forest = Forest()
        for y, line in enumerate(self.data_lines):
            for x, height in enumerate(line):
                forest.trees[Coord(x, y)] = Tree(int(height), Coord(x, y))

        return forest

    def part_1(self):
        forest = self.load_forest()
        forest.determine_visibility()

        total = sum(1 for tree in forest.trees.values() if tree.visible)
        print(f'Count is {total}')

    def part_2(self):
        forest = self.load_forest()

        max_score = 0
        for tree in forest.trees.values():
            scores = []
            for path in forest.get_neighbours(tree):
                score = 0
                for other in path:
                    score += 1
                    if other.height >= tree.height:
                        break

                scores.append(score)

            product = math.prod(scores)
            if product > max_score:
                max_score = product

        print(max_score)

Day().execute()
