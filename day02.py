from typing import Literal
from base import BaseDay


class Day(BaseDay):
    day = 2

    def get_my_score(self, them: Literal['A', 'B', 'C'], me: Literal['X', 'Y', 'Z']) -> int:
        # A, B, C = Rock, Paper, Scissors
        # X, Y, Z = Rock, Paper, Scissors

        choice_scores = {
            'X': 1,
            'Y': 2,
            'Z': 3
        }

        WIN = 6
        DRAW = 3
        LOSS = 0
        game_scores = {
            'AX': DRAW,
            'AY': WIN,
            'AZ': LOSS,
            'BX': LOSS,
            'BY': DRAW,
            'BZ': WIN,
            'CX': WIN,
            'CY': LOSS,
            'CZ': DRAW,
        }

        return choice_scores[me] + game_scores[f'{them}{me}']

    def part_1(self):
        score = 0
        for line in self.data_lines:
            if line == '':
                continue

            them, me = line.split(' ')
            score += self.get_my_score(them, me)

        print(f'Score is {score}')

    def get_my_turn(self, them: Literal['A', 'B', 'C'], desired_result: Literal['X', 'Y', 'Z']) -> Literal['X', 'Y', 'Z']:
        # X, Y, Z = lose, draw, win
        # A, B, C = Rock, Paper, Scissors
        # X, Y, Z = Rock, Paper, Scissors
        turns = {
            'AX': 'Z',
            'AY': 'X',
            'AZ': 'Y',
            'BX': 'X',
            'BY': 'Y',
            'BZ': 'Z',
            'CX': 'Y',
            'CY': 'Z',
            'CZ': 'X',
        }
        return turns[f'{them}{desired_result}']

    def part_2(self):
        score = 0
        for line in self.data_lines:
            if line == '':
                continue

            them, desired_result = line.split(' ')
            me = self.get_my_turn(them, desired_result)
            score += self.get_my_score(them, me)

        print(f'Score is {score}')

Day().execute()
