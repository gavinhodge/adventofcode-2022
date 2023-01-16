import requests
from pathlib import Path

from time import perf_counter
from contextlib import suppress
from functools import cached_property
import gc
from typing import Optional


class Timer:
    def __enter__(self):
        self.start = perf_counter()
        return self

    def __exit__(self, type, value, traceback):
        self.elapsed = perf_counter() - self.start


class BaseDay:
    day = 0  # Override to get the right input

    def __init__(self, test_data_filename: Optional[str] = None):
        if self.day == 0:
            raise ValueError("Please set the `day` property")

        self.data_filename = test_data_filename or f'day_{self.day}.txt'

    def load_data(self) -> str:
        current_dir = Path(__file__).parent

        # Check cache first
        filename = f'inputs/{self.data_filename}'
        filename_path = current_dir.joinpath(filename)
        if filename_path.exists():
            print(f"Using cached input {filename_path}")
            return filename_path.read_text()

        # Download from website
        cookies = {'session': current_dir.joinpath('inputs/cookie.txt').read_text()}
        url = f'https://adventofcode.com/2022/day/{self.day}/input'
        print(f"Fetching {url}")
        response = requests.get(url, cookies=cookies)
        response.raise_for_status()

        data = response.text
        filename_path.write_text(data)

        return data

    @cached_property
    def data_lines(self) -> list[str]:
        data = self.load_data()
        return data.split('\n')[:-1]

    def part_1(self):
        raise NotImplementedError("Part 1 not yet implemented")

    def part_2(self):
        raise NotImplementedError("Part 2 not yet implemented")

    def execute(self):
        with suppress(NotImplementedError):
            with Timer() as t:
                print("Starting part 1...")
                self.part_1()

            print(f"Done in {t.elapsed:.2f}s")

        with suppress(NotImplementedError):
            with Timer() as t:
                print("Starting part 2...")
                self.part_2()
            
            print(f"Done in {t.elapsed:.2f}s")

    def setup_gc(self):
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