"""
Advent of Code 2025
Day 8

Full problem: https://adventofcode.com/2025/day/8

A:

B:
"""

import heapq
import itertools
import math
import re
from collections.abc import Iterator
from pathlib import Path

from attrs import define, field

INPUT_FILE = "input.txt"
TEST_INPUT_FILE = "test_input.txt"

COORDINATES_PATTERN = re.compile(r"(\d+),(\d+),(\d+)", re.NOFLAG)


@define(eq=False)
class Point:
    unique_id: int = field(eq=True)

    x: int
    y: int
    z: int

    circuit_id: int | None = None

    @classmethod
    def from_line(cls, idx: int, input_line: str) -> "Point":
        if match := COORDINATES_PATTERN.search(input_line):
            x, y, z = map(int, match.group(1, 2, 3))
            return cls(idx, x, y, z)

        raise ValueError(
            "Unexpected input format. A new JunctionBox cannot be constructed."
        )


next_circuit_id = itertools.count(1)


@define
class Circuit:
    unique_id: int
    length: int
    points: set[Point]

    def add_point(self, point: Point) -> None:
        point.circuit_id = self.unique_id
        self.points.add(point)
        self.length += 1

    def add_points(self, points: set[Point]) -> None:
        for point in points:
            point.circuit_id = self.unique_id
            self.points.add(point)
            self.length += 1


@define
class Graph:
    points: dict[int, Point]
    limit: int

    distances_pq: list[tuple[int, tuple[int, int]]] = field(factory=list)
    circuits: dict[int, Circuit] = field(factory=dict)

    def __attrs_post_init__(self) -> None:
        push = heapq.heappush_max
        pushpop = heapq.heappushpop_max
        size = 0

        for point_a, point_b in itertools.combinations(self.points.values(), 2):
            distance_3D = (
                (point_a.x - point_b.x) ** 2
                + (point_a.y - point_b.y) ** 2
                + (point_a.z - point_b.z) ** 2
            )
            distance = (
                distance_3D,
                (point_a.unique_id, point_b.unique_id),
            )

            if size < self.limit:
                push(self.distances_pq, distance)
                size += 1
            else:
                pushpop(self.distances_pq, distance)

        heapq.heapify(self.distances_pq)

    def connect_shortest_edge(self) -> tuple[Point, Point] | None:
        id_a, id_b = heapq.heappop(self.distances_pq)[1]

        point_a = self.points[id_a]
        point_b = self.points[id_b]

        circuit_id_a = point_a.circuit_id
        circuit_id_b = point_b.circuit_id

        if circuit_id_a and circuit_id_b:
            if circuit_id_a == circuit_id_b:
                return
            removed_circuit_b = self.circuits.pop(circuit_id_b)
            self.circuits[circuit_id_a].add_points(removed_circuit_b.points)

        elif circuit_id_a and not circuit_id_b:
            self.circuits[circuit_id_a].add_point(point_b)

        elif circuit_id_b and not circuit_id_a:
            self.circuits[circuit_id_b].add_point(point_a)

        else:
            new_id = next(next_circuit_id)
            point_a.circuit_id = new_id
            point_b.circuit_id = new_id
            self.circuits[new_id] = Circuit(new_id, 2, set((point_a, point_b)))

        return (point_a, point_b)

    def connect_all(self) -> tuple[Point, Point]:
        while True:
            if last_connected := self.connect_shortest_edge():
                if self.is_one_circuit:
                    return last_connected

    def get_top_circuit_lengths(self, n: int) -> list[int]:
        top_n_circuits = sorted(
            self.circuits.values(), key=lambda x: x.length, reverse=True
        )[:n]
        return [circuit.length for circuit in top_n_circuits]

    @property
    def is_one_circuit(self) -> bool:
        if len(self.circuits) != 1:
            return False

        return next(iter(self.circuits.values())).length == len(self.points)


def read_input_lines(input_path: Path) -> Iterator[Point]:
    """
    Extracts all non-empty lines line by line from the provided file input.

    Args:
        input_path (Path): Path to the file input to read.

    Yields:
        Point: Parsed junction box point item.
    """
    with open(input_path, mode="r") as f:
        yield from (
            Point.from_line(idx, line.strip())
            for idx, line in enumerate(f)
            if line.strip()
        )


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

    graph = Graph({point.unique_id: point for point in points}, 5000)

    connection_limit = 10 if test else 1000
    for _ in range(connection_limit):
        graph.connect_shortest_edge()

    top_lengths = graph.get_top_circuit_lengths(3)

    last_connected = graph.connect_all()

    print(f"Problem 1: {math.prod(top_lengths)}")

    print(f"Problem 2: {last_connected[0].x * last_connected[1].x}")


if __name__ == "__main__":
    main(False)
