import math
from typing import Generator, Iterable, Literal, NamedTuple
from base import BaseDay
from tqdm import tqdm
from collections import deque


Direction = Literal['>', '<', '^', 'v']


class Coord(NamedTuple):
    x: int
    y: int


class Storm(NamedTuple):
    coord: Coord
    dir: Direction


dir_vectors: dict[Direction, tuple[int, int]] = {
    '>': (1, 0),
    '<': (-1, 0),
    '^': (0, -1),
    'v': (0, 1),
}


def next_storms_state(storms: Iterable[Storm], bounds: tuple[Coord, Coord]) -> list[Storm]:
    new_storms = []

    for storm in storms:
        dx, dy = dir_vectors[storm.dir]
        new_coord = Coord(storm.coord.x + dx, storm.coord.y + dy)

        # Wrap around
        if new_coord.x < bounds[0].x:
            new_coord = Coord(bounds[1].x, new_coord.y)
        elif new_coord.x > bounds[1].x:
            new_coord = Coord(bounds[0].x, new_coord.y)
        elif new_coord.y < bounds[0].y:
            new_coord = Coord(new_coord.x, bounds[1].y)
        elif new_coord.y > bounds[1].y:
            new_coord = Coord(new_coord.x, bounds[0].y)

        new_storms.append(Storm(new_coord, storm.dir))

    return new_storms


class GameState(NamedTuple):
    time: int
    position: Coord


class Game:
    def __init__(self, start_pos: Coord, end_pos: Coord, bounds: tuple[Coord, Coord], initial_storms: Iterable[Storm]):
        self.bounds = bounds
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.valid_coords = {
            self.start_pos,
            self.end_pos
        }
        for x in range(self.bounds[0].x, self.bounds[1].x + 1):
            for y in range(self.bounds[0].y, self.bounds[1].y + 1):
                self.valid_coords.add(Coord(x, y))

        # Precompute all storm states
        self.storm_states: list[tuple[Iterable[Storm], set[Coord]]] = [
            (initial_storms, {s.coord for s in initial_storms})
        ]
        self.storm_modulo = math.lcm(self.bounds[1].x, self.bounds[1].y)
        for n in tqdm(range(self.storm_modulo)):
            self.get_storm_state(n + 1)

        self.seen_states: dict[tuple[int, Coord], GameState] = {}

    def get_storm_state(self, time: int) -> tuple[Iterable[Storm], set[Coord]]:
        try:
            return self.storm_states[time % self.storm_modulo]
        except IndexError:
            last_state, _ = self.storm_states[-1]
            new_state = next_storms_state(last_state, self.bounds)
            self.storm_states.append(
                (new_state, {s.coord for s in new_state})
            )
            return self.storm_states[time]

    def generate_solution(self, initial: GameState, goal_pos: Coord) -> GameState:
        stack: deque[GameState] = deque([initial])
        progress = tqdm()

        while stack:
            state = stack.popleft()
            progress.update()
            
            seen_key = (state.time % self.storm_modulo, state.position)

            if seen_key in self.seen_states:
                continue

            if state.position == goal_pos:
                return state

            self.seen_states[seen_key] = state

            stack.extend(self.next_moves(state))

        raise ValueError("No paths")


    def next_moves(self, state: GameState) -> Generator[GameState, None, None]:
        next_storms, next_storm_coords = self.get_storm_state(state.time + 1)

        # Stay
        if state.position not in next_storm_coords:
            yield GameState(state.time + 1, state.position)

        # Move
        for dx, dy in dir_vectors.values():
            new_coord = Coord(state.position.x + dx, state.position.y + dy)
            if new_coord not in next_storm_coords and new_coord in self.valid_coords:
                yield GameState(state.time + 1, new_coord)


class Day(BaseDay):
    day = 24

    def create_game(self) -> Game:
        bounds = (Coord(1, 1), Coord(len(self.data_lines[0]) - 2, len(self.data_lines) - 2))
        start_pos = Coord(self.data_lines[0].index('.'), 0)
        end_pos = Coord(self.data_lines[-1].index('.'), len(self.data_lines) - 1)

        storms = []
        for y, line in enumerate(self.data_lines):
            for x, letter in enumerate(line):
                if letter in '<>^v':
                    storms.append(Storm(Coord(x, y), letter))

        return Game(start_pos, end_pos, bounds, storms)

    def part_1(self):
        self.setup_gc()
        game = self.create_game()

        result = game.generate_solution(GameState(0, game.start_pos), game.end_pos)

        print(result.time)

    def part_2(self):
        game = self.create_game()

        result = game.generate_solution(GameState(0, game.start_pos), game.end_pos)
        result_2 = game.generate_solution(result, game.start_pos)
        result_3 = game.generate_solution(result_2, game.end_pos)

        print(f'{result.time=} {result_2.time=} {result_3.time=}')
        print(result_3.time)


Day().execute()
# Day(f'day_{Day.day}_test.txt').execute()

# 1681 too high
