"""
Advent of Code 2025
Day 8

Full problem: https://adventofcode.com/2025/day/8

A: Make 1000 attempts to connect two junction boxes (points) with wires (edges)
in 3D space. Start with the two that are closest together, and continue in an order of
ascending distances between connectable boxes. Find the 3 circuits (graphs) that contain
the most amount of junction boxes. Calculate the product of the size of these circuits.

B: Find the two junction boxes that will connect all the junction box points
of the 3D space into one single circuit if connection attempts in an ascending order
defined by their distance continues. Calculate the product of their X coordinates.
"""

import heapq
import itertools
import math
import re
from collections.abc import Iterable, Iterator
from pathlib import Path

from attrs import define, field

INPUT_FILE = "input.txt"
TEST_INPUT_FILE = "test_input.txt"

COORDINATES_PATTERN = re.compile(r"(\d+),(\d+),(\d+)", re.NOFLAG)

next_junction_box_id = itertools.count(1)
next_circuit_id = itertools.count(1)


@define(eq=False)
class JunctionBox:
    """
    A point of 3D space representing single circuits that can be joined by wires
    to form a larger connected circuit.

    Attributes:
        x (int):
            Coordinate in 3D space along X axis.
        y (int):
            Coordinate in 3D space along Y axis.
        z (int):
            Coordinate in 3D space along Z axis.
        unique_id (int):
            Number uniquely identifying this specific JunctionBox instance. By default
            gets a value from an infinite incrementing counter starting from 1.
        circuit_id (int | None):
            Number identifying the circuit this instance belongs to. An item with
            no connections yet is handled as having no circuit_id. By default None.
    """

    x: int
    y: int
    z: int

    unique_id: int = field(eq=True, factory=lambda: next(next_junction_box_id))
    circuit_id: int | None = None

    @classmethod
    def from_line(cls, input_line: str) -> "JunctionBox":
        """
        Create a JunctionBox instance based on the 3 dimensional coordinates
        included in the provided line input.

        Args:
            input_line (str): Line string containing the x,y and z coordinates.

        Returns:
            JunctionBox: Created JunctionBox instance.

        Raises:
            ValueError: If the input does not include the x, y and z coordinates
                in the expected pattern.
        """
        if match := COORDINATES_PATTERN.search(input_line):
            x, y, z = map(int, match.group(1, 2, 3))
            return cls(x, y, z)

        raise ValueError("Unexpected input format. Cannot construct JunctionBox.")


@define
class Circuit:
    """
    A graph in 3D space representing multi-item circuits that are connected by wire
    edges from single JunctionBox circuit points.

    Attributes:
        unique_id (int):
            Number uniquely identifying this specific Circuit instance.
        points (set[JunctionBox]):
            Set of JunctionBox points that are connected and belong in this Circuit.
        size (int):
            Number of JunctionBox points forming part of this Circuit instance.
    """

    unique_id: int
    points: set[JunctionBox]
    size: int

    def add_point(self, point: JunctionBox) -> None:
        """
        Joins a JunctionBox to this circuit item by assiging the circuit's id to
        the JunctionBox, adding the JunctionBox to the point set of this circuit
        and incrementing the size counter accordingly.

        Args:
            point (JunctionBox): JunctionBox instance to join to this circuit.

        Returns:
            None
        """
        point.circuit_id = self.unique_id
        self.points.add(point)
        self.size += 1

    def add_points(self, points: Iterable[JunctionBox]) -> None:
        """
        Joins an iterable set of JunctionBox items to this circuit item by
        individually assiging the circuit's id to all JunctionBoxes, adding them to
        the point set of this circuit and incrementing the size counter accordingly.

        Args:
            points (Iterable[JunctionBox]): Iterable set of JunctionBox instances
                to join to this circuit.

        Returns:
            None
        """
        for point in points:
            point.circuit_id = self.unique_id
            self.points.add(point)
            self.size += 1


