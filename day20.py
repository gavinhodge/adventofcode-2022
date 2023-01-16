import contextlib
from dataclasses import dataclass
from typing import Generator
from base import BaseDay


@dataclass
class ListEntry:
    value: int
    next: 'ListEntry'
    prev: 'ListEntry'


class Day(BaseDay):
    day = 20

    def construct_ll(self) -> list[ListEntry]:
        numbers = [int(line) for line in self.data_lines]
        list_entries = [ListEntry(n, None, None) for n in numbers]   # type: ignore

        # Connect them all up
        for idx, entry in enumerate(list_entries):
            with contextlib.suppress(IndexError):
                entry.next = list_entries[idx + 1]
            
            with contextlib.suppress(IndexError):
                entry.prev = list_entries[idx - 1]

        # Join the ends
        list_entries[0].prev = list_entries[-1]
        list_entries[-1].next = list_entries[0]

        return list_entries

    def move_entry(self, entry: ListEntry, list_len: int | None = None):
        if entry.value == 0:
            return

        moves = abs(entry.value) % (list_len - 1) if list_len else abs(entry.value)
        left = entry.value < 0
        for _ in range(moves):
            if left:
                self.move_left(entry)
            else:
                self.move_right(entry)

    def to_list(self, first: ListEntry):
        output = [first.value]
        nxt = first.next
        while nxt != first:
            output.append(nxt.value)
            nxt = nxt.next
        return output

    def move_left(self, entry: ListEntry):
        # From:  a b *c d
        # To:    a *c b d
        a, b, c, d = entry.prev.prev, entry.prev, entry, entry.next
        a.next = c
        c.prev = a
        c.next = b
        b.prev = c
        b.next = d
        d.prev = b

    def move_right(self, entry: ListEntry):
        self.move_left(entry.next)
        # From: a *b c d
        # To:   a c *b d
        # a, b, c, d = entry.prev, entry, entry.next, entry.next.next
        # a.next = b
        # c.prev = a
        # c.next = b
        # b.prev = c
        # b.next = d
        # d.prev = b

    def cycle(self, entry: ListEntry) -> Generator[ListEntry, None, None]:
        while True:
            yield entry
            entry = entry.next

    def part_1(self):
        entries = self.construct_ll()
        list_len = len(entries)

        for entry in entries:
            # print(self.to_list(entries[0]))
            self.move_entry(entry, list_len)

        # Find value 0
        zero = next(entry for entry in entries if entry.value == 0)

        values = []
        entries_iter = self.cycle(zero)
        for n in range(0, 3001):
            entry = next(entries_iter)
            if n % 1000 == 0:
                values.append(entry.value)

        print(values)
        print(sum(values))

    def part_2(self):
        entries = self.construct_ll()
        entry_len = len(entries)

        for entry in entries:
            entry.value *= 811589153

        for _ in range(10):
            # print(self.to_list(entries[0]))
            for entry in entries:
                self.move_entry(entry, entry_len)

        # Find value 0
        zero = next(entry for entry in entries if entry.value == 0)

        values = []
        entries_iter = self.cycle(zero)
        for n in range(0, 3001):
            entry = next(entries_iter)
            if n % 1000 == 0:
                values.append(entry.value)

        print(values)
        print(sum(values))

        

Day().execute()
# Day(f'day_{Day.day}_test.txt').execute()

# [0, 4566000574778, -6646915163070, -4674753521280]  -6755668109572    - no
