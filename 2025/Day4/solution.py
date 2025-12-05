"""
Advent of Code 2025
Day 4

Full problem: https://adventofcode.com/2025/day/4

A: Count the number of paper rolls (@) on a grid that have less than 4 other
paper rolls in adjacent positions.

B: Count the total number of paper rolls that can be removed from the grid if any time
a paper roll has less than 4 adjacent paper rolls it is replaced with empty space (.)
"""

from enum import StrEnum
from pathlib import Path
from typing import NewType

from attrs import define, field

INPUT_FILE = "input.txt"
TEST_INPUT_FILE = "test_input.txt"


Position = NewType("Position", tuple[int, int])


class Cell(StrEnum):
    """Items that can occupy any cell position on the floor grid."""

    EMPTY = "."
    PAPER = "@"


@define
class FloorMap:
    """A 2D array grid of various cell items creating a floorplan."""

    # * Note: The list remains static, position updates are not reflected.
    grid: list[list[Cell]]

    # Derived attributes
    max_y: int = field(init=False)
    max_x: int = field(init=False)
    paper_positions: set[Position] = field(init=False)

    def __attrs_post_init__(self) -> None:
        """
        Calculates and sets the maximum y (height) and x (width) attributes
        and collects the position (x, y) of all paper items of the grid as a set.

        The actions are performed only once, after the 'grid' has been initialized.

        Returns:
            None
        """

        if not self.grid:
            self.max_x = 0
            self.max_y = 0
            return

        self.max_x = len(self.grid[0]) - 1
        self.max_y = len(self.grid) - 1
        self.paper_positions = {
            Position((col_idx, row_idx))
            for row_idx, row in enumerate(self.grid)
            for col_idx, cell in enumerate(row)
            if cell == Cell.PAPER
        }

    def has_less_than_4_adjacent_papers(self, position: Position) -> bool:
        """
        Determine if the cell at the position has less than 4 papers next to it.

        Args:
            position (Position): X and y coordinates as a position tuple
                for which the neighbouring paper positions should be counted.

        Returns:
            bool: True if the position has less than 4 adjacent papers, False otherwise.
        """
        px, py = position
        adjacent_positions = (
            (px - 1, py - 1),
            (px - 1, py),
            (px - 1, py + 1),
            (px, py - 1),
            (px, py + 1),
            (px + 1, py - 1),
            (px + 1, py),
            (px + 1, py + 1),
        )
        adjacent_papers_count = 0
        for adjacent_position in adjacent_positions:
            if adjacent_position in self.paper_positions:
                adjacent_papers_count += 1

            if adjacent_papers_count >= 4:
                return False

        return True

    def get_movable_papers(self) -> set[Position]:
        """
        Returns the movable paper positions from the FloorMap grid as a set.
        A movable position has less than 4 papers in adjacent positions.

        Returns:
            set[Position]: Paper positions represented by x and y coordinates
                that have less than 4 adjacent papers as a set.
        """
        return {
            paper_position
            for paper_position in self.paper_positions
            if self.has_less_than_4_adjacent_papers(paper_position)
        }

    def remove_papers(self, removable_positions: set[Position]) -> int:
        """
        Updates the paper positions by removing the provided set of coordinates.
        Returns the count of removed position x and y tuples.

        Returns:
            int: Count of removed positions
        """
        self.paper_positions -= removable_positions
        return len(removable_positions)

    @classmethod
    def from_grid_string(cls, grid_input: list[str]) -> "FloorMap":
        """
        Converts the provided grid string plan to a 2D array of a floor plan
        and creates the FloorMap instance accordingly.

        Args:
            grid_input (list[str]): A representation of the floor map, where
                each list represents one row of the 2D grid and each string
                the various items of the grid row in positional order.

        Returns:
            FloorMap: An instance of the current class.
        """
        return cls([[Cell(item) for item in row] for row in grid_input])


def read_grid_input(input_path: Path) -> list[str]:
    """
    Extract the 2D grid map from a file.

    Args:
        input_path (Path): Path to the file input to read.

    Returns:
        list[str]: Input grid rows as a list of strings.
    """
    with open(input_path, mode="r") as f:
        return [line.strip() for line in f if line.strip()]


def main(test: bool = False) -> None:
    """
    Main entry point for the script.

    Reads the input from a file, calculates and prints the solution
    to both parts of the problem.

    Returns:
        None
    """
    input_path = Path(__file__).parent / (TEST_INPUT_FILE if test else INPUT_FILE)

    grid_input = read_grid_input(input_path)

    floormap = FloorMap.from_grid_string(grid_input)

    p1_movable = len(floormap.get_movable_papers())

    p2_removed = 0
    while removed_count := floormap.remove_papers(floormap.get_movable_papers()):
        p2_removed += removed_count

    print(f"Problem 1: {p1_movable}")

    print(f"Problem 2: {p2_removed}")


if __name__ == "__main__":
    main(False)
