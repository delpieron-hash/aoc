"""
Advent of Code 2024
Day 6

Full problem: https://adventofcode.com/2024/day/6

A: Count the number of visited cells by the guard including the start position

B: Count the number of obstacle placements that force the guard to enter an infinite loop
"""

from collections.abc import Iterator
from enum import Enum
from pathlib import Path

from attrs import define

INPUT_FILE = "input_day6_aoc2024.txt"
OUTPUT_FILE = "output_day6_aoc2024.txt"


class Colors:
    """
    ANSI color codes for printing colored text in terminal

    Contains methods to wrap a given string in ANSI color codes.
    """

    GREEN = "\033[0;32m"
    PURPLE = "\033[0;35m"
    RED = "\033[0;31m"
    CYAN = "\033[0;36m"
    BOLD = "\033[1m"
    END = "\033[0m"

    @classmethod
    def purple(cls, char: str) -> str:
        """Wrap a string in purple color"""
        return f"{cls.PURPLE}{char}{cls.END}"

    @classmethod
    def green(cls, char: str) -> str:
        """Wrap a string in green color"""
        return f"{cls.GREEN}{char}{cls.END}"

    @classmethod
    def red(cls, char: str) -> str:
        """Wrap a string in red color"""
        return f"{cls.RED}{char}{cls.END}"

    @classmethod
    def cyan(cls, char: str) -> str:
        """Wrap a string in cyan color"""
        return f"{cls.CYAN}{char}{cls.END}"

    @classmethod
    def bold(cls, char: str) -> str:
        """Wrap a string in bold font"""
        return f"{cls.BOLD}{char}{cls.END}"


class Direction(Enum):
    """
    Enumeration of possible directions for the guard
    """

    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4

    def turn_right(self) -> "Direction":
        """
        Turn the direction to the right.

        Returns:
            Direction: The direction after turning right
        """
        return Direction(self.value % 4 + 1)


class LabObject(Enum):
    """
    Enumeration of possible objects in the lab
    """

    GUARD = (1, "G", Colors.red(Colors.bold("G")))
    WALL = (2, "#", Colors.purple("#"))
    SPACE = (3, ".", Colors.green("."))
    VISITED = (4, "X", Colors.green("X"))
    OBSTACLE = (5, "O", Colors.cyan(Colors.bold("O")))
    START = (6, "S", Colors.red(Colors.bold("S")))

    def __init__(self, idx: int, display: str, color_display: str) -> None:
        """
        Initialize a LabObject.

        Args:
            idx (int): The unique integer identifier for this LabObject.
            display (str): The string to display when this LabObject is printed.
            color_display (str): The string to display when this LabObject is printed in color.

        Returns:
            None
        """
        self.id = idx
        self.display = display
        self.color_display = color_display


@define
class Cell:
    """
    A cell in the 2D array map
    """

    value: LabObject
    y: int
    x: int

    def is_visitable(self) -> bool:
        """
        Return if the cell can be visited by the lab guard

        Returns:
            bool: True if the cell is a space or visited space, False otherwise
        """
        return self.value == LabObject.SPACE or self.value == LabObject.VISITED

    def copy(self) -> "Cell":
        """
        Create a copy of the current cell instance

        Returns:
            Cell: A new instance of Cell with the same value and coordinates
        """
        return Cell(self.value, self.y, self.x)


