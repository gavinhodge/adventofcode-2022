import contextlib
import functools
from typing import NamedTuple
from base import BaseDay
import ast
import builtins


class Pair(NamedTuple):
    first: list[int] | int
    second: list[int] | int


class OutOfOrderException(Exception):
    pass


class RightOrderException(Exception):
    pass


def make_comparator(less_than):
    def compare(x, y):
        if less_than(x, y):
            return -1
        elif less_than(y, x):
            return 1
        else:
            return 0
    return compare



class Day(BaseDay):
    day = 13

    def get_pairs(self) -> list[Pair]:
        pairs = []
        for idx in range(0, len(self.data_lines), 3):
            first = self.data_lines[idx]
            second = self.data_lines[idx + 1]
            pairs.append(Pair(ast.literal_eval(first), ast.literal_eval(second)))
        
        return pairs

    def part_1(self):
        pairs = self.get_pairs()

        total = 0
        for idx, pair in enumerate(pairs):
            if self.is_ordered(pair):
                # print(f'Pair {idx} is ordered')
                total += idx + 1

        print(total)

    def is_ordered(self, pair: Pair) -> bool:
        try:
            self.values_are_ordered(pair.first, pair.second)
        except RightOrderException:
            return True
        except OutOfOrderException:
            return False

        return True

    def compare(self, a: list[int] | int, b: list[int] | int) -> bool:
        return self.is_ordered(Pair(a, b))

    def values_are_ordered(self, a: list[int] | int, b: list[int] | int) -> None:
        match (type(a), type(b)):
            case [builtins.int, builtins.int]:
                if a < b:
                    raise RightOrderException()
                elif a == b:
                    return
                elif a > b:
                    raise OutOfOrderException(f'{a} was bigger than {b}')

            case [builtins.list, builtins.list]:
                for idx, first in enumerate(a):
                    try:
                        self.values_are_ordered(first, b[idx])
                    except IndexError:
                        raise OutOfOrderException(f'list {a} was longer than list {b}')  # B is shorter... not ok

                if len(a) < len(b):
                    raise RightOrderException()

            case [builtins.int, builtins.list]:
                self.values_are_ordered([a], b)

            case [builtins.list, builtins.int]:
                self.values_are_ordered(a, [b])

            case _:
                raise ValueError("No match!")


    def part_2(self):
        values = [ast.literal_eval(line) for line in self.data_lines if line != '']

        values.append([[2]])
        values.append([[6]])

        values.sort(key=functools.cmp_to_key(make_comparator(self.compare)))

        a_idx = values.index([[2]]) + 1
        b_idx = values.index([[6]]) + 1

        print(a_idx * b_idx)


Day().execute()
# Day(f'day_{Day.day}_test.txt').execute()
