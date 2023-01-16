import string
from base import BaseDay


class Day(BaseDay):
    day = 3

    priorities = f' {string.ascii_lowercase}{string.ascii_uppercase}'

    def part_1(self):
        total = 0
        for line in self.data_lines:
            if line == '':
                continue

            half = len(line) // 2
            first = line[:half]
            second = line[half:]
            common = set(first).intersection(set(second))
            total += self.priorities.index(list(common)[0])

        print(total)

    def part_2(self):
        total = 0

        def _lines_by_chunk(lines: list[str]) -> tuple[str, str, str]:
            n = 0
            while n < (len(lines) - 1):
                yield lines[n], lines[n + 1], lines[n + 2]
                n += 3

        for group in _lines_by_chunk(self.data_lines):
            result = set(group[0]).intersection(set(group[1])).intersection(set(group[2]))

            assert len(result) == 1
            total += self.priorities.index(list(result)[0])
        
        print(total)

Day().execute()
