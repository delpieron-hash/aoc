"""
Advent of Code 2025
Day 2

Full problem: https://adventofcode.com/2025/day/2

A: Sum up the invalid IDs within the input ranges. An invalid ID has
a sequence of digits repeated exactly twice.

B: Sum up the invalid IDs within the input ranges. An invalid ID has
a sequence of digits repeated twice or more.
"""

import math
import re
from collections.abc import Iterator
from pathlib import Path

from attrs import define

INPUT_FILE = "input.txt"
TEST_INPUT_FILE = "test_input.txt"


class IdRangeError(Exception):
    """
    Exception raised for an invalid ID range.

    Attributes:
        message (str): The explanation of the error
    """

    def __init__(self, message: str) -> None:
        """
        Create the custom ID range exception.

        Args:
            message (str): Explanation text for the error

        Returns:
            None
        """
        self.message = message
        super().__init__(self.message)


@define
class GiftID:
    """An ID that represents a valid product in the Gift Shop."""

    value: int

    @property
    def is_p1_valid(self) -> bool:
        """
        Determines whether the ID is a valid gift ID per problem part 1.

        Returns:
            bool: True if the ID represents a gift, False otherwise.
        """
        if self.value < 10:
            return True

        digit_count = math.floor(math.log10(self.value)) + 1

        if digit_count % 2 == 1:
            return True

        divider = 10 ** (digit_count // 2)
        first_half, second_half = divmod(self.value, divider)

        return first_half != second_half

    @property
    def is_p2_valid(self) -> bool:
        """
        Determines whether the ID is a valid gift ID per problem part 2.

        Returns:
            bool: True if the ID represents a gift, False otherwise.
        """
        if self.value < 10:
            return True

        digit_count = math.floor(math.log10(self.value)) + 1

        for pattern_length in range(1, (digit_count // 2) + 1):
            repeating_count, remainder = divmod(digit_count, pattern_length)

            # Skip patterns that do not exactly replicate the ID number
            if remainder != 0:
                continue

            pattern = str(self.value % (10**pattern_length))

            # Skip collapsing patterns starting with '0'
            if len(pattern) != pattern_length:
                continue

            if self.value == int(pattern * repeating_count):
                return False

        return True


@define
class Range:
    """A continuous range of Gift Shop product ID values."""

    lower_bound: int
    upper_bound: int

    def __attrs_post_init__(self) -> None:
        """
        Validates that the provided integer bounds construct a valid range.

        Returns:
            None

        Raises:
            IdRangeError: If the upper bound for the range does not exceed the
                lower bound.
        """
        if self.lower_bound >= self.upper_bound:
            raise IdRangeError(
                "Invalid range. The upper bound must be larger than the lower bound."
            )

    def get_p1_invalid_values(self) -> list[int]:
        """
        Returns a generated list of the part 1 invalid GiftID values within the range.

        Returns:
            list[int]: A list of the invalid GiftID values.
        """
        return [
            value
            for value in range(self.lower_bound, self.upper_bound + 1)
            if not GiftID(value).is_p1_valid
        ]

    def get_p2_invalid_values(self) -> list[int]:
        """
        Returns a generated list of the part 2 invalid GiftID values within the range.

        Returns:
            list[int]: A list of the invalid GiftID values.
        """
        return [
            value
            for value in range(self.lower_bound, self.upper_bound + 1)
            if not GiftID(value).is_p2_valid
        ]


def read_ranges(input_path: Path) -> Iterator[Range]:
    """
    Extract the integer ranges from a file.

    Args:
        input_path (Path): Path to the file input to read.

    Returns:
        Iterator[Range]: Iterator of integer Ranges.
    """
    pattern = re.compile(r"(\d+)-(\d+)", re.MULTILINE)

    with open(input_path, mode="r") as f:
        for line in f:
            if id_ranges := re.finditer(pattern, line.strip()):
                for id_range in id_ranges:
                    yield Range(int(id_range.group(1)), int(id_range.group(2)))


def main(test: bool = False) -> None:
    """
    Main entry point for the script.

    Reads the input from a file, calculates and prints the solution
    to both parts of the problem.

    Returns:
        None
    """
    input_path = Path(__file__).parent / (TEST_INPUT_FILE if test else INPUT_FILE)

    p1_invalid_sum = 0
    p2_invalid_sum = 0
    for id_range in read_ranges(input_path):
        p1_invalid_sum += sum(id_range.get_p1_invalid_values())
        p2_invalid_sum += sum(id_range.get_p2_invalid_values())

    print(f"Problem 1: {p1_invalid_sum}")

    print(f"Problem 2: {p2_invalid_sum}")


if __name__ == "__main__":
    main(False)
