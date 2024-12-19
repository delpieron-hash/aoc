"""
Advent of Code 2024
Day 11

Full problem: https://adventofcode.com/2024/day/11

A: Count the number of magic stones after 25 blinks (evolutions)

B: Count the number of magic stones after 75 blinks (evolutions)
"""

import math
from pathlib import Path

from attrs import define, field

INPUT_FILE = "input_day11_aoc2024.txt"
TEST_INPUT_FILE = "test_input_day11_aoc2024.txt"
OUTPUT_FILE = "output_day11_aoc2024.txt"
TEST_OUTPUT_FILE = "test_output_day11_aoc2024.txt"


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


@define(eq=False)
class MagicStone:
    """
    A class to represent a magic stone with a mark and its digit count.

    Attributes:
        mark (int): The mark value of the magic stone.
        digits (int): The number of digits in the mark.
    """

    mark: int = field(converter=int)
    digits: int = field(init=False)

    def __attrs_post_init__(self) -> None:
        """
        Initialize digits after mark has been set.

        Calculates the number of digits after the mark has been set.

        Returns:
            None
        """
        self.digits = MagicStone.count_digits(self.mark)

    @staticmethod
    def count_digits(n: int) -> int:
        """
        Count the number of digits in a number.

        Args:
            n (int): Number to count digits of

        Returns:
            int: Number of digits
        """
        if n == 0:
            return 1
        return math.floor(math.log10(n)) + 1


@define
class MagicField:
    """
    A class to represent a field of magic stones.

    A MagicField is a list of MagicStone instances, and it provides methods to
    evolve the field according to the rules of the problem.

    Attributes:
        stones (list[MagicStone]): The list of MagicStone instances
    """

    stones: list[MagicStone]
    evolution: int = field(default=0)
    stone_map: dict[MagicStone, int] = field(init=False)
    stone_cache: dict[int, tuple[MagicStone, ...]] = field(factory=dict)

    def __attrs_post_init__(self) -> None:
        """
        Initialize stone_map after stones have been set.

        Calculates the number of occurrences of each magic stone in the field.

        Returns:
            None
        """
        self.stone_map = {}
        for stone in self.stones:
            if stone in self.stone_map:
                self.stone_map[stone] += 1
            else:
                self.stone_map[stone] = 1

    @classmethod
    def from_text(cls, text: str) -> "MagicField":
        """
        Create a MagicField from a text string.

        The text string should be a space-separated list of integers, where each integer
        is the mark value of a magic stone.

        Args:
            text (str): The text string to create the MagicField from

        Returns:
            MagicField: The created MagicField
        """
        return cls([MagicStone(stone) for stone in text.strip().split(" ")])

    def evolve_to_n(self, n: int) -> None:
        """
        Evolve the field of magic stones to the specified number of times.

        Args:
            n (int): The number of times to evolve the field

        Returns:
            None
        """
        while self.evolution < n:
            self.evolve()

    def evolve(self) -> None:
        """
        Evolve the field of magic stones according to the specified rules.

        Returns:
            None
        """
        new_stones = {}
        for stone, count in self.stone_map.items():
            for evolved in self.evolve_stone(stone):
                if evolved in new_stones:
                    new_stones[evolved] += count
                else:
                    new_stones[evolved] = count

        self.evolution += 1
        self.stone_map = new_stones

    def evolve_stone(self, stone: MagicStone) -> tuple[MagicStone, ...]:
        """
        Evolve a single magic stone according to the rules:

        1. If a stone's mark is 0, it is replaced with a stone marked 1.
        2. If a stone's mark has an even number of digits, it is split into
        two stones: the left half of the digits and the right half.
        3. If neither condition applies, the stone's mark is multiplied by 2024.

        If the stone is found in the cache, return the cached result.
        Otherwise, apply the transformation rules to the stone and cache the result.

        Args:
            stone (MagicStone): The magic stone to evolve.

        Returns:
            tuple[MagicStone, ...]: A tuple of the resulting 1 or 2 magic stones.
        """

        if stone.mark in self.stone_cache:
            return self.stone_cache[stone.mark]

        if stone.mark == 0:
            evolved = (MagicStone(mark=1),)

        elif stone.digits % 2 == 0:
            split_point = 10 ** (stone.digits // 2)
            left, right = divmod(stone.mark, split_point)
            evolved = (MagicStone(mark=left), MagicStone(mark=right))

        else:
            evolved = (MagicStone(mark=stone.mark * 2024),)

        self.stone_cache[stone.mark] = evolved
        return evolved

    def total_stones(self) -> int:
        """
        Calculate the total number of stones in the magic field.

        Returns:
            int: The total number of stones.
        """
        return sum(count for count in self.stone_map.values())

    def print_stones(self) -> None:
        """
        Prints the current state of the magic field as a string of space-separated integers.

        Each integer is the mark on a magic stone, and the order is the same as the order of
        the stones in the field.

        Returns:
            None
        """
        print(" ".join(str(stone.mark) for stone in self.stones))


def main() -> None:
    """
    Main entry point for the script

    Reads the input from a file, processes data and prints the solution to
    both parts of the problem.

    Returns:
        None
    """
    txt_input = read_input(False).strip()

    magic_field = MagicField.from_text(txt_input)

    magic_field.evolve_to_n(25)

    print(f"Problem 1: {magic_field.total_stones()}")

    magic_field.evolve_to_n(75)

    print(f"Problem 2: {magic_field.total_stones()}")


if __name__ == "__main__":
    main()
