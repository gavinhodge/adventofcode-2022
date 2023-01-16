from dataclasses import dataclass
from typing import Optional
from base import BaseDay


@dataclass
class File:
    name: str
    size: int
    parent_dir: 'Directory'

    def __repr__(self) -> str:
        return ' ' * ((self.parent_dir.depth + 1) * 2) + f'- {self.name} (file, size={self.size})\n'

@dataclass
class Directory:
    name: str
    parent: Optional['Directory']
    dirs: list['Directory']
    files: list['File']
    depth: int

    def mk_dir(self, name: str) -> 'Directory':
        # New dir (if not exists)
        try:
            directory = next(d for d in self.dirs if d.name == name)
        except StopIteration:
            directory = Directory(name, self, [], [], self.depth + 1)
            self.dirs.append(directory)
        return directory

    def mk_file(self, name: str, size: int) -> File:
        try:
            file = next(file for file in self.files if file.name == name)
        except StopIteration:
            file = File(name, size, self)
            self.files.append(file)
        return file
        

    def size_recursive(self) -> int:
        total = sum(file.size for file in self.files)

        for d in self.dirs:
            total += d.size_recursive()

        return total

    def all_dirs(self) -> list['Directory']:
        all_dirs = [self]

        for d in self.dirs:
            all_dirs.extend(d.all_dirs())
        
        return all_dirs

    def __repr__(self) -> str:
        result = ' ' * (self.depth * 2) + f'- {self.name} (dir)\n'

        for d in self.dirs:
            result += repr(d)

        for file in self.files:
            result += repr(file)

        return result

class Day(BaseDay):
    day = 7

    def load_filesystem(self) -> Directory:
        root_dir: Directory = Directory('/', None, [], [], 0)
        current_dir = root_dir

        for line in self.data_lines:
            if line.startswith('$ cd'):
                name = line.replace('$ cd ', '')
                if name == '/':
                    current_dir = root_dir
                elif name == '..':
                    current_dir = current_dir.parent
                else:
                    current_dir = current_dir.mk_dir(name)

            elif line.startswith('$ ls'):
                pass
            elif line.startswith('dir '):
                name = line.replace('dir ', '')
                current_dir.mk_dir(name)
            else:
                # File
                size, name = line.split(' ')
                current_dir.mk_file(name, int(size))

        return root_dir

    def part_1(self):
        root_dir = self.load_filesystem()
        total = 0
        for dir in root_dir.all_dirs():
            size = dir.size_recursive()
            if size < 100000:
                total += size

        print(total)

    def part_2(self):
        TOTAL_SPACE = 70000000
        NEEDED_SPACE = 30000000

        root_dir = self.load_filesystem()
        free_space = TOTAL_SPACE - root_dir.size_recursive()
        gap = NEEDED_SPACE - free_space
        results = [(dir, dir.size_recursive()) for dir in root_dir.all_dirs()]
        results = [r for r in results if r[1] >= gap]
        results.sort(key=lambda r: r[1])
        print(results[0][1])

Day().execute()
