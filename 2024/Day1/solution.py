"""
Advent of Code 2024
Day 1

Full problem: https://adventofcode.com/2024/day/1

A: Finding the sum of distances between two lists of numbers. The distance should be
measured as the difference between the numbers ordered from smallest to largest

B: Calculating the product of the numbers in the first list that are also in the second list
and their frequency in the second list
"""

from collections import Counter
from collections.abc import Iterator
from pathlib import Path

INPUT_FILE = "input.txt"
TEST_INPUT_FILE = "test_input.txt"


def read_pairs(filename: str) -> Iterator[tuple[int, int]]:
    """
    Read number pairs from a file

    Args:
        filename (str): Name of the file to read

    Returns:
        Iterator[tuple[int, int]]: Iterator of tuples of two integers
    """
    input_src = Path(__file__).parent / filename

    with open(input_src, "r") as f:
        for line in f:
            left, right = line.split()
            yield int(left), int(right)


def main():
    """
    Main entry point for the script

    Reads the input from a file, calculates and prints the solution to
    both parts of the problem.
    """
    listA, listB = zip(*read_pairs(INPUT_FILE))

    distance = sum(abs(a - b) for a, b in zip(sorted(listA), sorted(listB)))
    print(f"Problem 1: {distance}")

    listB_count = Counter(listB)
    similarity_score = sum(item * listB_count[item] for item in listA)
    print(f"Problem 2: {similarity_score}")


if __name__ == "__main__":
    main()
