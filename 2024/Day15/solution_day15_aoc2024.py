"""
Advent of Code 2024
Day 15

Full problem: https://adventofcode.com/2024/day/15

A: Count the sum of all boxes' GPS coordinates after all robot moves are completed

B: Count the sum of all boxes' GPS coordinates in the scaled-up larger warehouse
"""

from collections import deque
from enum import Enum
from pathlib import Path

from attrs import define, field

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


def write_output(output: str, test: bool = False) -> None:
    """
    Write output to file

    Args:
        output (str): Output string to write to file
        test (bool): Whether to use the test output file
    """
    output_name = TEST_OUTPUT_FILE if test else OUTPUT_FILE
    output_src = Path(Path(__file__).parent / output_name)

    with open(output_src, "w") as f:
        f.write(output)


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
        match char:
            case "^":
                self.y, self.x = (-1, 0)
            case "v":
                self.y, self.x = (1, 0)
            case "<":
                self.y, self.x = (0, -1)
            case ">":
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
    BOX_LEFT = "["
    BOX_RIGHT = "]"


@define
class Warehouse:
    """
    A class representing a warehouse grid with a robot and boxes.

    Attributes:
        grid (list[list[Cell]]): The 2D grid representing the warehouse layout.
        robot_position (tuple[int, int]): The coordinates of the robot in the grid.
        double_grid (list[list[Cell]]): The expanded grid with duplicated cells for simulation.
        double_robot_position (tuple[int, int]): The robot position in the expanded grid.
    """

    grid: list[list[Cell]]
    robot_position: tuple[int, int]
    double_grid: list[list[Cell]] = field(init=False)
    double_robot_position: tuple[int, int] = field(init=False)

    def __attrs_post_init__(self) -> None:
        """
        Initialize the double grid after the single grid has been set.

        The double grid is the same as the single grid, but with each cell
        duplicated horizontally. This is used to simulate a more complex
        box pushing scenario, where boxes partially overlap each other.

        Returns:
            None
        """
        double_grid = []
        for row in self.grid:
            double_grid.append([])
            for cell in row:
                match cell:
                    case Cell.BOX:
                        double_grid[-1].append(Cell.BOX_LEFT)
                        double_grid[-1].append(Cell.BOX_RIGHT)
                    case Cell.ROBOT:
                        double_grid[-1].append(Cell.ROBOT)
                        double_grid[-1].append(Cell.EMPTY)
                    case _:
                        double_grid[-1].append(Cell(cell.value))
                        double_grid[-1].append(Cell(cell.value))
        self.double_grid = double_grid

        # The same height (y coordinate), but twice the width (x coordinate) for the double grid
        self.double_robot_position = self.robot_position[0], self.robot_position[1] * 2

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
                if char == Cell.ROBOT.value:
                    robot_position = (y, x)
                grid[-1].append(Cell(char))

        if not robot_position:
            raise ValueError("Robot position not found")

        return cls(grid, robot_position)

    def print_map(self, simple: bool = True) -> None:
        """
        Prints the current state of the warehouse grid to the console.

        Each cell in the grid is represented by its corresponding symbol
        from the ObjectType enumeration.

        Args:
            simple (bool): If True, print the simple grid, otherwise print the double grid

        Returns:
            None
        """
        grid_map = self.grid if simple else self.double_grid
        for row in grid_map:
            print("".join(cell.value for cell in row))

    def map_to_text(self, simple: bool = True) -> str:
        """
        Converts the warehouse grid to a text string.

        The text string is a grid of characters, where each character
        represents the type of object at that position in the warehouse.

        Args:
            simple (bool): If True, convert the simple grid, otherwise convert the double grid

        Returns:
            str: The converted text string
        """
        grid_map = self.grid if simple else self.double_grid
        return "\n".join("".join(cell.value for cell in row) for row in grid_map)

    def is_valid_map(self) -> bool:
        """
        Check if the large warehouse grid is valid according to the puzzle rules.
        Each left box must have an adjacent right box, and vice versa.

        Returns:
            bool: True if the warehouse is valid, False otherwise
        """
        for row in self.double_grid:
            for idx, cell in enumerate(row):
                if cell == Cell.BOX_LEFT and row[idx + 1] != Cell.BOX_RIGHT:
                    return False
        return True

    def find_movable_cells(
        self, start: tuple[int, int], grid: list[list[Cell]], move: Move
    ) -> list[tuple[int, int]] | None:
        """
        Find all cells that can be moved in the specified direction

        The method starts from the specified position and moves in the specified direction
        until it reaches an empty cell, or ends up at a wall (i.e. unmovable position).

        If an empty cell is found, the method returns the list of positions of all cells
        that can be moved in the specified direction.

        If no empty cell is found, the method returns None.

        Args:
            start (tuple[int, int]): The coordinates to start the search from
            grid (list[list[Cell]]): The 2D grid to search in
            move (Move): The move direction to search in

        Returns:
            list[tuple[int, int]] | None:
                The list of positions of all cells that can be moved in the specified
                direction or None if the search ends up at a wall
        """
        movable_positions = [start]
        next_position = start[0] + move.y, start[1] + move.x

        while (grid_cell := grid[next_position[0]][next_position[1]]) != Cell.WALL:

            movable_positions.append(next_position)

            if grid_cell == Cell.EMPTY:
                return movable_positions

            next_position = next_position[0] + move.y, next_position[1] + move.x

        return None

    def find_boxes_to_move(
        self,
        start_position: tuple[int, int],
        move: Move,
        boxes_to_move: set[tuple[tuple[int, int], tuple[int, int]]] | None = None,
    ) -> set[tuple[tuple[int, int], tuple[int, int]]] | None:
        """
        Find the boxes that can be moved in the specified direction from the
        specified start position.

        If a box is found, the method returns a set of tuples representing the
        left and right side positions of all boxes that can be moved in the
        specified direction.

        If no box is found, the method returns None.

        Args:
            start_position (tuple[int, int]):
                The coordinates to start the search from
            move (Move):
                The move direction to search in
            boxes_to_move (set[tuple[tuple[int, int]]] | None):
                The set of boxes collected to move

        Returns:
            set[tuple[tuple[int, int], tuple[int, int]]] | None:
                A set of tuples representing the positions of all boxes that can be
                moved in the specified direction or None if the search ends up at a
                wall
        """
        if move != Move.UP and move != Move.DOWN:
            raise ValueError("Move must be UP or DOWN to search for double width boxes")

        if boxes_to_move is None:
            boxes_to_move = set()

        next_position = start_position[0] + move.y, start_position[1] + move.x

        while True:
            match self.double_grid[next_position[0]][next_position[1]]:
                case Cell.WALL:
                    return None
                case Cell.BOX_LEFT:
                    box_part = next_position[0], next_position[1] + 1
                    boxes_to_move.add((next_position, box_part))
                    if self.find_boxes_to_move(box_part, move, boxes_to_move) is None:
                        return None
                case Cell.BOX_RIGHT:
                    box_part = next_position[0], next_position[1] - 1
                    boxes_to_move.add((box_part, next_position))
                    if self.find_boxes_to_move(box_part, move, boxes_to_move) is None:
                        return None
                case Cell.EMPTY:
                    return boxes_to_move

            next_position = next_position[0] + move.y, next_position[1] + move.x

    def p1_move_items(self, move: Move, simple: bool = True) -> None:
        """
        Move warehouse items (robot, boxes) in the specified direction
        and update the robot position as well as the grid accordingly.

        Args:
            simple (bool): If True, move the simple grid, otherwise move the double grid
            move (Move): The direction to move the robot

        Returns:
            None
        """
        grid = self.grid if simple else self.double_grid
        start = self.robot_position if simple else self.double_robot_position

        if not (positions_to_move := self.find_movable_cells(start, grid, move)):
            return

        values_to_move = deque([grid[p[0]][p[1]] for p in positions_to_move])
        values_to_move.rotate(1)

        for p in positions_to_move:
            grid[p[0]][p[1]] = values_to_move.popleft()

        if simple:
            self.robot_position = start[0] + move.y, start[1] + move.x
        else:
            self.double_robot_position = start[0] + move.y, start[1] + move.x

    def p2_move_items(self, move: Move) -> None:
        """
        Move the robot and boxes in the warehouse according to the specified move direction.

        This method handles the movement of the robot and boxes within the double grid.
        If the move direction is left or right, it uses the p1_move_items method to move
        the robot. If the direction is up or down, it moves the robot and any associated
        boxes vertically, ensuring that the boxes are moved into empty spaces from farthest
        to closest to the robot's starting position.

        Args:
            move (Move): The direction to move the robot, which can be up, down, left, or right.

        Returns:
            None
        """

        grid = self.double_grid
        start = self.double_robot_position

        # Move the robot as normal if moving left or right
        if move == Move.LEFT or move == Move.RIGHT:
            self.p1_move_items(move, simple=False)
            return

        # If moving up or down, check for movable boxes
        if (boxes_to_move := self.find_boxes_to_move(start, move)) is None:
            return

        # Move the boxes into empty spaces in the grid, from farthest to closest
        boxes = sorted(
            boxes_to_move,
            key=lambda b: b[0][0],
            reverse=True if move == Move.DOWN else False,
        )

        for left, right in boxes:
            grid[left[0] + move.y][left[1] + move.x] = Cell.BOX_LEFT
            grid[right[0] + move.y][right[1] + move.x] = Cell.BOX_RIGHT
            grid[left[0]][left[1]], grid[right[0]][right[1]] = Cell.EMPTY, Cell.EMPTY

        next_robot = start[0] + move.y, start[1] + move.x
        grid[next_robot[0]][next_robot[1]] = Cell.ROBOT
        grid[start[0]][start[1]] = Cell.EMPTY
        self.double_robot_position = next_robot

    def calculate_box_positions(self, simple: bool = True) -> int:
        """
        Calculate the total positional value of boxes in the warehouse.

        Args:
            simple (bool): If True, calculate the simple grid,
                otherwise calculate the double grid

        Returns:
            int: The total positional value of boxes in the warehouse
        """
        grid = self.grid if simple else self.double_grid
        value_cell = Cell.BOX if simple else Cell.BOX_LEFT

        return sum(
            100 * y + x
            for y, row in enumerate(grid)
            for x, cell in enumerate(row)
            if cell == value_cell
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
        warehouse.p1_move_items(move)
        warehouse.p2_move_items(move)

    print(f"Problem 1: {warehouse.calculate_box_positions()}")

    print(f"Problem 2: {warehouse.calculate_box_positions(False)}")


if __name__ == "__main__":
    main()
