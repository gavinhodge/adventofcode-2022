from base import BaseDay


class Day(BaseDay):
    day = 4

    def part_1(self):
        total = 0
        for line in self.data_lines:
            if line == '':
                continue

            first, second = line.split(',')
            a = self.range_to_tuple(first)
            b = self.range_to_tuple(second)

            if self.does_first_contain_second(a, b) or self.does_first_contain_second(b, a):
                total += 1

        print(total)

    def does_first_contain_second(self, a: tuple[int, int], b: tuple[int, int]) -> bool:
        return a[0] <= b[0] and a[1] >= b[1]

    def does_overlap(self, a: tuple[int, int], b: tuple[int, int]) -> bool:
        return (a[0] <= b[0] <= a[1]) or (a[0] <= b[1] <= a[1])

    def range_to_tuple(self, val: str) -> tuple[int, int]:
        a, b = val.split('-')
        return int(a), int(b)

    def part_2(self):
        total = 0
        for line in self.data_lines:
            if line == '':
                continue

            first, second = line.split(',')
            a = self.range_to_tuple(first)
            b = self.range_to_tuple(second)

            if self.does_first_contain_second(a, b) or self.does_first_contain_second(b, a) or self.does_overlap(a, b):
                total += 1

        print(total)

Day().execute()
