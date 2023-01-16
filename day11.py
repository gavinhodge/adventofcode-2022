from base import BaseDay
import operator
import math


class Monkey:
    def __init__(self):
        self.items = []
        self.operation: list[str] = None
        self.test_div: int = None
        self.true_throw: int = None
        self.false_throw: int = None
        self.inspection_count = 0
        self.worry_divide = 3

    def take_turn(self, monkeys: list['Monkey']):    
        for item in self.items:
            self.inspection_count += 1
            new_item = self.apply_operation(item)

            if self.worry_divide:
                new_item = new_item // self.worry_divide

            if self.apply_test(new_item):
                monkeys[self.true_throw].catch(new_item)
            else:
                monkeys[self.false_throw].catch(new_item)

        self.items = []

    def apply_operation(self, item: int) -> int:
        op1, oper, op2 = self.operation
        opers = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.ifloordiv
        }
        op1 = item if op1 == 'old' else int(op1)
        op2 = item if op2 == 'old' else int(op2)

        return opers[oper](op1, op2)

    def apply_test(self, item: int) -> bool:
        return item % self.test_div == 0

    def reduce_gcd(self, lcm: int):
        self.items = [item % lcm for item in self.items]

    def catch(self, item: int):
        self.items.append(item)

    def __str__(self):
        return ', '.join(str(i) for i in self.items)

class Day(BaseDay):
    day = 11

    def parse_monkeys(self) -> list[Monkey]:
        current_monkey = None
        monkeys = []
        for line in self.data_lines:
            match line.split():
                case ['Monkey', num]:
                    current_monkey = Monkey()
                    monkeys.append(current_monkey)
                case ['Starting', 'items:', *items]:
                    current_monkey.items = [int(item.replace(',', '')) for item in items]
                case ['Operation:', 'new', '=', *operation]:
                    current_monkey.operation = operation
                case ['Test:', 'divisible', 'by', div_by]:
                    current_monkey.test_div = int(div_by)
                case ['If', 'true:', 'throw', 'to', 'monkey', throw_to]:
                    current_monkey.true_throw = int(throw_to)
                case ['If', 'false:', 'throw', 'to', 'monkey', throw_to]:
                    current_monkey.false_throw = int(throw_to)
                case []:
                    pass

        return monkeys

    def part_1(self):
        monkeys = self.parse_monkeys()
        for _ in range(20):
            for monkey in monkeys:
                monkey.take_turn(monkeys)

        monkeys.sort(key=lambda m: m.inspection_count)
        print(monkeys[-2].inspection_count * monkeys[-1].inspection_count)

    def part_2(self):
        monkeys = self.parse_monkeys()
        gcd = math.prod(m.test_div for m in monkeys)
        print(f'{gcd=}')

        for monkey in monkeys:
            monkey.worry_divide = None

        for _ in range(10000):
            for monkey in monkeys:
                monkey.reduce_gcd(gcd)
                monkey.take_turn(monkeys)

        monkeys.sort(key=lambda m: m.inspection_count)
        print(monkeys[-2].inspection_count * monkeys[-1].inspection_count)

Day().execute()
