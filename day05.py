from base import BaseDay


class Day(BaseDay):
    day = 5

    def load_initial(self):
        lines = self.data_lines[:8]
        lines.reverse()
        STACK_COUNT = 9
        stacks = [list() for _ in range(STACK_COUNT)]

        for line in lines:
            for n in range(STACK_COUNT):
                letter = line[(n * 4) + 1]
                if letter != ' ':
                    stacks[n].append(letter)

        self.stacks = stacks

    def part_1(self):
        self.load_initial()
        
        instructions = self.data_lines[10:]
        for line in instructions:
            if line == '':
                continue

            _, a, _, b, _, c = line.split(' ')
            n, start, end = int(a), int(b), int(c)

            for _ in range(n):
                self.stacks[end - 1].append(self.stacks[start - 1].pop())

        ends = [stk.pop() for stk in self.stacks]
        print(''.join(ends))

    def part_2(self):
        self.load_initial()
        
        instructions = self.data_lines[10:]
        for line in instructions:
            if line == '':
                continue

            _, a, _, b, _, c = line.split(' ')
            n, start, end = int(a), int(b), int(c)

            to_remove = self.stacks[start - 1][-n:]
            del self.stacks[start - 1][-n:]

            self.stacks[end-1].extend(to_remove)

        ends = [stk.pop() for stk in self.stacks]
        print(''.join(ends))

Day().execute()
