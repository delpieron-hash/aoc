"""
Advent of Code 2024
Day 4

A: Count the number of times XMAS appears in the word map 
    in horizontal, vertical, and diagonal directions

B: Count the number of times an X shape of MAS appears in the word map
"""

from collections.abc import Iterator
from pathlib import Path

from attrs import define

INPUT_FILE = "input_day4_aoc2024.txt"


def read_input(filename: str | None = None) -> list[list[str]]:
    """
    Read full input from file into a 2d array

    Args:
        filename (str | None): Name of file to read from

    Returns:
        list[list[str]]: List of lists of strings
    """
    input_name = filename or INPUT_FILE
    input_src = Path(Path(__file__).parent / input_name)

    with open(input_src, "r") as f:
        return [list(line.strip()) for line in f]


@define
class CharPoint:
    """
    A class to represent a character with coordinates on a word map

    Attributes:
        value (str): The character
        y (int): The y coordinate
        x (int): The x coordinate
    """

    value: str
    y: int
    x: int


class WordMap:

    def __init__(self, word_map: list[list[str]]) -> None:
        self.map = word_map
        self.width = len(word_map[0])
        self.height = len(word_map)

    def traverse_map(self) -> Iterator[CharPoint]:
        """
        Iterate over the map and yield each character with its coordinates

        Args:
            None

        Yields:
            CharPoint: A character with its coordinates
        """

        for y, row in enumerate(self.map):
            for x, char in enumerate(row):
                yield CharPoint(char, y, x)

    def adjacent_points(self, point: CharPoint) -> list[CharPoint]:
        """
        Return the points adjacent to a given char in the word map

        Args:
            point (CharPoint): The character to generate adjacent points for

        Returns:
            list[CharPoint]: List of adjacent points
        """
        adjacent_points = []

        for x in (point.x - 1, point.x, point.x + 1):
            for y in (point.y - 1, point.y, point.y + 1):
                if not self.is_valid_point(y, x):
                    continue

                if (x, y) != (point.x, point.y):
                    adjacent_points.append(CharPoint(self.map[y][x], y, x))

        return adjacent_points

    def diagonal_points(self, point: CharPoint) -> list[CharPoint] | None:
        """
        Return the 4 points diagonal to a given char in the word map

        Args:
            point (CharPoint): The character to generate diagonal points for

        Returns:
            list[CharPoint] | None:
                List of 4 diagonal points or
                None if any diagonal point would be out of bounds
        """
        diagonal_points = []

        for x in (point.x - 1, point.x + 1):
            for y in (point.y - 1, point.y + 1):
                if self.is_valid_point(y, x):
                    diagonal_points.append(CharPoint(self.map[y][x], y, x))

        if len(diagonal_points) == 4:
            return diagonal_points

    def is_valid_point(self, y: int, x: int) -> bool:
        """
        Check if given coordinates point to a valid point in the word map

        Args:
            y (int): The y coordinate
            x (int): The x coordinate

        Returns:
            bool: True if the point is valid, False otherwise
        """
        return 0 <= x < self.width and 0 <= y < self.height

    def calc_direction(self, first: CharPoint, second: CharPoint) -> tuple[int, int]:
        """
        Calculate the direction from first to second point in the word map

        Args:
            first (CharPoint): The first character
            second (CharPoint): The second character

        Returns:
            tuple[int, int]: The direction from first to second
        """
        return second.y - first.y, second.x - first.x

    def step_in_direction(
        self, point: CharPoint, direction: tuple[int, int]
    ) -> CharPoint:
        """
        Step in a given direction from a point in the word map

        Args:
            point (CharPoint): The character to step from
            direction (tuple[int, int]): The direction to step in

        Returns:
            CharPoint: The character at the new point
        """
        new_y = point.y + direction[0]
        new_x = point.x + direction[1]

        if not self.is_valid_point(new_y, new_x):
            raise ValueError("Coordinates are out of bounds")

        return CharPoint(self.map[new_y][new_x], new_y, new_x)

    def print_map(self) -> None:
        """
        Prints the word map to the console.

        Args:
            None

        Returns:
            None
        """
        for row in self.map:
            print("".join(row))

    def count_xmas(self) -> int:
        """
        Count the number of times an XMAS text appears in any direction in the word map

        Returns:
            int: The number of times an XMAS text appears
        """
        count = 0
        for first in self.traverse_map():

            if first.value != "X":
                continue

            for second in self.adjacent_points(first):

                if second.value != "M":
                    continue

                direction = self.calc_direction(first, second)

                try:
                    third = self.step_in_direction(second, direction)
                    if third.value != "A":
                        continue
                except ValueError:
                    continue

                try:
                    fourth = self.step_in_direction(third, direction)
                    if fourth.value != "S":
                        continue
                except ValueError:
                    continue

                count += 1

        return count

    def count_x_shape_mas(self) -> int:
        """
        Count the A characters that are part of two diagonal MAS texts in the word map

        Returns:
            int: The number of times an X shape of MAS appears
        """
        count = 0
        for middle in self.traverse_map():
            if middle.value != "A":
                continue

            if diagonal_points := self.diagonal_points(middle):
                values = [p.value for p in diagonal_points]
                if values.count("M") != 2 or values.count("S") != 2:
                    continue

                ordered_points = sorted(diagonal_points, key=lambda p: (p.y, p.x))
                # First - last and middle points must be different if ordered
                if (
                    ordered_points[0].value != ordered_points[3].value
                    and ordered_points[1].value != ordered_points[2].value
                ):
                    count += 1

        return count


def main() -> None:
    """
    Main entry point for the script

    Reads the input from a file, processes data and prints the solution to
    both parts of the problem.

    Returns:
        None
    """
    word_map = WordMap(read_input())

    xmas_count = word_map.count_xmas()
    print(f"Problem 1: {xmas_count}")

    x_mas_count = word_map.count_x_shape_mas()
    print(f"Problem 2: {x_mas_count}")


if __name__ == "__main__":
    main()
