from base import BaseDay


class Cpu:
    def __init__(self):
        self.counter = 0
        self.x = 1
        self.history = [0]

    def noop(self):
        self.counter += 1
        self.history.append(self.x)

    def addx(self, x: int):
        self.counter += 1
        self.history.append(self.x)
        self.counter += 1
        self.x += x
        self.history.append(self.x)


class Crt:
    lines = 6
    rows = 40

    def __init__(self):
        self.pixels = ['.'] * (self.rows * self.lines)

    def __str__(self):
        lines = [
            self.pixels[self.rows * n:(self.rows * n) + self.rows] for n in range(self.lines)
        ]
        return '\n'.join(''.join(line) for line in lines)

    def draw_pixel(self, pos: int, sprite_pos: int):
        sprite_pixels = {sprite_pos - 1, sprite_pos, sprite_pos + 1}
        if pos % self.rows in sprite_pixels:
            self.pixels[pos] = '#'

class Day(BaseDay):
    day = 10

    def part_1(self):
        cpu = Cpu()
        for line in self.data_lines:
            match line.split():
                case ["noop"]:
                    cpu.noop()
                case ["addx", amount]:
                    cpu.addx(int(amount))

        total = 0
        for counter in range(20, 221, 40):
            # print(f'{counter=} {cpu.history[counter]=} {counter * cpu.history[counter]}')
            total += counter * cpu.history[counter - 1]
        print(total)

    def part_2(self):
        cpu = Cpu()
        crt = Crt()

        for line in self.data_lines:
            match line.split():
                case ["noop"]:
                    cpu.noop()
                case ["addx", amount]:
                    cpu.addx(int(amount))

        for idx, x in enumerate(cpu.history):
            crt.draw_pixel(idx, x)

        print(crt)

# Day('day_10_test.txt').execute()
Day().execute()
