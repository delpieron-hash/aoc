"""
Advent of Code 2025
Day 6

Full problem: https://adventofcode.com/2025/day/6

A: Arrange the provided numbers and operators into columns. Perform the operation for each
group of numbers and calculate the total sum.

B: Position the numbers according to digit-by-digit columns read right-to-left. Once again
perform the operations on the group of number and calculate the total sum.
"""

import math
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Literal, cast

INPUT_FILE = "input.txt"
TEST_INPUT_FILE = "test_input.txt"

NUMBER_PATTERN = re.compile(r"\d+")
OPERATOR_PATTERN = re.compile(r"\*|\+")


def read_input_lines(input_path: Path) -> list[str]:
    """
    Extracts all non-empty lines preserving whitespace from the provided file.

    Args:
        input_path (Path): Path to the file input to read.

    Returns:
        list[str]: Non-empty input lines as a list of strings.
    """
    with open(input_path, mode="r") as f:
        return f.read().splitlines(False)


def read_numbers(input_line: str) -> list[int]:
    """
    Finds all numbers in the input line and returns them as a list.

    Returns:
        list[int]: Numbers found in the input as a list of integers.
    """
    return [int(num) for num in NUMBER_PATTERN.findall(input_line)]


def read_arithmetic_operators(input_line: str) -> Iterator[Literal["*"] | Literal["+"]]:
    """
    Finds all arithmetic operators in the input line and yields them as an iterator.

    Yields:
        Literal['*'|'+']: Arithmetic operator found in the input as a literal string.
    """
    for operator in OPERATOR_PATTERN.finditer(input_line):
        yield cast(Literal["*"] | Literal["+"], operator.group())


def group_numbers_by_digit_columns(input_lines: list[str]) -> Iterator[list[int]]:
    """
    Groups numbers from the input lines by digit-columns, where groups are
    separated by blank columns.

    Args:
        input_lines (list[str]): The raw input lines containing the numbers and digits.

    Yields:
        list[int]: List of integers representing a number group.
    """
    number_group: list[int] = []
    for num_digits in zip(*input_lines, strict=True):
        # If current column has a number, add it to group
        if number_str := "".join(num_digits).strip():
            number_group += [int(number_str)]

        # Yield the accumulated group, if empty, separator column
        else:
            if number_group:
                yield number_group
            number_group = []

    if number_group:
        yield number_group


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

    input_lines = read_input_lines(input_path)

    operators = read_arithmetic_operators(input_lines.pop())

    p1_number_columns = zip(*[read_numbers(line) for line in input_lines], strict=True)
    p2_number_columns = group_numbers_by_digit_columns(input_lines)

    p1_total_sum = 0
    p2_total_sum = 0
    for operator, p1_num_col, p2_num_col in zip(
        operators, p1_number_columns, p2_number_columns
    ):
        match operator:
            case "+":
                p1_col_sum = sum(p1_num_col)
                p2_col_sum = sum(p2_num_col)
            case "*":
                p1_col_sum = math.prod(p1_num_col)
                p2_col_sum = math.prod(p2_num_col)

        p1_total_sum += p1_col_sum
        p2_total_sum += p2_col_sum

    print(f"Problem 1: {p1_total_sum}")

    print(f"Problem 2: {p2_total_sum}")


if __name__ == "__main__":
    main(False)
