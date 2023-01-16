import contextlib
from collections import deque
import itertools
from tqdm import tqdm
from functools import cached_property, lru_cache
import re
from typing import Generator, NamedTuple
from base import BaseDay
import networkx
import gc


def setup_gc():
    """
    Suggested here: https://mkennedy.codes/posts/python-gc-settings-change-this-and-make-your-app-go-20pc-faster/

    Seems to work well. It's important that it only happens once ever in the python process.
    """
    # gc.set_debug(gc.DEBUG_STATS)  # Enable to have each GC printed to the console
    allocs, gen1, gen2 = gc.get_threshold()
    allocs = 50_000  # Start the GC sequence every 50K not 700 allocations.
    gen1 = gen1 * 2
    gen2 = gen2 * 2
    gc.set_threshold(allocs, gen1, gen2)


class Valve(NamedTuple):
    name: str
    flow_rate: int
    tunnels: tuple[str]


class GameState(NamedTuple):
    pressure: int
    total_pressure: int
    minute: int
    position: Valve
    closed_valves: frozenset[Valve]
    history: list[str]

@lru_cache(maxsize=None)
def _shortest_path(a: Valve, b: Valve, all_valves: tuple[Valve]) -> list[Valve]:
    stack: deque[list[Valve]] = deque([[a]])

    while stack:
        current_path = stack.popleft()
        
        if len(current_path) > 50:
            raise ValueError('No path found')

        if current_path[-1] == b:
            return current_path  # First path we find will be shortest

        for tunnel in current_path[-1].tunnels:
            valve = next(v for v in all_valves if v.name == tunnel)
            stack.append(current_path + [valve])

    raise ValueError('No path found')


@lru_cache(maxsize=100000)
def _shortest_path_length(a: Valve, b: Valve, all_valves: tuple[Valve]) -> int:
    if a == b:
        return 0

    def find_valve(name: str):
        return next(v for v in all_valves if v.name == name)

    return min(_shortest_path_length(find_valve(tunnel), b, all_valves) for tunnel in a.tunnels) + 1


def floyd(valves: list[Valve]) -> dict[tuple[str, str], int]:
    # Construct a matrix with known path weights between valves
    valve_indexes = {v.name: idx for idx, v in enumerate(valves)}

    inf = 1000000
    matrix: list[list[int]] = [
        [inf for _ in valves] for _ in valves
    ]

    for idx, valve in enumerate(valves):
        matrix[idx][idx] = 0
        for tunnel in valve.tunnels:
            matrix[idx][valve_indexes[tunnel]] = 1

    n_v = len(valves)
    for k, i, j in itertools.product(range(n_v), range(n_v), range(n_v)):
        matrix[i][j] = min(matrix[i][j], matrix[i][k] + matrix[k][j])

    # Constuct a dict for each valve -> non-empty valve
    output = {}
    for idx, valve in enumerate(valves):
        for other_idx, other in enumerate(valves):
            if other.flow_rate > 0:
                output[(valve.name, other.name)] = matrix[idx][other_idx]

    return output

