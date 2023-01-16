import itertools
from base import BaseDay


snafu_digits = {
    '11': 6,
    '10': 5,
    '1-': 4,
    '1=': 3,
    '2': 2,
    '1': 1,
    '0': 0,
    '-': -1,
    '=': -2,
    '-2': -3,
    '-1': -4,
    '-0': -5,
    '--': -6,
}

snafu_rev = {v: k for k, v in snafu_digits.items()}

def snafu_to_int(snafu: str) -> int:
    return sum(
        5 ** (idx) * snafu_digits[letter]
        for idx, letter in enumerate(reversed(snafu))
    )


def add_snafu(a: str, b: str) -> str:
    # Zip reversed, add digits, carry if overflow (+ve or -ve!)
    answer = ''
    carry = '0'

    for x_str, y_str in itertools.zip_longest(reversed(a), reversed(b), fillvalue='0'):
        # Use integers then go back
        x = snafu_digits[x_str]
        y = snafu_digits[y_str]
        z = snafu_digits[carry]

        num = x + y + z
        digit = snafu_rev[num]

        answer = digit[-1] + answer
        carry = digit[0] if len(digit) > 1 else '0'

    if carry != '0':
        answer = carry + answer

    # Check it
    assert snafu_to_int(a) + snafu_to_int(b) == snafu_to_int(answer)

    return answer


def int_to_snafu(val: int) -> str:
    remaining = val
    power = 0
    output = ''

    # Find size of biggest digit we need
    while val > (5 ** power) * 2:
        power += 1

    while power >= 0:
        if remaining > (5 ** power):
            digit = '2'
        elif remaining > 0:
            digit = '1'
        elif remaining < -1 * (5 ** power):
            digit = '='
        elif remaining < 0:
            digit = '-' 
        else:
            digit = '0'

        output = output + digit
        remaining = remaining - (snafu_digits[digit] * (5 ** power))
        power -= 1

    assert snafu_to_int(output) == val

    return output


class Day(BaseDay):
    day = 25

    def part_1(self):
        total = '0'

        for line in self.data_lines:
            temp_total = total
            total = add_snafu(total, line)
            print(f'{temp_total} ({snafu_to_int(temp_total)}) + {line} ({snafu_to_int(line)}) >>> {total} ({snafu_to_int(total)})')
            int_to_snafu(snafu_to_int(line))

        print(total)


    def part_2(self):
        pass

Day().execute()
# Day(f'day_{Day.day}_test.txt').execute()


# 2==02=120-=-2110-0=1 is wrong