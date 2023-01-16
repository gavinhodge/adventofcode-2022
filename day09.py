from typing import Literal, NamedTuple
from base import BaseDay


class Coord(NamedTuple):
    x: int
    y: int


class Rope:
    def __init__(self):
        self.head = Coord(0, 0)
        self.tail = Coord(0, 0)
        self.tail_history: set[Coord] = {Coord(0, 0)}

    def move_head(self, direction: Literal['U', 'D', 'L', 'R'], distance: int):
        if direction == 'U':
            self.head = Coord(self.head.x, self.head.y + distance)
        elif direction == 'D':
            self.head = Coord(self.head.x, self.head.y - distance)
        elif direction == 'L':
            self.head = Coord(self.head.x - distance, self.head.y)
        elif direction == 'R':
            self.head = Coord(self.head.x + distance, self.head.y)

    def move_tail(self):
        if abs(self.head.x - self.tail.x) <= 1 and abs(self.head.y - self.tail.y) <= 1:
            # No move
            return

        dx = 0
        if self.head.x > self.tail.x:
            dx = 1
        elif self.head.x < self.tail.x:
            dx = -1

        dy = 0
        if self.head.y > self.tail.y:
            dy = 1
        elif self.head.y < self.tail.y:
            dy = -1

        self.tail = Coord(self.tail.x + dx, self.tail.y + dy)
        self.tail_history.add(self.tail)


class Day(BaseDay):
    day = 9

    def part_1(self):
        rope = Rope()
        for line in self.data_lines:
            direction, distance = line.split(' ')
            for _ in range(int(distance)):
                rope.move_head(direction, 1)
                rope.move_tail()

        print(len(rope.tail_history))

    def part_2(self):
        ropes = [Rope() for _ in range(9)]
        for line in self.data_lines:
            direction, distance = line.split(' ')
            for _ in range(int(distance)):
                # Move first rope according to instructions
                ropes[0].move_head(direction, 1)
                ropes[0].move_tail()

                # Move subsequent ropes to match
                for idx, rope in enumerate(ropes):
                    if idx == 0:
                        continue

                    rope.head = ropes[idx - 1].tail
                    rope.move_tail()

        print(len(ropes[-1].tail_history))

Day().execute()
