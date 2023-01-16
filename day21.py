import operator
from base import BaseDay
from tqdm import tqdm


class Day(BaseDay):
    day = 21

    def parse_lines(self):
        known: dict[str, float] = {}
        unknown: dict[str, tuple[str, str, str]] = {}
        for line in self.data_lines:
            p1, p2 = line.split(':')
            try:
                num = int(p2.strip())
                known[p1] = num
            except ValueError:
                bits = p2.strip().split(' ')
                unknown[p1] = tuple(bits)

        return known, unknown

    def solve(self, known: dict[str, float], unknown: dict[str, tuple[str, str, str]]):
        ops = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.ifloordiv
        }

        while unknown:
            to_remove = []
            for key, val in unknown.items():
                a, op, b = val
                if a in known and b in known:
                    known[key] = ops[op](known[a], known[b])
                    to_remove.append(key)

            if not to_remove:
                break  # Didn't find anything

            for key in to_remove:
                del unknown[key]

    def part_1(self):
        known, unknown = self.parse_lines()

        self.solve(known, unknown)

        print(known['root'])

    def part_2(self):
        known, unknown = self.parse_lines()
        root_1, _, root_2 = unknown['root']
        del known['humn']
        del unknown['root']

        self.solve(known, unknown)

        if root_1 in known:
            known_key, unknown_key = root_1, root_2
        else:
            known_key, unknown_key = root_2, root_1

        target = known[known_key]
        target_key = unknown_key
        known[unknown_key] = target  # There is now an overlap between known/unknown
        print(f'Target is {target}')

        # Work backwards
        while True:
            to_remove = []
            for key, vals in unknown.items():
                if key in known and any(k in known for k in vals):
                    # We know 2/3, we can figure out the rest
                    assert vals[0] not in known or vals[2] not in known
                    known_key = vals[0] if vals[0] in known else vals[2]
                    unknown_key = vals[2] if vals[0] in known else vals[0]
                    op = vals[1]
                    ans = known[key]
                    a = known[known_key]

                    if op == '+':
                        known[unknown_key] = ans - a

                    elif op == '-' and known_key == vals[0]:
                        known[unknown_key] = a - ans

                    elif op == '-' and known_key == vals[2]:
                        known[unknown_key] = ans + a

                    elif op == '*':
                        known[unknown_key] = ans / a

                    elif op == '/' and known_key == vals[0]:
                        known[unknown_key] = a / ans

                    elif op == '/' and known_key == vals[2]:
                        known[unknown_key] = a * ans

                    else:
                        raise ValueError("Unexpected")

                    to_remove.append(key)
                    # print(f"Solved key {unknown_key} as {known[unknown_key]}. {len(unknown)} left")
                    break

            if not to_remove:
                break

            for key in to_remove:
                try:
                    del unknown[key]
                except KeyError:
                    print(f"Couldn't delete key {key}")
                
                # self.solve(known, unknown)

        answer = known['humn']
        print(f'humn should be {known["humn"]}')

        # Verify
        known, unknown = self.parse_lines()
        known['humn'] = answer
        root_1, _, root_2 = unknown['root']
        del unknown['root']
        self.solve(known, unknown)

        print(f'Roots were {known[root_1]} and {known[root_2]}')


Day().execute()
# Day(f'day_{Day.day}_test.txt').execute()


# ans = a + x  =>  x = ans - a
# ans = x - a  =>  x = ans + a
# ans = a - x  =>  ans + x = a   =>  x = a - ans
# ans = a * x  =>  x = ans / a
# ans = a / x  =>  ans*x = a    =>  x = a / ans
# ans = x / a  =>  x = ans * a

# -5387037869263
# 5387037869263
# -5387037871181

# 46779208742730