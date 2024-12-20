"""
Advent of Code 2024
Day 15

Full problem: https://adventofcode.com/2024/day/15

A:

B:
"""

from collections import deque
from enum import Enum
from pathlib import Path

from attrs import define

INPUT_FILE = "input_day15_aoc2024.txt"
TEST_INPUT_FILE = "test_input_day15_aoc2024.txt"
OUTPUT_FILE = "output_day15_aoc2024.txt"
TEST_OUTPUT_FILE = "test_output_day15_aoc2024.txt"


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


class Move(Enum):
    """
    Enumeration of possible movement directions, each associated with a character.

    Attributes:
        UP (str): Represents upward movement with the character '^'.
        DOWN (str): Represents downward movement with the character 'v'.
        LEFT (str): Represents leftward movement with the character '<'.
        RIGHT (str): Represents rightward movement with the character '>'.
    """

    UP = "^"
    DOWN = "v"
    LEFT = "<"
    RIGHT = ">"

    def __init__(self, char: str) -> None:
        """
        Initialize the move enum with the given character, and set the
        corresponding (y, x) coordinate offset for the move direction.

        Args:
            char (str): The character to use for this move direction,
                must be one of "^", "v", "<", or ">"
        """
        self.char = char
        if char == "^":
            self.y, self.x = (-1, 0)
        elif char == "v":
            self.y, self.x = (1, 0)
        elif char == "<":
            self.y, self.x = (0, -1)
        elif char == ">":
            self.y, self.x = (0, 1)

    def __str__(self) -> str:
        """
        Return a string representation of this enum value, which is the single char
        used to represent the move in the input text.

        Returns:
            str: The character representation of this enum
        """
        return self.char


class Cell(Enum):
    """
    Enumeration representing different cell object types in the warehouse grid that
    can be represented by a single character.

    Attributes:
        WALL (str): Represents a wall with the character '#'.
        BOX (str): Represents a box with the character 'O'.
        ROBOT (str): Represents a robot with the character '@'.
        EMPTY (str): Represents an empty space with the character '.'.
    """

    WALL = "#"
    BOX = "O"
    ROBOT = "@"
    EMPTY = "."


@define
class Warehouse:
    grid: list[list[Cell]]
    robot_position: tuple[int, int]

    @classmethod
    def from_text(cls, text: str) -> "Warehouse":
        """
        Create a Warehouse from a text string.

        The text string should be a grid of characters, where each character
        represents the type of object at that position in the warehouse.

        The method reads the text string into a 2D array of Cell objects, and
        locates the initial position of the robot in the grid.

        Args:
            text (str): The text string to create the Warehouse from

        Returns:
            Warehouse: The created Warehouse
        """
        grid = []
        robot_position = None
        for y, line in enumerate(text.splitlines()):
            grid.append([])
            for x, char in enumerate(line):
                if isinstance(char, Cell):
                    raise ValueError(f"Invalid character: {char}")
                if char == Cell.ROBOT.value:
                    robot_position = (y, x)
                grid[-1].append(Cell(char))

        if not robot_position:
            raise ValueError("Robot position not found")

        return cls(grid, robot_position)

    def print_map(self) -> None:
        """
        Prints the current state of the warehouse grid to the console.

        Each cell in the grid is represented by its corresponding symbol
        from the ObjectType enumeration.

        Returns:
            None
        """
        for row in self.grid:
            print("".join(cell.value for cell in row))

    def find_empty_cell(self, move: Move) -> list[tuple[int, int]] | None:
        """
        Find the next empty cell in the specified move direction from the current robot position.

        The method starts from the current robot position and moves in the specified direction
        until it reaches an empty cell, or ends up at a wall (i.e. unmovable position).

        If an empty cell is found, the method returns a list of tuples representing the
        positions of all cells that can be moved in the specified direction.

        If no empty cell is found, the method returns None.

        Args:
            move (Move): The move direction to search in

        Returns:
            list[tuple[int, int]] | None: A list of tuples representing the movable positions,
                or None if no empty cell is found
        """
        movable_positions: list[tuple[int, int]] = [self.robot_position]
        next_position = self.robot_position[0] + move.y, self.robot_position[1] + move.x

        while self.grid[next_position[0]][next_position[1]] != Cell.WALL:

            movable_positions.append(next_position)
            # movable_cells.append(self.grid[next_position[0]][next_position[1]])

            if self.grid[next_position[0]][next_position[1]] == Cell.EMPTY:
                return movable_positions

            next_position = next_position[0] + move.y, next_position[1] + move.x

        return None

    def move_items(self, move: Move) -> None:
        """
        Move warehouse items (robot, boxes) in the specified direction
        and update the robot position as well as the grid accordingly.

        Args:
            move (Move): The direction to move the robot

        Returns:
            None
        """
        if not (position_to_move := self.find_empty_cell(move)):
            return

        values_to_move = deque([self.grid[p[0]][p[1]] for p in position_to_move])
        values_to_move.rotate(1)

        for p in position_to_move:
            self.grid[p[0]][p[1]] = values_to_move.popleft()

        self.robot_position = (
            self.robot_position[0] + move.y,
            self.robot_position[1] + move.x,
        )

    def calculate_box_positions(self) -> int:
        """
        Calculate the total positional value of boxes in the warehouse.

        Returns:
            int: The total positional value of boxes in the warehouse
        """
        return sum(
            100 * y + x
            for y, row in enumerate(self.grid)
            for x, cell in enumerate(row)
            if cell == Cell.BOX
        )


def main() -> None:
    """
    Main entry point for the script

    Reads the input from a file, processes data and prints the solution to
    both parts of the problem.

    Returns:
        None
    """
    test = False

    warehouse_map, robot_moves = read_input(test).strip().split("\n\n")

    warehouse = Warehouse.from_text(warehouse_map)
    moves = [Move(char) for char in robot_moves.replace("\n", "")]

    for move in moves:
        warehouse.move_items(move)

    total_box_positions = warehouse.calculate_box_positions()

    print(f"Problem 1: {total_box_positions}")

    print(f"Problem 2: ")


if __name__ == "__main__":
    main()
