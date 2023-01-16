from base import BaseDay


class Day(BaseDay):
    day = 6

    def part_1(self):
        # msg = 'mjqjpqmgbljsphdztnvjfqwrcgsmlb'
        msg = self.data_lines[0]
        size = 4
        for idx, letter in enumerate(msg):
            if len(set(msg[idx:idx + size])) == size:
                print(idx + size)
                break

    def part_2(self):
        msg = self.data_lines[0]
        size = 14
        for idx, letter in enumerate(msg):
            if len(set(msg[idx:idx + size])) == size:
                print(idx + size)
                break

Day().execute()
