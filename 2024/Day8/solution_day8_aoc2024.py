"""
Advent of Code 2024
Day 8

Full problem: https://adventofcode.com/2024/day/8

A: Count the number of equal distance antinodes created by same frequency antenna pairs

B: Count the number of all antinodes created in line by same frequency antenna pairs
"""

from itertools import combinations
from pathlib import Path

from attrs import define

INPUT_FILE = "input_day8_aoc2024.txt"
TEST_INPUT_FILE = "test_input_day8_aoc2024.txt"
OUTPUT_FILE = "output_day8_aoc2024.txt"
TEST_OUTPUT_FILE = "test_output_day8_aoc2024.txt"


def read_input(test: bool = False) -> str:
    """
    Read full input from file

    Args:
        test (bool): Whether to use the test input

    Returns:
        str: Full input text
    """
    input_name = TEST_INPUT_FILE if test else INPUT_FILE
    input_src = Path(Path(__file__).parent / input_name)

    with open(input_src, "r") as f:
        return f.read()


class Colors:
    """
    ANSI color codes for printing colored text in terminal

    Contains methods to wrap a given string in ANSI color codes.
    """

    GREEN = "\033[0;32m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    BOLD = "\033[1m"
    END = "\033[0m"

    @classmethod
    def purple(cls, char: str) -> str:
        """Wrap a string in purple color"""
        return f"{cls.PURPLE}{char}{cls.END}"

    @classmethod
    def green(cls, char: str) -> str:
        """Wrap a string in green color"""
        return f"{cls.GREEN}{char}{cls.END}"

    @classmethod
    def cyan(cls, char: str) -> str:
        """Wrap a string in cyan color"""
        return f"{cls.CYAN}{char}{cls.END}"

    @classmethod
    def bold(cls, char: str) -> str:
        """Wrap a string in bold font"""
        return f"{cls.BOLD}{char}{cls.END}"


@define
class Antenna:
    name: str


@define
class Node:
    y: int
    x: int
    value: Antenna | None


class CityMap:

    def __init__(self, city_map: str) -> None:
        """
        Initialize a CityMap instance from a string of text

        Args:
            city_map (str): City map text

        Returns:
            None
        """
        self.city_map = CityMap.process_city_map(city_map)
        self.height = len(self.city_map)
        self.width = len(self.city_map[0])

        self.antennas = self.collect_antennas()
        self.v1_antinodes = self.v1_calculate_antinodes()
        self.v2_antinodes = self.v2_calculate_antinodes()

    @staticmethod
    def process_city_map(city_map: str) -> list[list[Node]]:
        """
        Process a city map into a 2D array of nodes

        Args:
            city_map (str): City map text

        Returns:
            list[list[Node]]: 2D array of nodes
        """
        node_map = []
        for y, line in enumerate(city_map.splitlines(keepends=False)):
            node_map.append([])
            for x, char in enumerate(line):
                if char == ".":
                    node_map[y].append(Node(y, x, None))
                elif char.isalnum():
                    node_map[y].append(Node(y, x, Antenna(char)))
                else:
                    raise ValueError(f"Invalid character: {char}")

        return node_map

    def print_map(self, version: int = 1) -> None:
        """
        Prints the city map to the console

        Args:
            version (int): Version of the map

        Returns:
            None
        """
        antinodes = self.v1_antinodes if version == 1 else self.v2_antinodes

        for y, line in enumerate(self.city_map):
            for x, char in enumerate(line):
                if isinstance(char.value, Antenna):
                    print(Colors.green(Colors.bold(char.value.name)), end="")
                elif (y, x) in antinodes:
                    print(Colors.purple("X"), end="")
                else:
                    print(Colors.cyan("."), end="")
            print("\n", end="")

    def is_valid_point(self, y: float, x: float) -> bool:
        """
        Check if given coordinates point to a valid point of the map

        Args:
            y (float): The y coordinate
            x (float): The x coordinate

        Returns:
            bool: True if the point is valid, False otherwise
        """
        return int(y) == round(y, 5) and int(x) == round(x, 5)

    def is_within_map(self, y: float, x: float) -> bool:
        """
        Check if given coordinates point to within the map

        Args:
            y (float): The y coordinate
            x (float): The x coordinate

        Returns:
            bool: True if the point is valid, False otherwise
        """
        return 0 <= x < self.width and 0 <= y < self.height

    def collect_antennas(self) -> dict[str, list[Node]]:
        """
        Process a city map and collect antennas of any frequency

        Args:
            city_map (str): City map text

        Returns:
            dict[str, list[Node]]: Antennas of any frequency
        """
        antennas = {}
        for line in self.city_map:
            for node in line:
                if isinstance(node.value, Antenna):
                    if node.value.name in antennas:
                        antennas[node.value.name] += [node]
                    else:
                        antennas[node.value.name] = [node]

        return antennas

    def v1_calculate_antinodes(self) -> set[tuple[int, int]]:
        """
        Collect antinodes created by equally spaced same frequency antenna pairs

        Args:
            city_map (str): City map text

        Returns:
            set[tuple[int, int]]: Set of y, x coordinates of antinodes
        """
        antinodes = set()
        for antenna in self.antennas:
            antenna_nodes = self.antennas[antenna]
            for a1, a2 in combinations(antenna_nodes, 2):
                distance = (a2.y - a1.y, a2.x - a1.x)
                antinode1 = (a1.y - distance[0], a1.x - distance[1])
                antinode2 = (a2.y + distance[0], a2.x + distance[1])

                for antinode in (antinode1, antinode2):
                    if self.is_within_map(antinode[0], antinode[1]):
                        antinodes.add(antinode)

        return antinodes

    def v2_calculate_antinodes(self) -> set[tuple[int, int]]:
        """
        Collect antinodes created by any same frequency antenna pair lines

        Args:
            city_map (str): City map text

        Returns:
            set[tuple[int, int]]: Set of y, x coordinates of antinodes
        """
        antinodes = set()
        for antenna in self.antennas:
            antenna_nodes = self.antennas[antenna]
            for a1, a2 in combinations(antenna_nodes, 2):

                dy, dx = a2.y - a1.y, a2.x - a1.x
                points: list[tuple[int, int]] = []

                if a1.x == a2.x:
                    points += [(i, a1.x) for i in range(self.height + 1)]

                for i in range(self.width - a2.x + 1):
                    x = a2.x + i
                    y = a2.y + i * dy / dx
                    if not self.is_within_map(y, x):
                        break
                    if self.is_valid_point(y, x):
                        points.append((int(y), int(x)))

                for j in range(a1.x + 1):
                    x = a1.x - j
                    y = a1.y - j * dy / dx
                    if not self.is_within_map(y, x):
                        break
                    if self.is_valid_point(y, x):
                        points.append((int(y), int(x)))

                antinodes.update(points)

        return antinodes


def main() -> None:
    """
    Main entry point for the script

    Reads the input from a file, processes data and prints the solution to
    both parts of the problem.

    Returns:
        None
    """
    txt_input = read_input(False)

    city_map = CityMap(txt_input)

    print(f"Problem 1: {len(city_map.v1_antinodes)}")

    print(f"Problem 2: {len(city_map.v2_antinodes)}")


if __name__ == "__main__":
    main()
