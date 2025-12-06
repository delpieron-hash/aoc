"""
Advent of Code 2025
Day 5

Full problem: https://adventofcode.com/2025/day/5

A: Determine how many of the ingredient ID's provided do fall within the fresh ID ranges.

B: Calculate the count of all available, unique fresh IDs within the provided ranges.
"""

import re
from collections.abc import Iterator
from pathlib import Path
from typing import cast

from attrs import define

INPUT_FILE = "input.txt"
TEST_INPUT_FILE = "test_input.txt"


@define
class IdRange:
    """Represents a range of ingredient IDs."""

    min_value: int
    max_value: int

    def __attrs_post_init__(self) -> None:
        """
        Verifies that the IdRange was created with correct min and max attributes.

        Returns:
            None

        Raises:
            ValueError: If the upper bound is smaller than the lower bound.
        """
        if self.min_value > self.max_value:
            raise ValueError(
                "Unexpected range input. Upper bound must be larger than lower bound."
            )

    def is_in_range(self, test_id: int) -> bool:
        """
        Determines whether the provided id falls within the current range.

        Args:
            test_id (int): The integer id to test.

        Returns:
            bool: True if the id falls within the range, False otherwise.
        """
        return self.min_value <= test_id <= self.max_value

    @property
    def span(self) -> int:
        """
        Calculates the number of unique IDs falling in the current range.

        Returns:
            int: Count of IDs within the range.
        """
        return self.max_value - self.min_value + 1

    def __lt__(self, other_range: "IdRange") -> bool:
        """
        Compares the current range with another range and determines
        if this range is less than the provided one.

        A range is considered less than another one when all IDs of the range
        are smaller than any ID of the other range.

        Args:
            other_range (IdRange): IdRange to which to compare the current one.

        Returns:
            bool: True if this range is less than the other range, otherwise False.
        """
        return self.max_value < other_range.min_value

    def has_overlap(self, other_range: "IdRange") -> bool:
        """
        Determines if the current range has any IDs that also fall within
        the provided other range.

        Args:
            other_range (IdRange): IdRange to which to compare the current one.

        Returns:
            bool: True if this range has overlap with the other range, False otherwise.
        """
        return not (self < other_range or other_range < self)

    def extend(self, other_range: "IdRange") -> None:
        """
        Combines the current range with another IdRange.

        The new union of ranges will span from the lowest of the lower bounds
        to the highest of the upper bounds.

        Args:
            other_range (IdRange): IdRange to combine with the current one.

        Returns:
            None
        """
        self.min_value = min(self.min_value, other_range.min_value)
        self.max_value = max(self.max_value, other_range.max_value)

    def __str__(self) -> str:
        """
        Display the range as the min and max value connected by a pointed arrow.

        Returns:
            str: The string representation of the object.
        """
        return f"{self.min_value}->{self.max_value}"


@define
class IdRangeCollection:
    """Represents a collection of non-overlapping, consolidated IdRanges."""

    id_ranges: list[IdRange]

    def is_in_collection(self, test_id: int) -> bool:
        """
        Checks if the provided ID number falls within any of the held IdRanges.

        Returns:
            bool: True if the provided ID is in any of the ranges, False otherwise.
        """
        for id_range in self.id_ranges:
            if id_range.is_in_range(test_id):
                return True

        return False

    @property
    def span(self) -> int:
        """
        Calculates the number of unique IDs in the collected ranges.

        Returns:
            int: Count of all IDs within ranges of the collection.
        """
        return sum(id_range.span for id_range in self.id_ranges)

    @classmethod
    def from_overlapping_ranges(cls, id_ranges: list[IdRange]) -> "IdRangeCollection":
        """
        Create an instance of the current class from a list of IdRanges that
        potentially overlap. The created item should have ranges that are merged
        where necessary to create a non-overlapping set and put in ascending order.

        Returns:
            IdRangeCollection: An instance of the current class with ordered ranges.
        """
        id_ranges.sort()

        i = 0
        while i + 1 < len(id_ranges):
            if id_ranges[i].has_overlap(id_ranges[i + 1]):
                id_ranges[i].extend(id_ranges.pop(i + 1))

                # Check if extension caused some overlap with the previous item
                if i > 0:
                    i -= 1

            else:
                i += 1

        return cls(id_ranges)


def read_ingredient_input(input_path: Path) -> str:
    """
    Read the input data as a string from the provided file path.

    Args:
        input_path (Path): Path to the file input to read.

    Returns:
        str: Full input data as a string.
    """
    with open(input_path, mode="r") as f:
        return f.read()


def find_fresh_id_ranges(input_text: str) -> list[IdRange]:
    """
    Finds the fresh ingredient ranges from the input text using pattern matching.
    Converts the found range bounds to a list of IdRanges and returns them.

    Args:
        input_text (str): Text input for the IDs as a string.

    Returns:
        list[IdRange]: List of extracted fresh ingredient IdRanges.
    """
    id_range_pattern = re.compile(r"^(\d+)-(\d+)$", re.MULTILINE)

    # Returns a list of tuples if 2 capturing groups in pattern
    fresh_id_ranges = cast(list[tuple[str, str]], id_range_pattern.findall(input_text))

    return [
        IdRange(int(min_bound), int(max_bound))
        for min_bound, max_bound in fresh_id_ranges
    ]


def find_ingredient_ids(input_text: str) -> Iterator[int]:
    """
    Finds the ingredient ID numbers from the input text using pattern matching.
    Converts the found IDs to integers and returns them as an iterator.

    Args:
        input_text (str): Text input for the IDs as a string.

    Returns:
        Iterator[int]: Iterator of ingredient ID integers.
    """
    id_pattern = re.compile(r"^\d+$", re.MULTILINE)

    # Returns a list of strings if no capturing groups in pattern
    id_inputs = cast(list[str], id_pattern.findall(input_text))

    return map(int, id_inputs)


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

    ingredient_data = read_ingredient_input(input_path)

    verifiable_ingredient_ids = find_ingredient_ids(ingredient_data)
    fresh_ranges = IdRangeCollection.from_overlapping_ranges(
        find_fresh_id_ranges(ingredient_data)
    )

    fresh_count = sum(
        fresh_ranges.is_in_collection(ingredient_id)
        for ingredient_id in verifiable_ingredient_ids
    )

    print(f"Problem 1: {fresh_count}")

    print(f"Problem 2: {fresh_ranges.span}")


if __name__ == "__main__":
    main(False)
