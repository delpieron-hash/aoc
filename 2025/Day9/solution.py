"""
Advent of Code 2025
Day 9

Full problem: https://adventofcode.com/2025/day/9

A:

B:
"""

import itertools
import re
from collections.abc import Iterator
from pathlib import Path

from attrs import define

INPUT_FILE = "input.txt"
TEST_INPUT_FILE = "test_input.txt"

POINT_PATTERN = re.compile(r"(\d+),(\d+)", re.NOFLAG)


@define
class Point:
    x: int
    y: int

    @classmethod
    def from_line(cls, input_line: str) -> "Point":
        if match := POINT_PATTERN.search(input_line):
            x, y = map(int, match.group(1, 2))
            return cls(x, y)

        raise ValueError("Unexpected input.")


def read_input_lines(input_path: Path) -> Iterator[Point]:
    """
    Extracts all non-empty lines line by line from the provided file input.

    Args:
        input_path (Path): Path to the file input to read.

    Yields:
        Point: Parsed junction box point item.
    """
    with open(input_path, mode="r") as f:
        yield from (Point.from_line(line.strip()) for line in f if line.strip())


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

    points = read_input_lines(input_path)

    largest_rectangle = 0
    for point_a, point_b in itertools.combinations(points, 2):
        rectangle_area = (abs(point_a.x - point_b.x) + 1) * (
            abs(point_a.y - point_b.y) + 1
        )
        if rectangle_area > largest_rectangle:
            largest_rectangle = rectangle_area

    print(f"Problem 1: {largest_rectangle}")

    print("Problem 2: ")


if __name__ == "__main__":
    main(False)
