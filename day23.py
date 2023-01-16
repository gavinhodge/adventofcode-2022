import collections
from typing import NamedTuple, NewType
from base import BaseDay
from tqdm import tqdm


X = NewType('X', int)
Y = NewType('Y', int)


class Coord(NamedTuple):
    x: X
    y: Y


class Elf:
    dirs = 'nswe'
    dir_peeks = {
        'n': ((-1, -1), (0, -1), (1, -1)),
        's': ((-1, 1), (0, 1), (1, 1)),
        'w': ((-1, 1), (-1, 0), (-1, -1)),
        'e': ((1, 1), (1, 0), (1, -1)),
    }

    def __init__(self, coord: Coord):
        self.coord = coord
        self.dir_offest = 0
        self.proposed_move: Coord | None = None
        self.all_dir_peeks = set()
        for val in self.dir_peeks.values():
            for peek in val:
                self.all_dir_peeks.add(peek)

    def propose_move(self, grid: "Grid") -> Coord | None:
        if all(Coord(self.coord.x + x, self.coord.y + y) not in grid.elves for x, y in self.all_dir_peeks):
            # Surrounding is empty... do nothing
            self.proposed_move = None
            return

        for n in range(4):
            direction = self.dirs[(n + self.dir_offest) % 4]
            peeks = self.dir_peeks[direction]
            if all(Coord(self.coord.x + x, self.coord.y + y) not in grid.elves for x, y in peeks):
                self.proposed_move = Coord(self.coord.x + peeks[1][0], self.coord.y + peeks[1][1])
                return
    
        self.proposed_move = None

    def move(self, coord: Coord):
        self.coord = coord
        self.dir_offest += 1


class Grid:
    def __init__(self):
        self.elves: dict[Coord, Elf] = {}

    def move_elves(self) -> bool:
        for elf in self.elves.values():
            elf.propose_move(self)

        counter = collections.Counter(e.proposed_move for e in self.elves.values() if e.proposed_move is not None)

        for elf in self.elves.values():
            if elf.proposed_move is not None and counter[elf.proposed_move] == 1:
                elf.move(elf.proposed_move)
            else:
                elf.move(elf.coord)
                # elf.proposed_move = None

        new_elves = {elf.coord: elf for elf in self.elves.values()}

        moves_happened = set(self.elves.keys()) == set(new_elves.keys())
        self.elves = new_elves

        return moves_happened

    def count_empty(self) -> int:
        # Determine bounds
        min_x = min(c.x for c in self.elves.keys())
        max_x = max(c.x for c in self.elves.keys())
        min_y = min(c.y for c in self.elves.keys())
        max_y = max(c.y for c in self.elves.keys())

        return (max_x - min_x + 1) * (max_y - min_y + 1) - len(self.elves)

    def output(self):
        min_x = min(c.x for c in self.elves.keys())
        max_x = max(c.x for c in self.elves.keys())
        min_y = min(c.y for c in self.elves.keys())
        max_y = max(c.y for c in self.elves.keys())

        for y in range(min_y, max_y + 1):
            line = []
            for x in range(min_x, max_x + 1):
                line.append('#' if Coord(X(x), Y(y)) in self.elves else '.')
            print(''.join(line))


class Day(BaseDay):
    day = 23

    def load_grid(self) -> Grid:
        grid = Grid()

        for y, line in enumerate(self.data_lines):
            for x, letter in enumerate(line):
                if letter == '#':
                    coord = Coord(X(x), Y(y))
                    grid.elves[coord] = Elf(coord)

        return grid

    def part_1(self):
        grid = self.load_grid()

        for _ in range(10):
            grid.move_elves()

        print(f'Answer is {grid.count_empty()}')

    def part_2(self):
        grid = self.load_grid()

        answer = 0
        for n in tqdm(range(10000)):
            if grid.move_elves():
                answer = n
                break

        print(f'Answer is {answer + 1}')

Day().execute()
# Day(f'day_{Day.day}_test.txt').execute()

# 3821 too low

# 969 too low