class Day(BaseDay):
    day = 16

    minutes = 0
    def make_graph(self) -> networkx.DiGraph:
        g = networkx.DiGraph()
        end = 'end'

        # Nodes first
        for line in self.data_lines:
            valve, flow_rate, *valves = re.findall('[A-Z]{2}|[0-9]+', line)
            g.add_node(valve, flow_rate=int(flow_rate))

        # Now edges
        for line in self.data_lines:
            valve, flow_rate, *valves = re.findall('[A-Z]+|[0-9]+', line)
            for dest in valves:
                g.add_edge(valve, dest)

            g.add_edge(valve, end)  # Hack: every valve can be an end
            
        return g

    @cached_property
    def valves(self) -> dict[str, Valve]:
        output = {}

        for line in self.data_lines:
            name, flow_rate, *tunnels = re.findall('[A-Z]{2}|[0-9]+', line)
            output[name] = Valve(name, int(flow_rate), tuple(tunnels))

        return output

    @cached_property
    def all_valves(self) -> tuple[Valve]:
        return tuple(self.valves.values())

    def shortest_path(self, a: Valve, b: Valve) -> list[Valve]:
        return _shortest_path(a, b, self.all_valves)

    def generate_games(self) -> Generator[GameState, None, None]:
        starting_valve = self.valves['AA']
        initial_state = GameState(
            0, 0, 1, starting_valve, 
            frozenset(v for v in self.all_valves if v.flow_rate > 0),
            [starting_valve.name]
        )
        dfs_stack: list[GameState] = []
        dfs_stack.extend(self.next_moves(initial_state))

        similar_states: set[tuple[Valve, int, frozenset[Valve], int]] = set()

        while dfs_stack:
            state = dfs_stack.pop()

            if (state.position, state.minute, state.closed_valves, state.total_pressure) in similar_states:
                continue  # We've already handled a similar state

            similar_states.add((state.position, state.minute, state.closed_valves, state.total_pressure))

            if state.minute >= self.minutes:
                yield state
                continue

            dfs_stack.extend(self.next_moves(state))

    def next_moves(self, state: GameState) -> Generator[GameState, None, None]:
        # Given a state, figure out the next possible moves

        # Or move to an open valve
        for valve in sorted(state.closed_valves, key=lambda v: v.flow_rate):
            if valve == state.position:
                continue
            new_state = self.move_to(state, valve)
            with contextlib.suppress(ValueError):
                new_state = self.open_valve(new_state)
            yield new_state

        if not state.closed_valves:
            # Wait here
            minutes = self.minutes - state.minute
            yield GameState(
                state.pressure, state.total_pressure + (state.pressure * minutes),
                state.minute + minutes, state.position,
                state.closed_valves, state.history + ['sit' for _ in range(minutes)]
            )

    
    def open_valve(self, state: GameState) -> GameState:
        if state.position not in state.closed_valves:
            raise ValueError("Already open")

        if state.position.flow_rate == 0:
            raise ValueError("Valve doesn't have any flow")

        if state.minute == self.minutes:
            raise ValueError("Out of time")

        return GameState(
            state.pressure + state.position.flow_rate, state.total_pressure + state.pressure,
            state.minute + 1, state.position,
            state.closed_valves - {state.position}, state.history + [f'open {state.position}']
        )

    def move_to(self, state: GameState, pos: Valve) -> GameState:
        path = self.shortest_path(state.position, pos)[1:]  # Exclude first valve

        jumps_allowed = len(path)
        jumps_to_execute = min(self.minutes - state.minute, jumps_allowed)
        
        return GameState(
            state.pressure, state.total_pressure + (state.pressure * jumps_to_execute),
            state.minute + jumps_to_execute, path[jumps_to_execute - 1],
            state.closed_valves, state.history + [f'move {valve.name}' for valve in path[:jumps_to_execute]]
        )

    def part_1(self):
        self.minutes = 31
        max_score = 0
        best = None
        games = tqdm(self.generate_games())
        for game in games:
            assert game.minute == self.minutes
            assert len(game.history) == self.minutes
            if game.total_pressure > max_score:
                max_score = game.total_pressure
                best = game
                games.set_description(f'Max is {max_score}')

        assert best is not None
        print(best)
        print(best.total_pressure)

    def part_2(self):
        self.minutes = 27
        games = list(self.generate_games())

        count = 0
        for g1, g2 in tqdm(itertools.product(games, games)):
            count += 1

        print(count)

        print(len(games))


class GameStateV2(NamedTuple):
    position: Valve
    time_left: int
    open_valves: tuple[str, ...]


