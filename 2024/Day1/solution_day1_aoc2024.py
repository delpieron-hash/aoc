"""
Advent of Code 2024
Day 1

A: Finding the sum of distances between two lists of numbers. The distance should be 
measured as the difference between the numbers ordered from smallest to largest

B: Calculating the product of the numbers in the first list that are also in the second list
and their frequency in the second list
"""

import re
from collections import Counter
from pathlib import Path

INPUT_FILE = "input_day1_aoc2024.txt"


def read_input(filename: str | None = None) -> tuple[list[int], list[int]]:
    """
    Read number pairs from file

    Args:
        filename (str | None): Name of file to read from

    Returns:
        tuple[list[int], list[int]]: Two lists of numbers
    """
    input_name = filename or INPUT_FILE
    input_src = Path(Path(__file__).parent / input_name)

    listA, listB = [], []

    with open(input_src, "r") as f:
        num_pattern = re.compile(r"(\d+)\s+(\d+)")
        for line in f:
            matches = re.findall(num_pattern, line.strip())
            listA.append(int(matches[0][0]))
            listB.append(int(matches[0][1]))

    return listA, listB


def main():
    """
    Main entry point for the script

    Reads the input from a file, calculates and prints the solution to
    both parts of the problem.
    """
    listA, listB = read_input()

    distance = sum(abs(a - b) for a, b in zip(sorted(listA), sorted(listB)))
    print(f"Problem 1: {distance}")

    listB_count = Counter(listB)
    similarity_score = sum(item * listB_count[item] for item in listA)
    print(f"Problem 2: {similarity_score}")


if __name__ == "__main__":
    main()
