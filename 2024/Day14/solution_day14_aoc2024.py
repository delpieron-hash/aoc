"""
Advent of Code 2024
Day 14

Full problem: https://adventofcode.com/2024/day/14

A: 

B: 
"""

from pathlib import Path

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


def main() -> None:
    """
    Main entry point for the script

    Reads the input from a file, processes data and prints the solution to
    both parts of the problem.

    Returns:
        None
    """
    txt_input = read_input(True).strip()

    print(txt_input)

    print(f"Problem 1:")

    print(f"Problem 2:")


if __name__ == "__main__":
    main()