class DayV2(BaseDay):
    day = 16

    initial_time_left = 0

    def part_1(self):
        self.initial_time_left = 30
        max_score = 0

        games = tqdm(self.generate_games())
        for game in games:
            score = self.determine_score(game.open_valves)
            if score > max_score:
                max_score = score
                games.set_description(str(max_score))
        print(max_score)

    def part_2(self):
        self.initial_time_left = 26
        max_score = 0

        games = list(self.generate_games())

        games.sort(key=lambda g: self.determine_score(g.open_valves), reverse=True)

        game_iter = tqdm(games)
        for g1 in game_iter:
            for g2 in games:
                score = self.determine_score_p2(g1.open_valves, g2.open_valves)
                if score > max_score:
                    max_score = score
                    game_iter.set_description(str(max_score))

        print(max_score)

    @cached_property
    def valves(self) -> dict[str, Valve]:
        output = {}

        for line in self.data_lines:
            name, flow_rate, *tunnels = re.findall('[A-Z]{2}|[0-9]+', line)
            output[name] = Valve(name, int(flow_rate), tuple(tunnels))

        return output

    @cached_property
    def non_zero_valves(self) -> list[Valve]:
        return [v for v in self.valves.values() if v.flow_rate > 0]

    @cached_property
    def distances(self) -> dict[tuple[str, str], int]:
        return floyd(list(self.valves.values()))

    def generate_games(self) -> Generator[GameStateV2, None, None]:
        initial_state = GameStateV2(self.valves['AA'], self.initial_time_left, tuple())

        dfs_stack: list[GameStateV2] = []
        dfs_stack.extend(self.next_moves(initial_state))

        while dfs_stack:
            state = dfs_stack.pop()

            if state.time_left == 0:
                yield state
                continue

            dfs_stack.extend(self.next_moves(state))

    def next_moves(self, state: GameStateV2) -> Generator[GameStateV2, None, None]:
        # Find candidate valves to open next
        candidates = [
            v for v in self.non_zero_valves
            if v.name not in state.open_valves and self.distances[(state.position.name, v.name)] < state.time_left - 2
        ]

        if candidates:
            for candidate in candidates:
                yield self.move_to(state, candidate)
        else:
            yield self.move_to(state, state.position)  # Stay in place and wait out the time

    def move_to(self, state: GameStateV2, valve: Valve) -> GameStateV2:
        if valve == state.position:
            # Same valve... stay here until time ends
            return GameStateV2(state.position, 0, state.open_valves)

        open_valves = state.open_valves + (valve.name,)
        distance = self.distances[(state.position.name, valve.name)]
        return GameStateV2(valve, state.time_left - distance - 1, open_valves)

    def determine_score(self, open_valves: tuple[str, ...]) -> int:
        time_left = self.initial_time_left
        cumulative_pressure = 0
        pressure = 0
        current_valve = 'AA'
        for valve in open_valves:
            # Move to valve
            distance = self.distances[(current_valve, valve)]
            cumulative_pressure += distance * pressure
            time_left -= distance
            current_valve = valve

            # Open valve
            cumulative_pressure += pressure
            pressure += self.valves[valve].flow_rate
            time_left -= 1

        assert time_left >= 0

        # Use up remaining time
        cumulative_pressure += time_left * pressure

        return cumulative_pressure

    def determine_score_p2(self, open_valves_1: tuple[str, ...], open_valves_2: tuple[str, ...]) -> int:
        time_left = self.initial_time_left
        cumulative_pressure = 0
        pressure = 0
        open_valves = set()
        p1_iter = iter(open_valves_1)
        p2_iter = iter(open_valves_2)
        iters = [p1_iter, p2_iter]
        dest_valves = [next(p1_iter), next(p2_iter)]
        moving_seconds_remaining = [self.distances[('AA', dest_valves[0])], self.distances[('AA', dest_valves[1])]]

        while time_left > 0:
            cumulative_pressure += pressure
            for pl in range(2):
                if moving_seconds_remaining[pl] == 0:
                    current_valve = dest_valves[pl]
                    # Open this valve if not open
                    if current_valve not in open_valves:
                        open_valves.add(current_valve)
                        pressure += self.valves[current_valve].flow_rate

                    # Setup move to next valve
                    try:
                        dest = next(iters[pl])
                        moving_seconds_remaining[pl] = self.distances[(dest_valves[pl], dest)] + 1
                        dest_valves[pl] = dest
                    except StopIteration:
                        # Out of moves, stay here
                        moving_seconds_remaining[pl] = 1000

                moving_seconds_remaining[pl] -= 1

            time_left -= 1

        return cumulative_pressure

setup_gc()

DayV2().execute()
# DayV2(f'day_{Day.day}_test.txt').execute()

# 1763 too low
# 1766 too low
# 1915
# 2198 too high