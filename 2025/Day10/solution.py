"""
Advent of Code 2025
Day 10

Full problem: https://adventofcode.com/2025/day/10

A:

B:.
"""

import itertools
import re
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Literal

from attrs import define, field

INPUT_FILE = "input.txt"
TEST_INPUT_FILE = "test_input.txt"

MACHINE_PATTERN = re.compile(
    r"(?P<lights>\[[.#]+\])(?P<buttons>.*)(?P<joltages>{[0-9,]+})", re.NOFLAG
)

item_counter = itertools.count(1)


def print_lights(states: list[bool]) -> None:
    print("".join(["#" if state else "." for state in states]))


@define
class LightDiagram:
    """
    Represents a set of lights in order with each in an on or off state.

    Attributes:
        ...
    """

    target: list[bool]
    target_value: int

    @classmethod
    def from_line(cls, light_map: str) -> "LightDiagram":
        """
        Returns:
            LightDiagram:
        """
        target_map = [state == "#" for state in light_map]
        target_value = 0
        for idx, position in enumerate(target_map[::-1]):
            if position:
                target_value += 2**idx
        return cls(target_map, target_value)


@define
class Button:
    size: int
    wiring: tuple[int, ...]
    joltage: int | None = None

    toggle: int = 0

    def __attrs_post_init__(self) -> None:
        value = 0
        for i in range(self.size):
            if i in self.wiring:
                value += 2 ** (self.size - (i + 1))
        self.toggle = value

    def __repr__(self) -> str:
        return "".join(map(str, self.wiring))


@define
class Machine:
    lights: LightDiagram
    buttons: list[Button]

    def find_configuration(self) -> tuple[Button, ...]:
        if 0 == self.lights.target_value:
            return tuple()

        for elem_count in itertools.count(1):
            for buttons in itertools.product(self.buttons, repeat=elem_count):
                light_state = 0
                for button in buttons:
                    light_state = light_state ^ button.toggle
                if light_state == self.lights.target_value:
                    return buttons

        raise ValueError("Could not find a correct configuration.")

    @classmethod
    def from_line(cls, input_line: str) -> "Machine":
        """
        Creates a new Machine instance from the parsed input string.

        Args:
            input_line (str): Input string with parsable machine data.

        Returns:
            Machine: Machine instance parsed from the input.

        Raises:
            ValueError: If input string does not contain the data points
                required to create a machine in the expected pattern.
        """

        if match := MACHINE_PATTERN.match(input_line):
            components = match.groupdict()
            lights = LightDiagram.from_line(components["lights"].strip("[]"))

            size = len(lights.target)
            wirings = map(
                lambda x: tuple(map(int, x.strip("()").split(","))),
                components["buttons"].strip().split(),
            )
            joltages = map(int, components["joltages"].strip("{}").split(","))

            buttons = [Button(size, wiring) for wiring in wirings]

            return cls(lights, buttons)

        raise ValueError("Unexpected input data. Machine cannot be created.")


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

    machines = [Machine.from_line(line) for line in read_lines(input_path)]

    button_presses = [len(machine.find_configuration()) for machine in machines]

    print(f"Problem 1: {sum(button_presses)}")

    print(f"Problem 2: ")


if __name__ == "__main__":
    main(False)
