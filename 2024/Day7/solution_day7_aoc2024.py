"""
Advent of Code 2024
Day 7

A: Find the correct equations and sum their test values

B: Sum the test values of correct equations if the concatenation operator is allowed
"""

import re
from pathlib import Path

INPUT_FILE = "input_day7_aoc2024.txt"
TEST_INPUT_FILE = "test_input_day7_aoc2024.txt"
OUTPUT_FILE = "output_day7_aoc2024.txt"
TEST_OUTPUT_FILE = "test_output_day7_aoc2024.txt"


class Equation:

    def __init__(self, test_num: int, numbers: list[int], operands: list[str]) -> None:
        self.test_num = test_num
        self.numbers = numbers
        self.operands = operands
        self.operations: list[str] = ["+"]
        self.is_validated = self.is_valid(self.numbers[1:], self.numbers[0])

    def __repr__(self) -> str:
        """
        Return a string representation of the equation

        Returns:
            str: String representation of the equation
        """
        return f"Equation(test_num={self.test_num}, numbers={self.numbers})"

    def is_valid(self, numbers: list[int], total: int = 0) -> bool:
        """
        Check if the equation test number can be produced from the given list of numbers

        Args:
            numbers (list[int]): List of numbers to check
            total (int): Total of numbers so far

        Returns:
            bool: True if the equation is valid, False otherwise
        """
        # Base case - Valid
        if total == self.test_num and not numbers:
            return True

        # Base case - Invalid
        if total > self.test_num:
            return False

        # Recursive case
        if total <= self.test_num:

            # Base case - No more numbers and still below target
            if not numbers:
                return False

            for operand in self.operands:
                self.operations.append(operand)
                new_total = self.evaluate(operand, total, numbers[0])

                if self.is_valid(numbers[1:], new_total):
                    return True
                else:
                    self.operations.pop()

        return False

    def evaluate(self, operand: str, num1: int, num2: int) -> int:
        """
        Evaluate the equation

        Args:
            operand (str): The operation to perform
            num1 (int): The first number
            num2 (int): The second number

        Returns:
            int: The result of the equation
        """

        if operand == "+":
            return num1 + num2
        if operand == "*":
            return num1 * num2
        if operand == "||":
            return num1 * (10 ** len(str(num2))) + num2

        raise ValueError(f"Invalid operand: {operand}")

    def print_solution(self) -> None:
        """
        Print the equation and its solution if there is one to the console

        Returns:
            None
        """
        if not self.is_validated:
            print(f"{self.test_num} != {self.numbers}")
            return

        equation_str = f"{self.test_num} ="
        for num, operation in zip(self.numbers, self.operations):
            equation_str += f" {operation} {num}"
        print(equation_str)


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


def process_equation_line(line: str, operands: list[str]) -> Equation:
    """
    Process an equation line

    Args:
        line (str): Line of equation to process
        operands (list[str]): List of valid operands in the equation

    Returns:
        Equation: Processed equation
    """

    test_num, num_str = re.split(r":\s", line, maxsplit=1)

    (*numbers,) = map(int, re.findall(r"\d+", num_str))

    return Equation(int(test_num), numbers, operands)


def main() -> None:
    """
    Main entry point for the script

    Reads the input from a file, processes data and prints the solution to
    both parts of the problem.

    Returns:
        None
    """
    txt_input = read_input(False)

    p1_operands = ["+", "*"]
    p1_equations = [
        process_equation_line(line, p1_operands)
        for line in txt_input.splitlines(keepends=False)
    ]
    p1_sum_valid_test_values = sum(
        equation.test_num for equation in p1_equations if equation.is_validated
    )

    print(f"Problem 1: {p1_sum_valid_test_values}")

    p2_operands = ["+", "*", "||"]
    p2_equations = [
        process_equation_line(line, p2_operands)
        for line in txt_input.splitlines(keepends=False)
    ]
    p2_sum_valid_test_values = sum(
        equation.test_num for equation in p2_equations if equation.is_validated
    )

    print(f"Problem 2: {p2_sum_valid_test_values}")


if __name__ == "__main__":
    main()
