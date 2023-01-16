from dataclasses import dataclass
from functools import cached_property, lru_cache
import re
from typing import Generator, NamedTuple
from base import BaseDay
from tqdm import tqdm


class Coord(NamedTuple):
    x: int
    y: int


def manhattan_distance(a: Coord, b: Coord) -> int:
    return abs(a.x - b.x) + abs(a.y - b.y)


@dataclass
class Sensor:
    coord: Coord
    beacon_coord: Coord

    @cached_property
    def beacon_distance(self) -> int:
        # Manhattan distance
        return manhattan_distance(self.coord, self.beacon_coord)

    def coord_is_covered(self, other: Coord):
        return manhattan_distance(self.coord, other) <= self.beacon_distance

    def just_outside_coords(self) -> Generator[Coord, None, None]:
        # Start at the top of the diamond
        y = self.coord.y + self.beacon_distance + 1
        x = self.coord.x
        dx, dy = 1, 1
        start = Coord(x, y)
        current = start

        while True:
            yield current
            
            # Move x/y
            if abs(current.x - self.coord.x) == (self.beacon_distance + 1):
                # Reverse direction
                dx *= -1
            if abs(current.y - self.coord.y) == (self.beacon_distance + 1):
                # Reverse direction
                dy *= -1

            current = Coord(current.x + dx, current.y + dy)

            if current == start:
                return
        

class Grid:
    def __init__(self):
        self.sensors: list[Sensor] = []

    @cached_property
    def min_x(self):
        return min(sensor.coord.x - sensor.beacon_distance for sensor in self.sensors)
    
    @cached_property
    def max_x(self):
        return max(sensor.coord.x + sensor.beacon_distance for sensor in self.sensors)

    def coord_is_not_beacon(self, coord: Coord, sensors: list[Sensor]) -> bool:
        if any(sensor.beacon_coord == coord for sensor in sensors):
            return False  # Beacons don't count

        return any(sensor.coord_is_covered(coord) for sensor in sensors)

    def coord_is_covered(self, coord: Coord) -> bool:
        return any(sensor.coord_is_covered(coord) for sensor in self.sensors)

    def sensors_intersecting_with_line(self, y: int):
        for sensor in self.sensors:
            if sensor.coord.y - sensor.beacon_distance <= y <= sensor.coord.y + sensor.beacon_distance:
                yield sensor


class Day(BaseDay):
    day = 15

    def load_grid(self) -> Grid:
        grid = Grid()

        for line in self.data_lines:
            matches = re.findall('\-?[0-9]+', line)
            sensor_coord = Coord(int(matches[0]), int(matches[1]))
            beacon_coord = Coord(int(matches[2]), int(matches[3]))
            grid.sensors.append(Sensor(sensor_coord, beacon_coord))

        return grid

    def part_1(self):
        grid = self.load_grid()
        return

        # Naive: Go through each coord and see if it's covered by a sensor
        total = 0
        y = 2000000
        sensors = list(grid.sensors_intersecting_with_line(y))
        for x in tqdm(range(grid.min_x, grid.max_x + 1), 'x'):
            if grid.coord_is_not_beacon(Coord(x, y), sensors):
                total += 1

        print(total)

    def part_2(self):
        grid = self.load_grid()
        min_bounds = 0
        max_bounds = 4000000
        result = None

        # Search outline of each sensor
        for sensor in tqdm(grid.sensors, 'sensor'):
            if result is not None:
                break

            for idx, coord in enumerate(tqdm(sensor.just_outside_coords(), total=sensor.beacon_distance * 4)):
                if coord.x < min_bounds or coord.x > max_bounds:
                    continue
                if coord.y < min_bounds or coord.y > max_bounds:
                    continue

                if not grid.coord_is_covered(coord):
                    result = coord
                    break
    
        print(f'{result=}')
        print(result.x * max_bounds + result.y)


Day().execute()
# Day(f'day_{Day.day}_test.txt').execute()
