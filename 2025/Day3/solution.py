"""
Advent of Code 2025
Day 3

Full problem: https://adventofcode.com/2025/day/3

A: Find the largest combined 2 digit number possible within a line of decimals
without changing the order of digits. Get the sum of such numbers for all lines.

B: Find the largest combined 12 digit number possible within a line of decimals
without changing the order of digits. Get the sum of such numbers for all lines.
"""

from collections.abc import Iterator
from pathlib import Path

from attrs import define

INPUT_FILE = "input.txt"
TEST_INPUT_FILE = "test_input.txt"


class BatteryJoltageError(Exception):
    """
    Exception raised for an invalid battery joltage value.

    Attributes:
        message (str): The explanation of the error
    """

    def __init__(self, message: str) -> None:
        """
        Create the custom battery joltage exception.

        Args:
            message (str): Explanation text for the error

        Returns:
            None
        """
        self.message = message
        super().__init__(self.message)


@define
class BatteryBank:
    """A bank represented by the joltage and placement of the turned on batteries."""

    batteries: list[int]

    @property
    def joltage(self) -> int:
        """
        Calculates the joltage produced by the current batteries.

        Returns:
            int: The total joltage of the batteries.
        """
        result = 0
        for idx, battery in enumerate(reversed(self.batteries)):
            result += 10**idx * battery
        return result


@define
class MaximumJoltageFinder:
    """A finder class to test battery arrangements for best joltage output."""

    @staticmethod
    def get_new_maximum_joltage_bank(
        current_bank: BatteryBank, battery_new: int
    ) -> BatteryBank:
        """
        Calculate alternative bank arrangements for the provided battery sequence
        and return the maximum joltage value producing batteries as the new bank.

        Args:
            current_bank (BatteryBank): Current bank defined by a sequence of batteries.
            battery_new (int): A new battery represented by its joltage value that
                can be used to replace the batteries of the current bank.
        Returns:
            BatteryBank: Bank of batteries producing the maximum joltage amount.
        """
        batteries: list[int] = [*current_bank.batteries, battery_new]

        best_arrangement = current_bank.batteries
        max_joltage = current_bank.joltage
        for i in range(len(batteries)):
            alt_arrangement = batteries[:]
            alt_arrangement.pop(i)

            alt_bank = BatteryBank(alt_arrangement)
            if alt_bank.joltage > max_joltage:
                max_joltage = alt_bank.joltage
                best_arrangement = alt_bank.batteries

        return BatteryBank(best_arrangement)


def read_battery_banks(input_path: Path) -> Iterator[list[int]]:
    """
    Extract the battery bank lines from a file.

    Args:
        input_path (Path): Path to the file input to read.

    Returns:
        Iterator[list[int]]: Iterator of lists of decimal integers in a line.

    Raises:
        BatteryJoltageError: If any of the batteries within a bank line
            has a non-decimal joltage value.
    """
    with open(input_path, mode="r") as f:
        for line in f:
            digits = line.strip()
            if not digits.isdecimal():
                raise BatteryJoltageError(
                    "Unexpected value. Battery joltage must be decimal values."
                )
            yield list(map(int, digits))


def main(test: bool = False) -> None:
    """
    Main entry point for the script.

    Reads the input from a file, calculates and prints the solution
    to both parts of the problem.

    Returns:
        None
    """
    input_path = Path(__file__).parent / (TEST_INPUT_FILE if test else INPUT_FILE)

    bank_lines = read_battery_banks(input_path)

    total_output_for_2 = 0
    total_output_for_12 = 0
    for battery_bank in bank_lines:
        bank_of_2 = BatteryBank(battery_bank[:2])
        bank_of_12 = BatteryBank(battery_bank[:12])

        for i in range(len(battery_bank)):
            if i >= 2:
                bank_of_2 = MaximumJoltageFinder.get_new_maximum_joltage_bank(
                    bank_of_2, battery_bank[i]
                )

            if i >= 12:
                bank_of_12 = MaximumJoltageFinder.get_new_maximum_joltage_bank(
                    bank_of_12, battery_bank[i]
                )

        total_output_for_2 += bank_of_2.joltage
        total_output_for_12 += bank_of_12.joltage

    print(f"Problem 1: {total_output_for_2}")

    print(f"Problem 2: {total_output_for_12}")


if __name__ == "__main__":
    main(False)
