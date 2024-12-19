"""
Advent of Code 2024
Day 14

Full problem: https://adventofcode.com/2024/day/14

A: Calculate the product of the number of robots in each quadrant after 100 seconds

B: Find the least amount of seconds it takes for the robots to form 
a picture of a Christmas tree.
"""

import math
import re
import typing
from pathlib import Path

from attrs import define

INPUT_FILE = "input_day14_aoc2024.txt"
TEST_INPUT_FILE = "test_input_day14_aoc2024.txt"
OUTPUT_FILE = "output_day14_aoc2024.txt"
TEST_OUTPUT_FILE = "test_output_day14_aoc2024.txt"


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


@define
class Area:
    """
    A 2D area with a width and height.
    """

    width: int
    height: int

    def convert_position(self, x: int, y: int) -> tuple[int, int]:
        """
        Convert given coordinates to a point within the bounds of the map.

        This is done by taking the modulus of the coordinates with the width and height
        of the map.

        Args:
            x (int): The x coordinate
            y (int): The y coordinate

        Returns:
            tuple[int, int]: The converted coordinates
        """
        return (x % self.width, y % self.height)

    def quadrant_positions(self, positions: list[tuple[int, int]]) -> dict[int, int]:
        """
        Count the number of positions falling into each of the four quadrants.

        The quadrants are determined by splitting the area into four regions
        using the midpoint of the width and height. The quadrants are numbered
        1, 2, 3, and 4 from top left to bottom right.

        Args:
            positions (list[tuple[int, int]]): A list of (x, y) coordinates.

        Returns:
            dict[int, int]: A dictionary mapping quadrant numbers to the
                number of positions in that quadrant
        """
        v_middle = self.width // 2
        h_middle = self.height // 2

        quadrants = {0: 0, 1: 0, 2: 0, 3: 0}

        for position in positions:
            if position[0] < v_middle:
                if position[1] < h_middle:
                    quadrants[0] += 1
                elif position[1] > h_middle:
                    quadrants[1] += 1
            elif position[0] > v_middle:
                if position[1] < h_middle:
                    quadrants[2] += 1
                elif position[1] > h_middle:
                    quadrants[3] += 1

        return quadrants

    def print_map(self, positions: list[tuple[int, int]]) -> None:
        """
        Print the positions as a 2D map to the console.

        The positions are represented as "#" characters, while the rest of the map is
        represented as ".".

        Args:
            positions (list[tuple[int, int]]): A list of positions to print on the map.
        """
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in positions:
                    print("#", end="")
                else:
                    print(".", end="")
            print("\n", end="")


@define
class Robot:
    """
    Represents a robot with a position and a velocity.

    The position and velocity are represented as tuples of two integers each,
    representing the x and y coordinates.

    The class also has a class variable `pattern` which is a regular expression
    pattern that can be used to parse a string representation of a robot.

    The string representation of a robot is expected to be in the format
    "p=<x>,<y> v=<vx>,<vy>".
    """

    pattern: typing.ClassVar = re.compile(r"p\=(-?\d+),(-?\d+)\s+v\=(-?\d+),(-?\d+)")
    position: tuple[int, int]
    velocity: tuple[int, int]

    @classmethod
    def from_text(cls, text: str) -> "Robot":
        """
        Create a Robot instance from a text string.

        The text string should be a space-separated list of four integers, where
        the first two integers represent the x and y coordinates of the position
        and the second two integers represent the x and y components of the
        velocity.

        Args:
            text (str): The text string to create the Robot from

        Returns:
            Robot: The created Robot instance
        """
        if (match := re.match(cls.pattern, text)) is None:
            raise ValueError("No match for robot pattern")

        if len(values := match.groups()) != 4:
            raise ValueError("Robot score pattern has incorrect number of groups")

        return cls(
            position=(int(values[0]), int(values[1])),
            velocity=(int(values[2]), int(values[3])),
        )

    def move_until(self, seconds: int) -> tuple[int, int]:
        """
        Move the robot to a new position after a given number of seconds.

        The new position is calculated by adding the product of velocity
        and time to the initial position for both x and y coordinates.

        Args:
            seconds (int): The number of seconds to move the robot.

        Returns:
            tuple[int, int]: The new (x, y) position of the robot.
        """
        return (
            self.position[0] + self.velocity[0] * seconds,
            self.position[1] + self.velocity[1] * seconds,
        )


def main() -> None:
    """
    Main entry point for the script

    Reads the input from a file, processes data and prints the solution to
    both parts of the problem.

    Returns:
        None
    """
    test = False

    if test:
        area = Area(width=11, height=7)
    else:
        area = Area(width=101, height=103)

    txt_input = read_input(test).strip()

    robots = [Robot.from_text(line) for line in txt_input.splitlines(keepends=False)]
    positions_100s = [area.convert_position(*r.move_until(100)) for r in robots]
    quadrants = area.quadrant_positions(positions_100s)
    print(f"Problem 1: {math.prod(quadrants.values())}")

    ## Look for a pattern in robot positions
    # for i in range(1, 1000):
    #     print(f"\n{i} seconds \n")
    #     positions_i = [area.convert_position(*r.move_until(i)) for r in robots]
    #     area.print_map(positions_i)

    ## Search the pattern at every 101th sec for tree
    # for i in range(97, 10000, 101):
    #     print(f"\n{i} seconds \n")
    #     positions_i = [area.convert_position(*r.move_until(i)) for r in robots]
    #     area.print_map(positions_i)

    ## Print christmas tree
    # position_x_seconds = [area.convert_position(*r.move_until(7672)) for r in robots]
    # area.print_map(position_x_seconds)

    print(f"Problem 2: 7672")


if __name__ == "__main__":
    main()
