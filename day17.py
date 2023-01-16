from dataclasses import dataclass
from typing import Generator, NamedTuple
from base import BaseDay
from tqdm import tqdm


class Coord(NamedTuple):
    x: int
    y: int


class RockType(NamedTuple):
    width: int
    height: int
    coords: tuple[Coord, ...]  # Shape pixels from top left


rock_types = [
    RockType(4, 1, ((Coord(0, 0), Coord(1, 0), Coord(2, 0), Coord(3, 0)))),
    RockType(3, 3, ((Coord(1, 0), Coord(0, 1), Coord(1, 1), Coord(2, 1), Coord(1, 2)))),
    RockType(3, 3, ((Coord(2, 0), Coord(2, 1), Coord(0, 2), Coord(1, 2), Coord(2, 2)))),
    RockType(1, 4, ((Coord(0, 0), Coord(0, 1), Coord(0, 2), Coord(0, 3)))),
    RockType(2, 2, ((Coord(0, 0), Coord(1, 0), Coord(0, 1), Coord(1, 1)))),
]


@dataclass
class Rock:
    tl_position: Coord
    height: int
    width: int
    shape: tuple[Coord, ...]
    stopped = False

    def occupied_coords(self, pos: Coord) -> Generator[Coord, None, None]:
        for coord in self.shape:
            yield Coord(pos.x + coord.x, pos.y - coord.y)

    def move(self, gas: str, blocked_coords: set[Coord]):
        dy = -1
        dx = -1 if gas == '<' else 1

        # Left/right first
        new_x_pos = Coord(self.tl_position.x + dx, self.tl_position.y)

        # Check for collision with wall
        if new_x_pos.x < 0 or (new_x_pos.x + self.width) > 7:
            # No move
            new_x_pos = self.tl_position
        elif set(self.occupied_coords(new_x_pos)) & blocked_coords:
            # Blocked by another rock, no move
            new_x_pos = self.tl_position

        # Move down
        new_y_pos = Coord(new_x_pos.x, new_x_pos.y + dy)

        # Check if collision with existing rocks
        if (new_y_pos.y - self.height) < -1:
            # Hit floor
            new_y_pos = new_x_pos
            self.stopped = True
        if set(self.occupied_coords(new_y_pos)) & blocked_coords:
            new_y_pos = new_x_pos
            self.stopped = True

        self.tl_position = new_y_pos


class Tunnel:
    width = 7
    
    def __init__(self):
        self.blocked_coords: set[Coord] = set()
        self.max_height = 0
        self.height_offset = 0

    def add_rock(self, rock_type: RockType, gases: Generator[str, None, None]):
        rock = Rock(
            Coord(2, self.max_height + 3 + (rock_type.height - 1)),
            rock_type.height, rock_type.width, rock_type.coords
        )

        while not rock.stopped:
            rock.move(next(gases), self.blocked_coords)

        occupied = set(rock.occupied_coords(rock.tl_position))
        self.blocked_coords |= occupied

        self.max_height = max(self.max_height, rock.tl_position.y + 1)

    def __str__(self) -> str:
        lines = [
            '|' + ''.join('#' if Coord(x, y) in self.blocked_coords else '.'  for x in range(self.width)) + '|'
            for y in range(self.max_height + 2, -1, -1)
        ]
        lines += ['-' * 9]
        lines += []

        return '\n'.join(lines)

    def collapse(self) -> int:
        # Find a horizontal line where no pieces could possible get through, and treat that as the new floor
        for y in range(self.max_height, -1, -1):
            if {Coord(x, y) for x in range(self.width)}.issubset(self.blocked_coords):
                # y will be the new floor
                self.height_offset += y

                # Translate all higher coords
                self.blocked_coords = {Coord(coord.x, coord.y - y) for coord in self.blocked_coords if coord.y >= y}
                self.max_height -= y
                return y

        raise ValueError("No collapse possible")
    
    def print_whole_rows(self):
        prev_match = 0
        for y in range(0, self.max_height):
            if {Coord(x, y) for x in range(self.width)}.issubset(self.blocked_coords):
                print(f'{y - prev_match}    {y=}')
                prev_match = y

    def peek_top(self, n: int) -> set[Coord]:
        # Top n rows, translated so the bottom row is y=0
        return {Coord(coord.x, coord.y - (self.max_height - n)) for coord in self.blocked_coords if coord.y >= (self.max_height - n)}


class Day(BaseDay):
    day = 17

    def gas_generator(self) -> Generator[str, None, None]:
        while True:
            yield from self.data_lines[0]

    def rock_type_generator(self) -> Generator[RockType, None, None]:
        while True:
            yield from rock_types

    def part_1(self):
        tunnel = Tunnel()
        rocks = self.rock_type_generator()
        gases = self.gas_generator()

        for _ in range(600):
            tunnel.add_rock(next(rocks), gases)

        # print(tunnel)
        print(tunnel.max_height)

    def part_2(self):
        self.setup_gc()
        print(flush=True)

        found = None
        tunnel = Tunnel()
        rocks = self.rock_type_generator()
        gases = self.gas_generator()
        peek_size = 50
        states: dict[frozenset[Coord], tuple[int, int]] = {}
        for loop_start in range(5000):
            tunnel.add_rock(next(rocks), gases)

            peek = frozenset(tunnel.peek_top(peek_size))

            if peek in states:
                # We found a match!
                found = loop_start, states[peek][0], tunnel.max_height - states[peek][1]
                break

            if tunnel.max_height > peek_size:
                states[peek] = loop_start, tunnel.max_height
        
        assert found is not None
        print(f'Cycle starts at {found[0]} and repeats every {found[0] - found[1]} and adds {found[2]}')
        cycle_start = found[0]
        cycle_period = found[0] - found[1]
        cycle_height = found[2]

        tunnel = Tunnel()
        rocks = self.rock_type_generator()
        gases = self.gas_generator()
        cycles = 1000000000000

        for _ in range(cycle_start):
            tunnel.add_rock(next(rocks), gases)
        cycles -= cycle_start

        divisor, remainder = divmod(cycles, cycle_period)
        for _ in range(remainder):
            tunnel.add_rock(next(rocks), gases)
        print(f'Answer is {tunnel.max_height + cycle_height * divisor}')

Day().execute()
# Day(f'day_{Day.day}_test.txt').execute()

# 3116 no