@define
class ConnectionManager:
    """
    Manager class for the 3D space of JunctionBoxes and Circuits.

    Attributes:
        points (dict[int, JunctionBox]):
            Mapping of unique id numbers to the corresponding JunctionBox items.
        limit (int):
            Maximum number of shortest distances stored by this manager class.
        distances_pq (list[tuple[int, tuple[int, int]]]):
            Minimum priority queue of distances between the stored JunctionBox items.
            Each distance is stored as a tuple of the distance value and the unique
            id numbers of the respective two JunctionBox items.
        circuits (dict[int, Circuit]):
            Mapping of unique id numbers to the corresponding Circuit items.
    """

    points: dict[int, JunctionBox]
    limit: int

    distances_pq: list[tuple[int, tuple[int, int]]] = field(factory=list)  # pyright: ignore[reportUnknownVariableType]
    circuits: dict[int, Circuit] = field(factory=dict)  # pyright: ignore[reportUnknownVariableType]

    def __attrs_post_init__(self) -> None:
        """
        Initializes the minimum distances priority queue based on the provided points.

        Calculates the distances between any combinations of the JunctionBox points by
        keeping the N shortest of them using a maximum priority queue, where N is the
        limit value. After all combinations are evaluated the distances are reordered as
        a minimum priority queue.

        Runs only once upon initialization.

        Returns:
            None
        """
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

    @property
    def is_one_circuit(self) -> bool:
        """
        Determines whether all JunctionBox points of the 3D space form part of
        one single Circuit graph.

        Returns:
            bool: True if all JunctionBoxes are connected, otherwise False.
        """
        if len(self.circuits) != 1:
            return False

        return next(iter(self.circuits.values())).size == len(self.points)

    def connect_shortest_edge(self) -> tuple[JunctionBox, JunctionBox] | None:
        """
        Finds the two JunctionBox items defined by the shortest unused distance,
        attempts to connect them and returns them if the attempt was successful.

        A connection between two JunctionBox points means that all other JunctionBox
        points that were already connected to any of the JunctionBox points will
        also form part of the same Circuit afterwards.

        Returns:
            tuple[JunctionBox, JunctionBox] | None: Tuple of connected JunctionBoxes
                or None if the connection attempt was aborted.
        """
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
            self.circuits[new_id] = Circuit(new_id, set((point_a, point_b)), 2)

        return (point_a, point_b)

    def connect_all(self) -> tuple[JunctionBox, JunctionBox]:
        """
        Connects the JunctionBox items of the 3D space until all items form part of
        one single circuit. Returns the last connected pair of JunctionBoxes.

        Returns:
            tuple[JunctionBox, JunctionBox]: Tuple containing the two JunctionBox items
                that were last successfully connected.
        """
        while True:
            if last_connected := self.connect_shortest_edge():
                if self.is_one_circuit:
                    return last_connected

    def get_top_circuit_sizes(self, n: int) -> list[int]:
        """
        Filters the top n largest circuits and returns their sizes as a list.

        Args:
            n (int): Number of circuits to filter for.

        Returns:
            list[int]: Size of n largest circuits as a list of integers.
        """
        top_n_circuits = sorted(
            self.circuits.values(), key=lambda x: x.size, reverse=True
        )[:n]
        return [circuit.size for circuit in top_n_circuits]


def read_input_lines(input_path: Path) -> Iterator[JunctionBox]:
    """
    Extracts all items line by line from the non-empty lines of the provided file.

    Args:
        input_path (Path): Path to the file input to read.

    Yields:
        JunctionBox: JunctionBox point instance parsed from the input.
    """
    with open(input_path, mode="r") as f:
        yield from (JunctionBox.from_line(line.strip()) for line in f if line.strip())


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

    manager = ConnectionManager({point.unique_id: point for point in points}, 5000)

    connection_limit = 10 if test else 1000
    for _ in range(connection_limit):
        manager.connect_shortest_edge()

    top_lengths = manager.get_top_circuit_sizes(3)

    last_connected = manager.connect_all()

    print(f"Problem 1: {math.prod(top_lengths)}")

    print(f"Problem 2: {last_connected[0].x * last_connected[1].x}")


if __name__ == "__main__":
    main(False)
