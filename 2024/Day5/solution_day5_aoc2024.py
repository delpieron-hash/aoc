"""
Advent of Code 2024
Day 5

Full problem: https://adventofcode.com/2024/day/5

A: Find all valid (i.e. correctly ordered) updates and sum their middle page numbers

B: Fix all incorrect updates (i.e. order them correctly) and sum their middle page numbers
"""

import re
from pathlib import Path

INPUT_FILE = "input_day5_aoc2024.txt"


class NumberRule:
    """
    A class to represent a number and its ordering rules.

    Attributes:
        value (int): The number for which the ordering rules are defined.
        before (list[int]): A list of numbers that should come before the current number.
        after (list[int]): A list of numbers that should come after the current number.
    """

    def __init__(
        self,
        value: int,
        before: list[int] | None = None,
        after: list[int] | None = None,
    ) -> None:
        """
        Initialize a NumberRule instance with a specified value and empty lists for ordering rules.

        Args:
            value (int): The number for which the ordering rules will be defined.
            before (list[int] | None):
                A list of numbers that should come before the current number. None by default.
            after (list[int] | None):
                A list of numbers that should come after the current number. None by default.
        """
        self.value = value
        self.before = before if before else []
        self.after = after if after else []

    def add_before(self, value: int) -> None:
        """
        Add value to the list of numbers that should come before the current number

        Args:
            value (int): The value to add to the list
        """
        self.before.append(value)

    def add_after(self, value: int) -> None:
        """
        Add value to the list of numbers that should come after the current number

        Args:
            value (int): The value to add to the list
        """
        self.after.append(value)

    def __repr__(self) -> str:
        """
        Return a string representation of the NumberRule instance.

        Returns:
            str: A string representation of the NumberRule instance.
        """
        return (
            f"NumberRule(value={self.value}, before={self.before}, after={self.after})"
        )


def read_input(filename: str | None = None) -> str:
    """
    Read full input from file

    Args:
        filename (str | None): Name of file to read from

    Returns:
        str: Full input text
    """
    input_name = filename or INPUT_FILE
    input_src = Path(Path(__file__).parent / input_name)

    with open(input_src, "r") as f:
        return f.read()


def process_instructions(instructions: list[str]) -> tuple[list[str], list[str]]:
    """
    Separate instructions into based on empty line divisor

    Args:
        instructions (list[str]): List of instructions to process

    Returns:
        tuple[list[str], list[str]]: Tuple of two lists. The first list contains the
            ordering rules and the second list contains the pages to update.
    """
    separator_idx = instructions.index("")
    ordering_rules = instructions[:separator_idx]
    pages_to_update = instructions[separator_idx + 1 :]

    return ordering_rules, pages_to_update


def process_rules(ordering_rules: list[str]) -> dict[int, NumberRule]:
    """
    Process a list of ordering rules and return a dictionary mapping each number to its rules.

    Args:
        ordering_rules (list[str]): List of ordering rules to process

    Returns:
        dict[int, NumberRule]: Dictionary mapping each number to its rules
    """
    num_rules = {}

    for rule in ordering_rules:

        if match := re.match(r"^(\d+)\|(\d+)$", rule):
            left = int(match.group(1))
            right = int(match.group(2))

            left_rule = num_rules.setdefault(left, NumberRule(left))
            left_rule.add_after(right)
            right_rule = num_rules.setdefault(right, NumberRule(right))
            right_rule.add_before(left)

    return num_rules


def process_updates(
    updates: list[list[int]], num_rules: dict[int, NumberRule]
) -> tuple[list[list[int]], list[list[int]]]:
    """
    Process a list of updates and return two lists:
    one with correct updates and one with incorrect updates

    Args:
        updates (list[list[int]]): List of updates to process
        num_rules (dict[int, NumberRule]): Dictionary mapping each number to its rules

    Returns:
        tuple[list[list[int]], list[list[int]]]: Tuple of two lists. The first list contains the
            updates that are correct and the second list contains the updates that are incorrect
    """
    ok_updates = []
    failed_updates = []

    for update in updates:
        if is_correct_update(update, num_rules):
            ok_updates.append(update)
        else:
            failed_updates.append(update)

    return ok_updates, failed_updates


def is_correct_update(update: list[int], num_rules: dict[int, NumberRule]) -> bool:
    """
    Check if an update is correct based on the number rules

    Args:
        update (list[int]): List of numbers to check
        num_rules (dict[int, NumberRule]): Dictionary mapping each number to its rules

    Returns:
        bool: True if the update is correct, False otherwise
    """

    for idx, update_num in enumerate(update):
        if not all(num not in num_rules[update_num].after for num in update[:idx]):
            return False

        # Note: No need to check if seq_num is in num_rules[update_num].before
        # because if it is, then it would have been flagged above

    return True


def fix_failed_update(update: list[int], num_rules: dict[int, NumberRule]) -> list[int]:
    """
    Fix an incorrect update based on the number rules

    Args:
        update (list[int]): List of numbers to fix
        num_rules (dict[int, NumberRule]): Dictionary mapping each number to its rules

    Returns:
        list[int]: Fixed update
    """

    while not is_correct_update(update, num_rules):
        swapped = False
        for idx, update_num in enumerate(update):
            for cmp_idx, seq_num in enumerate(update[:idx]):
                if seq_num in num_rules[update_num].after:
                    update[idx], update[cmp_idx] = seq_num, update_num
                    swapped = True
                    break  # Break out of inner loop after swap

            # * Note: No need to check if seq_num is in num_rules[update_num].before
            # * because if it is, then it would have been swapped above

            # If swapped, we can break out of the outer loop and recheck
            if swapped:
                break

        if not swapped:
            raise ValueError("Update cannot be fixed - no valid swaps possible")

    return update


def main() -> None:
    """
    Main entry point for the script

    Reads the input from a file, processes data and prints the solution to
    both parts of the problem.

    Returns:
        None
    """
    instructions = read_input().splitlines(keepends=False)

    ordering_rules, pages_to_update = process_instructions(instructions)

    num_rules = process_rules(ordering_rules)
    update_instructions = [
        list(map(int, update.split(","))) for update in pages_to_update
    ]

    ok_updates, failed_updates = process_updates(update_instructions, num_rules)
    sum_ok_updates = sum(update[len(update) // 2] for update in ok_updates)

    print(f"Problem 1: {sum_ok_updates}")

    sum_fixed_updates = sum(
        fix_failed_update(update, num_rules)[len(update) // 2]
        for update in failed_updates
    )
    print(f"Problem 2: {sum_fixed_updates}")


if __name__ == "__main__":
    main()
