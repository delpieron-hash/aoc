"""
Advent of Code 2025
Day 11

Full problem: https://adventofcode.com/2025/day/11

A:

B:.
"""

import re
from collections import defaultdict
from collections.abc import Iterable, Iterator
from pathlib import Path

from attrs import define

INPUT_FILE = "input.txt"
TEST_INPUT_FILE = "test_input.txt"

NODE_PATTERN = re.compile(r"(?P<name>\w+):(?P<outs>[a-z ]+)", re.NOFLAG)


@define
class Graph:
    nodes: dict[str, list[str]]

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> "Graph":
        nodes: dict[str, list[str]] = {}
        for line in lines:
            if match := NODE_PATTERN.match(line):
                name, outs = match.group("name", "outs")
                nodes[name] = [out.strip() for out in outs.strip().split()]

        return cls(nodes)

    def find_in_levels(self, start: str, target: str) -> int:
        all_counts: dict[str, int] = defaultdict(int)
        counts = {start: 1}
        while counts:
            counts = self.find_in_level(counts)

            for node, count in counts.items():
                all_counts[node] += count

        return all_counts.get(target, 0)

    def find_in_level(self, current_level: dict[str, int]):
        next_level: dict[str, int] = defaultdict(int)

        for branch, count in current_level.items():
            if branch not in self.nodes:
                continue

            for node in self.nodes[branch]:
                next_level[node] += count

        return next_level

    def find_paths(
        self, start: str, end: str, avoid: Iterable[str] | None = None
    ) -> int:
        avoid = set(avoid) if avoid else set()
        return self.find_out(start, end, set(), avoid)

    def find_out(
        self,
        current: str,
        target: str,
        visited: set[str],
        avoid: set[str] | None = None,
    ) -> int:
        if current in visited or (avoid and current in avoid):
            return 0

        if current == target:
            return 1

        visited = visited | {current}

        count = 0
        for next_node in self.nodes[current]:
            count += self.find_out(next_node, target, visited, avoid)

        return count


def read_lines(input_path: Path) -> Iterator[str]:
    """
    Yields the input file line by line on each non-empty line.

    Args:
        input_path (Path): Path to the input file to read.

    Yields:
        str: Line string read from the file input
    """
    with open(input_path, mode="r") as f:
        yield from (line.strip() for line in f if line.strip())


def main(test: bool = False) -> None:
    """
    Main entry point for the script.

    Reads the input from a file, calculates and prints the solution
    to both parts of the problem.

    Args:
        test (bool): Determines if the script should be run on test input.
            By default it is false, and the production input is used.

    Returns:
        None
    """
    input_path = Path(__file__).parent / (TEST_INPUT_FILE if test else INPUT_FILE)

    graph = Graph.from_lines(read_lines(input_path))

    p1 = graph.find_paths("you", "out")

    one_way = (
        graph.find_in_levels("svr", "fft")
        * graph.find_in_levels("fft", "dac")
        * graph.find_in_levels("dac", "out")
    )
    another_way = (
        graph.find_in_levels("svr", "dac")
        * graph.find_in_levels("dac", "fft")
        * graph.find_in_levels("fft", "out")
    )

    print(f"Problem 1: {p1}")

    print(f"Problem 2: {one_way + another_way}")


if __name__ == "__main__":
    main(False)