class LabMap:
    """
    A 2D array map of LabObjects and a guard cell that can move around the map
    """

    def __init__(self, text_map: str) -> None:
        """
        Initialize the LabMap instance with the provided text map

        Args:
            text_map (str): The map as a string, separated by newlines
        """
        # Initialize the map based on input
        self.process_map(text_map)
        self.faced_obstacles: set[tuple[int, int, Direction]] = set()
        self.has_infinite_loop = False

        if not self.guard_cell or not self.guard_direction:
            raise ValueError(
                "Something went wrong with map processing: "
                "guard cell or direction not set"
            )

        # Calculate map width and height
        self.width = len(self.cell_map[0])
        self.height = len(self.cell_map)

        # Create a save of the original map and guard position
        self.original_map = self.copy_map(self.cell_map)
        self.start_cell = Cell(LabObject.START, self.guard_cell.y, self.guard_cell.x)
        self.start_direction = self.guard_direction

    def copy_map(self, cell_map: list[list[Cell]]) -> list[list[Cell]]:
        """
        Create a deep copy of the provided 2d array map

        Args:
            cell_map (list[list[Cell]]): The map to copy

        Returns:
            list[list[Cell]]: A copy of the current map
        """
        return [[cell.copy() for cell in row] for row in cell_map]

    def reset_map(self) -> None:
        """
        Reset the map to the original state

        Returns:
            None
        """
        self.cell_map = self.copy_map(self.original_map)
        self.guard_cell = Cell(LabObject.GUARD, self.start_cell.y, self.start_cell.x)
        self.guard_direction = self.start_direction
        self.faced_obstacles = set()
        self.has_infinite_loop = False

    def print_map(self, original: bool = False) -> None:
        """
        Prints the current or original state of the map to the console

        Returns:
            None
        """
        printable_map = self.original_map if original else self.cell_map
        for row in printable_map:
            print("".join(cell.value.color_display for cell in row))

    def process_map(self, txt_input: str) -> None:
        """
        Process the input into a usable 2D array map of cells
        and determine the guard direction

        Args:
            txt_input (str): Input text

        Returns:
            None
        """
        self.cell_map = []
        for row_idx, line in enumerate(txt_input.splitlines(keepends=False)):
            map_row = []
            for col_idx, char in enumerate(line):
                if char == ".":
                    object_type = LabObject.SPACE
                elif char == "#":
                    object_type = LabObject.WALL
                else:
                    object_type = LabObject.GUARD
                    self.guard_cell = Cell(object_type, row_idx, col_idx)
                    if char == ">":
                        self.guard_direction = Direction.RIGHT
                    elif char == "<":
                        self.guard_direction = Direction.LEFT
                    elif char == "^":
                        self.guard_direction = Direction.UP
                    elif char == "v":
                        self.guard_direction = Direction.DOWN

                map_row.append(Cell(object_type, row_idx, col_idx))

            self.cell_map.append(map_row)

    def is_valid_point(self, y: int, x: int) -> bool:
        """
        Check if given coordinates point to a valid point in the map

        Args:
            y (int): The y coordinate
            x (int): The x coordinate

        Returns:
            bool: True if the point is valid, False otherwise
        """
        return 0 <= x < self.width and 0 <= y < self.height

    def next_guard_cell(self) -> Cell | None:
        """
        Returns the target cell for the guard in the given direction

        Args:
            direction (Direction): The direction to move the guard

        Returns:
            Cell | None: The target cell to move to or None if it is out of bounds
        """
        if not self.guard_cell:
            raise ValueError("Guard cell is not set")

        if self.guard_direction == Direction.UP:
            target_x = self.guard_cell.x
            target_y = self.guard_cell.y - 1
        elif self.guard_direction == Direction.RIGHT:
            target_x = self.guard_cell.x + 1
            target_y = self.guard_cell.y
        elif self.guard_direction == Direction.DOWN:
            target_x = self.guard_cell.x
            target_y = self.guard_cell.y + 1
        elif self.guard_direction == Direction.LEFT:
            target_x = self.guard_cell.x - 1
            target_y = self.guard_cell.y

        if self.is_valid_point(target_y, target_x):
            return self.cell_map[target_y][target_x]

    def next_turn_cell(self) -> tuple[int, int, Direction] | None:
        """
        Moves up guard to the next cell in the given direction and returns the faced obstacle

        Args:
            direction (Direction): The direction to move the guard

        Returns:
            tuple[int, int, Direction] | None:
                The faced obstacle or None if it is out of bounds
        """
        if not self.guard_cell:
            raise ValueError("Guard cell is not set")

        if self.guard_direction == Direction.UP:
            target_x = self.guard_cell.x
            target_y = self.guard_cell.y - 1
            while (
                self.is_valid_point(target_y, target_x)
                and self.cell_map[target_y][target_x].is_visitable()
            ):
                target_y -= 1
            boundary_y, boundary_x = target_y, target_x
            last_cell = self.cell_map[target_y + 1][target_x]

        elif self.guard_direction == Direction.DOWN:
            target_x = self.guard_cell.x
            target_y = self.guard_cell.y + 1
            while (
                self.is_valid_point(target_y, target_x)
                and self.cell_map[target_y][target_x].is_visitable()
            ):
                target_y += 1
            boundary_y, boundary_x = target_y, target_x
            last_cell = self.cell_map[target_y - 1][target_x]

        elif self.guard_direction == Direction.RIGHT:
            target_x = self.guard_cell.x + 1
            target_y = self.guard_cell.y
            while (
                self.is_valid_point(target_y, target_x)
                and self.cell_map[target_y][target_x].is_visitable()
            ):
                target_x += 1
            boundary_y, boundary_x = target_y, target_x
            last_cell = self.cell_map[target_y][target_x - 1]

        elif self.guard_direction == Direction.LEFT:
            target_x = self.guard_cell.x - 1
            target_y = self.guard_cell.y
            while (
                self.is_valid_point(target_y, target_x)
                and self.cell_map[target_y][target_x].is_visitable()
            ):
                target_x -= 1
            boundary_y, boundary_x = target_y, target_x
            last_cell = self.cell_map[target_y][target_x + 1]
        else:
            raise ValueError("Invalid direction")

        if not self.is_valid_point(boundary_y, boundary_x):
            self.exit_guard(last_cell)
            return

        # Move to last visitable cell
        self.step_guard_forward(last_cell)

        return (boundary_y, boundary_x, self.guard_direction)

    def step_guard_forward(self, target_cell: Cell) -> None:
        """
        Move the guard to the target cell and update the map

        Args:
            target_cell (Cell): The target cell to move to

        Returns:
            None
        """
        if not self.guard_cell:
            raise ValueError("Guard cell is not set")

        # Set guard cell to visited space
        self.cell_map[self.guard_cell.y][self.guard_cell.x].value = LabObject.VISITED

        # Set target cell to guard and refresh guard cell
        self.cell_map[target_cell.y][target_cell.x].value = LabObject.GUARD
        self.guard_cell = target_cell

    def exit_guard(self, guard_cell: Cell) -> None:
        """
        Exit the guard from the map and indicate the start position

        Args:
            guard_cell (Cell): The current cell of the guard

        Returns:
            None
        """
        self.cell_map[guard_cell.y][guard_cell.x].value = LabObject.VISITED
        self.guard_cell = None
        self.guard_direction = None

        # Indicate guard start position
        self.cell_map[self.start_cell.y][self.start_cell.x] = self.start_cell

    def walk_guard(self) -> None:
        """
        Move the guard forward until it hits a wall or exits

        Returns:
            None
        """
        while self.guard_cell and self.guard_direction:

            # Remove guard from map if out of bounds
            if not (target_cell := self.next_guard_cell()):
                self.exit_guard(self.guard_cell)
                return

            # Turn right if target cell is an obstacle
            if not target_cell.is_visitable():
                faced_obstacle = (target_cell.y, target_cell.x, self.guard_direction)
                self.guard_direction = self.guard_direction.turn_right()

                # Exit if infinite loop
                if faced_obstacle in self.faced_obstacles:
                    self.has_infinite_loop = True
                    return

                # Add obstacle to list
                self.faced_obstacles.add(faced_obstacle)
                continue

            # Move to target cell
            self.step_guard_forward(target_cell)

    def jump_guard(self) -> None:
        """
        Move the guard forward until it hits a wall or exits

        Returns:
            None
        """
        while self.guard_cell and self.guard_direction:

            # Remove guard from map if out of bounds
            if not (faced_obstacle := self.next_turn_cell()):
                return

            if faced_obstacle in self.faced_obstacles:
                self.has_infinite_loop = True
                return

            # Add obstacle to list
            self.faced_obstacles.add(faced_obstacle)

            self.guard_direction = self.guard_direction.turn_right()

    def find_walked_cells(self) -> Iterator[Cell]:
        """
        Find all cells in the map the guard walked through not including the start position

        Returns:
            Iterator[Cell]: An iterator over all visited cells
        """
        for row in self.cell_map:
            for cell in row:
                if cell.value == LabObject.VISITED:
                    yield cell

    def count_visited(self) -> int:
        """
        Count the number of visited cells by the guard including the start position

        Returns:
            int: The number of visited cells in the map
        """
        return sum(
            1
            for row in self.cell_map
            for cell in row
            if cell.value in (LabObject.VISITED, LabObject.START)
        )

    def place_obstacle(self, cell: Cell) -> None:
        """
        Place an obstacle at the given cell

        Args:
            cell (Cell): The cell to place the obstacle

        Returns:
            None
        """
        self.cell_map[cell.y][cell.x].value = LabObject.OBSTACLE

    def count_infinite_placements(self) -> int:
        """
        Count the number of placements that force the guard to enter an infinite loop.

        Returns:
            int: The number of placements
        """
        count = 0

        for obstacle_cell in self.find_walked_cells():
            # Reset the map
            self.reset_map()

            # Place the obstacle
            self.place_obstacle(obstacle_cell)

            # Walk the map using multi-step jumps
            self.jump_guard()

            # Check if the guard entered an infinite loop
            if self.has_infinite_loop:
                count += 1

        return count


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


def main() -> None:
    """
    Main entry point for the script

    Reads the input from a file, processes data and prints the solution to
    both parts of the problem.

    Returns:
        None
    """
    txt_input = read_input()

    lab_map = LabMap(txt_input)
    lab_map.walk_guard()

    print(f"Problem 1: {lab_map.count_visited()}")

    # Note: One potential performance improvement is to keep track of the
    # changes and only restore those cells
    obstructive_position_count = lab_map.count_infinite_placements()

    print(f"Problem 2: {obstructive_position_count}")


if __name__ == "__main__":
    main()
