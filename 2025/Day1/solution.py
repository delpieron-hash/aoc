"""
Advent of Code 2025
Day 1

Full problem: https://adventofcode.com/2025/day/1

A: Count the number of 0 states on a 0-99 rotating dial at the end of
the given left and right rotations.

B: Count the number of times the dial is at 0 state during anytime while
performing the given left and right rotations.
"""

import re
from collections.abc import Iterator
from enum import StrEnum
from pathlib import Path

from attrs import Attribute, define, field, validators

INPUT_FILE = "input.txt"
TEST_INPUT_FILE = "test_input.txt"


class RotationInstructionError(Exception):
    """
    Exception raised for an invalid rotation instruction.

    Attributes:
        message (str): The explanation of the error
    """

    def __init__(self, message: str) -> None:
        """
        Create the custom rotation instruction exception.

        Args:
            message (str): Explanation text for the error

        Returns:
            None
        """
        self.message = message
        super().__init__(self.message)


class RotationDistanceError(RotationInstructionError):
    """Exception raised for an invalid rotation distance."""


class RotationDirectionError(RotationInstructionError):
    """Exception raised for an invalid rotation direction."""


class Direction(StrEnum):
    """The directions in which the safe dial can be rotated"""

    LEFT = "L"
    RIGHT = "R"


@define
class Instruction:
    """The number of clicks the dials should be rotated following the text instruction."""

    direction: Direction
    distance: int = field(validator=[validators.instance_of(int)])

    @distance.validator  # pyright: ignore[reportAttributeAccessIssue]
    def is_non_negative_distance(self, attribute: Attribute, value: int) -> None:
        """
        Validate that the rotation distance is non-negative.

        Args:
            attribute (Attribute): The attribute that needs to be validated.
            value (int): The value to validate for the attribute.

        Returns:
            None

        Raises:
            RotationDistanceError: If the distance value is negative.
        """
        if value < 0:
            raise RotationDistanceError(
                f"Rotation distance must be non-negative, got {value}"
            )

    @property
    def rotation(self) -> int:
        """
        Converts the direction and distance of the rotation to a single value.
        Positive values represent right turns, negative left turns on the dial.

        Returns:
            int: The rotation to make per current instructions.

        Raises:
            RotationDirectionError: If the direction of the rotation is invalid.
        """
        if self.direction == Direction.RIGHT:
            return self.distance

        elif self.direction == Direction.LEFT:
            return -self.distance

        raise RotationDirectionError("Invalid rotation direction.")


@define
class Dial:
    """The dial protecting the safe with numbers 0 through 99."""

    state: int = 50

    def rotate(self, instruction: Instruction) -> None:
        """
        Change the current state of the dial according to the rotation instruction.

        Args:
            rotation (Instruction): A rotation instruction with direction and distance.

        Returns:
            None
        """
        self.state += instruction.rotation

    def is_zero(self) -> bool:
        """
        Check if the current state of the dial is zero.

        Returns:
            bool: True if the dial points at 0, False otherwise.
        """
        return self.state % 100 == 0

    def count_zero_passes(self, instruction: Instruction) -> int:
        """
        Count the interim zero states of the dial during the execution of a rotation.

        Args:
            instruction (Instruction): The rotation instruction to simulate.

        Returns:
            int: The number of times the dial points at 0 while performing the rotation.

        Raises:
            RotationDirectionError: If the direction of the rotation is invalid.
        """
        future_state = self.state + instruction.rotation

        if instruction.direction == Direction.RIGHT:
            return abs(future_state // 100 - self.state // 100)
        elif instruction.direction == Direction.LEFT:
            return abs((future_state - 1) // 100 - (self.state - 1) // 100)

        raise RotationDirectionError("Invalid rotation direction.")


def read_instructions(input_path: Path) -> Iterator[Instruction]:
    """
    Read the rotation instructions line by line from a file.

    Args:
        input_path (Path): Path to the file input to read.

    Returns:
        Iterator[Rotation]: Iterator of Rotation instructions.

    Raises:
        RotationInstructionError: If the input read from file cannot be translated
            to a valid rotation instruction.
    """
    pattern = re.compile(r"(L|R)(\d+)")

    with open(input_path, mode="r") as f:
        for line in f:
            if instruction := re.match(pattern, line.strip()):
                direction = Direction(value=instruction.group(1))
                distance = int(instruction.group(2))
                yield Instruction(direction, distance)
            else:
                raise RotationInstructionError(
                    "Unexpected instruction. Cannot translate to turns for the dial"
                )


def main(test: bool = False) -> None:
    """
    Main entry point for the script.

    Reads the input from a file, calculates and prints the solution
    to both parts of the problem.

    Returns:
        None
    """
    input_path = Path(__file__).parent / (TEST_INPUT_FILE if test else INPUT_FILE)

    instructions = read_instructions(input_path)

    dial = Dial()
    zero_state_count = 0
    zero_passed_count = 0
    for instruction in instructions:
        zero_passed_count += dial.count_zero_passes(instruction)
        dial.rotate(instruction)
        if dial.is_zero():
            zero_state_count += 1

    print(f"Problem 1: {zero_state_count}")

    print(f"Problem 2: {zero_passed_count}")


if __name__ == "__main__":
    main(False)
