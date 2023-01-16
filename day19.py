import contextlib
from dataclasses import dataclass, field
from functools import lru_cache
import math
from queue import PriorityQueue
import re
from typing import Generator, NamedTuple, TypeAlias
from base import BaseDay
from tqdm import tqdm


Robots: TypeAlias = tuple[int, int, int, int]
Resources: TypeAlias = tuple[int, int, int, int]


class Blueprint(NamedTuple):
    id: int
    ore_robot_cost: int  # in Ore
    clay_robot_cost: int  # in Ore
    obsidian_robot_cost: tuple[int, int]  # in Ore + Clay
    geode_robot_cost: tuple[int, int]  # in Ore + Obsidian


class State(NamedTuple):
    minutes_left: int
    resources: Resources
    robots: Robots


@dataclass(order=True, slots=True)
class PriorityState:
    priority: int
    state: State = field(compare=False)


ORE, CLAY, OBS, GEO = 0, 1, 2, 3
TYPE_COUNT = 4
 

def can_build(state: State, costs: Resources) -> bool:
    return all(res >= cost for res, cost in zip(state.resources, costs))


@lru_cache(maxsize=100000)
def time_to_build(robots: Robots, resources: Resources, costs: Resources) -> int:
    times = []
    for cost, robot_count, resource in zip(costs, robots, resources):
        if cost == 0:
            continue

        if robot_count == 0:
            raise ValueError("Can't build - need some robots for a resource")

        times.append(math.ceil((cost - resource) / robot_count))

    return max(times)


class Simulation:
    def __init__(self, blueprint: Blueprint, minutes: int):
        self.minutes = minutes
        self.robot_costs = (
            (blueprint.ore_robot_cost, 0, 0, 0),
            (blueprint.clay_robot_cost, 0, 0, 0),
            (blueprint.obsidian_robot_cost[0], blueprint.obsidian_robot_cost[1], 0, 0),
            (blueprint.geode_robot_cost[0], 0, blueprint.geode_robot_cost[1], 0)
        )
        self.max_build_costs: Resources = tuple(max(robot[idx] for robot in self.robot_costs) for idx in range(4))

    def generate_end_states_dfs(self) -> Generator[State, None, None]:
        initial_state = State(self.minutes, (0, 0, 0, 0), (1, 0, 0, 0))

        stack: list[State] = [initial_state]
        seen: set[State] = set()

        while stack:
            state = stack.pop()
            if state in seen:
                continue

            if state.minutes_left == 0:
                yield state
                continue

            seen.add(state)

            for new_state in self.next_states(state):
                stack.append(new_state)

    def generate_end_states(self) -> Generator[State, None, None]:
        initial_state = State(self.minutes, (0, 0, 0, 0), (1, 0, 0, 0))

        stack: PriorityQueue[PriorityState] = PriorityQueue()
        stack.put(PriorityState(0, initial_state))

        # seen: set[State] = set()

        while stack:
            state = stack.get().state
            stack.task_done()
            # if state in seen:
            #     continue

            if state.minutes_left == 0:
                yield state
                continue

            # seen.add(state)

            for new_state in self.next_states(state):
                stack.put(PriorityState(-1 * new_state.resources[GEO], new_state))

    def next_states(self, state: State) -> Generator[State, None, None]:
        "Generate possible next states based on picking what to build next"

        # Option 1: don't build anything, just wait out the remaining time
        # Do this when we definitely can't build any more geode robots
        # before 1 minute left
        if state.resources[GEO] > 0:
            yield self.wait_out(state)

        if state.minutes_left == 1:
            # No point building anything - time will run out before it's productive
            pass

        # Option 2: generate a state by picking each robot to build next
        for type_idx, robot_costs in enumerate(self.robot_costs):
            with contextlib.suppress(ValueError):
                # Don't build more robots than the max build cost for that resource
                if type_idx != GEO and state.robots[type_idx] >= self.max_build_costs[type_idx]:
                    continue

                build_time = max(0, time_to_build(state.robots, state.resources, robot_costs))
                if build_time > state.minutes_left - 1:
                    continue  # Not enough to build + mine

                yield self.build_bot(state, type_idx, robot_costs, build_time + 1)

    def wait_out(self, state: State) -> State:
        return State(
            0,
            tuple(res + state.minutes_left * n_robots for res, n_robots in zip(state.resources, state.robots)),
            state.robots
        )

    def build_bot(self, state: State, type_idx: int, costs: Resources, build_time: int) -> State:
        return State(
            state.minutes_left - build_time,
            tuple(res - cost + build_time * n_robots for res, n_robots, cost in zip(state.resources, state.robots, costs)),
            tuple(r + (1 if type_idx == idx else 0) for idx, r in enumerate(state.robots))
        )

class Day(BaseDay):
    day = 19

    def load_blueprints(self) -> Generator[Blueprint, None, None]:
        for line in self.data_lines:
            idx, ore, clay, obs_1, obs_2, geo_1, geo_2 = re.findall('[0-9]+', line)
            yield Blueprint(
                int(idx), int(ore), int(clay),
                (int(obs_1), int(obs_2)), (int(geo_1), int(geo_2))
            )

    def part_1(self):
        results = []
        for bp in tqdm(self.load_blueprints()):
            sim = Simulation(bp, 24)
            max_geode = 0
            n_since_max = 0
            state_iter = sim.generate_end_states_dfs()
            for state in state_iter:
                if state.resources[GEO] > max_geode:
                    max_geode = state.resources[GEO]
                    n_since_max = 0
                else:
                    n_since_max += 1

                if n_since_max > 100000:
                    break

            # print(f'BP {bp.id} has geode count {max_geode}')
            results.append(max_geode)

        print(results)
        print(sum((idx + 1) * n for idx, n in enumerate(results)))

    def part_2(self):
        results = []
        blueprints = list(self.load_blueprints())
        for bp in blueprints[:3]:
            sim = Simulation(bp, 32)
            max_geode = 0
            state_iter = tqdm(sim.generate_end_states_dfs())
            for state in state_iter:
                if state.resources[GEO] > max_geode:
                    max_geode = state.resources[GEO]

            # print(f'BP {bp.id} has geode count {max_geode}')
            results.append(max_geode)

        print(results)
        print(results[0] * results[1] * results[2])

Day().execute()
# Day(f'day_{Day.day}_test.txt').execute()


# 1352 too low