
from base import BaseDay


class Day01(BaseDay):
    day = 1

    def part_1(self):
        elves = [0]
        for line in self.data_lines:
            if line == '':
                elves.append(0)
                continue

            elves[-1] += int(line)

        self.elves = elves

        print(max(elves))

    def part_2(self):
        sorted_elves = list(sorted(self.elves))
        print(sorted_elves[-3:])
        print(sum(sorted_elves[-3:]))

Day01().execute()
