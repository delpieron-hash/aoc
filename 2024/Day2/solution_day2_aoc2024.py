"""
Advent of Code 2024
Day 2

Full problem: https://adventofcode.com/2024/day/2

A: Find the count of lists of numbers that satisfy two rules. The numbers must be 
either in increasing or decreasing order. The difference between two adjacent 
numbers must be between 1 and 3.

B: Allow one number to be omitted from the list to satisfy the two rules.
"""

import re
from pathlib import Path

INPUT_FILE = "input_day2_aoc2024.txt"


def read_input(filename: str | None = None) -> list[list[int]]:
    """
    Read all lists of numbers from file

    Args:
        filename (str | None): Name of file to read from

    Returns:
        list[list[int]]: List of lists of numbers
    """
    input_name = filename or INPUT_FILE
    input_src = Path(Path(__file__).parent / input_name)

    num_pattern = re.compile(r"(\d+)")

    with open(input_src, "r") as f:

        matches = [re.findall(num_pattern, line.strip()) for line in f]
        nums = [list(map(int, match)) for match in matches]

    return nums


def is_safe(nums: list[int], strict: bool = True) -> bool:
    """
    Check if a list of numbers satisfy the two safety rules

    All numbers must be either in increasing or decreasing order.
    The difference between two adjacent numbers must be between 1 and 3.

    Args:
        nums (list[int]): List of numbers to check
        strict (bool): If False, one number can be omitted from the list

    Returns:
        bool: True if the list satisfies the rules
    """
    if is_increasing(nums) or is_decreasing(nums):
        return True

    if not strict:
        for i in range(len(nums)):
            lazy_nums = nums[:i] + nums[i + 1 :]
            if is_increasing(lazy_nums) or is_decreasing(lazy_nums):
                return True

    return False


def is_increasing(nums: list[int]) -> bool:
    """
    Check if the list of numbers is in increasing order with each
    adjacent pair differing by 1 to 3.

    Args:
        nums (list[int]): List of numbers to check

    Returns:
        bool: True if the numbers are in increasing order with each
              adjacent pair differing by 1 to 3, otherwise False
    """
    for i in range(len(nums) - 1):
        if not (1 <= nums[i + 1] - nums[i] <= 3):
            return False

    return True


def is_decreasing(nums: list[int]) -> bool:
    """
    Check if the list of numbers is in decreasing order with each
    adjacent pair differing by 1 to 3.

    Args:
        nums (list[int]): List of numbers to check

    Returns:
        bool: True if the numbers are in decreasing order with each
              adjacent pair differing by 1 to 3, otherwise False
    """
    for i in range(len(nums) - 1):
        if not (-3 <= nums[i + 1] - nums[i] <= -1):
            return False

    return True


def main():
    """
    Main entry point for the script

    Reads the input from a file, calculates and prints the solution to
    both parts of the problem.
    """
    input_lists = read_input()

    strict_safe_count = sum(1 for nums in input_lists if is_safe(nums))
    print(f"Problem 1: {strict_safe_count}")

    lazy_safe_count = sum(1 for nums in input_lists if is_safe(nums, False))
    print(f"Problem 2: {lazy_safe_count}")


if __name__ == "__main__":
    main()
