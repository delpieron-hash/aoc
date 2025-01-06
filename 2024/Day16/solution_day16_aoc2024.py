"""
Advent of Code 2024
Day 16

Full problem: https://adventofcode.com/2024/day/16

A: Find the score of the best (i.e. fewest turns and steps) path through the maze

B: Find the number of tiles that are part of any of the best (lowest scoring) paths
"""

import argparse
import heapq
import math
from collections.abc import Iterator
from enum import Enum
from functools import cached_property
from pathlib import Path

from attrs import define, field

INPUT_FILE = "input_day16_aoc2024.txt"
TEST_INPUT_FILE = "test_input_day16_aoc2024.txt"
OUTPUT_FILE = "output_day16_aoc2024.txt"
TEST_OUTPUT_FILE = "test_output_day16_aoc2024.txt"


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


class Colors:
    """
    ANSI color codes for printing colored text in terminal

    Contains methods to wrap a given string in ANSI color codes.
    """

    YELLOW = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    END = "\033[0m"

    @classmethod
    def purple(cls, char: str) -> str:
        """
        Wrap a string in purple color for printing to the console

        Args:
            char (str): The string to wrap

        Returns:
            str: The wrapped string
        """
        return f"{Colors.PURPLE}{char}{Colors.END}"

    @classmethod
    def blue(cls, char: str) -> str:
        """
        Wrap a string in blue color for printing to the console

        Args:
            char (str): The string to wrap

        Returns:
            str: The wrapped string
        """
        return f"{Colors.BLUE}{char}{Colors.END}"

    @classmethod
    def yellow(cls, char: str) -> str:
        """
        Wrap a string in yellow color for printing to the console

        Args:
            char (str): The string to wrap

        Returns:
            str: The wrapped string
        """
        return f"{Colors.YELLOW}{char}{Colors.END}"


class Direction(Enum):
    """
    Enumeration representing four cardinal directions with corresponding vector movements.
    Each direction is associated with a tuple representing the change in (y, x) coordinates.
    """

    EAST = (0, -1)
    NORTH = (-1, 0)
    WEST = (0, 1)
    SOUTH = (1, 0)

    @property
    def opposite(self) -> "Direction":
        """
        Get the opposite direction.

        Returns:
            Direction: The opposite direction (EAST<->WEST, NORTH<->SOUTH)
        """
        opposites = {
            Direction.EAST: Direction.WEST,
            Direction.NORTH: Direction.SOUTH,
            Direction.WEST: Direction.EAST,
            Direction.SOUTH: Direction.NORTH,
        }
        return opposites[self]

    @property
    def left(self) -> "Direction":
        """
        Get the direction to the left of the current direction.

        Returns:
            Direction: The direction to the left
        """
        left_rotations = {
            Direction.EAST: Direction.SOUTH,
            Direction.NORTH: Direction.EAST,
            Direction.WEST: Direction.NORTH,
            Direction.SOUTH: Direction.WEST,
        }
        return left_rotations[self]

    @property
    def right(self) -> "Direction":
        """
        Get the direction to the right of the current direction.

        Returns:
            Direction: The direction to the right
        """
        right_rotations = {
            Direction.EAST: Direction.NORTH,
            Direction.NORTH: Direction.WEST,
            Direction.WEST: Direction.SOUTH,
            Direction.SOUTH: Direction.EAST,
        }
        return right_rotations[self]


@define
class Distance:
    """
    A class to represent the distance from a cell to the target,
    expressed in terms of the number of turns and steps required to reach the target.
    """

    turns: int | float = math.inf
    steps: int | float = math.inf

    @property
    def score(self) -> int | float:
        """
        Calculate the score based on the number of turns and steps.

        It is computed as the number of turns multiplied by 1000,
        plus the number of steps. This provides a weighted number where
        turns are more significant than steps.

        Returns:
            int | float: The calculated score.
        """
        return (self.turns * 1000) + self.steps

    def __lt__(self, other: "Distance") -> bool:
        """
        Compare this Distance object with another to determine if it is less than.

        Args:
            other (Distance): The other Distance object to compare against.

        Returns:
            bool: True if this Distance object's score value is less than
                the other Distance object's score value.
        """
        return self.score < other.score

    def __le__(self, other: "Distance") -> bool:
        """
        Compare this Distance object with another to determine
        if it is less than or equal to.

        Args:
            other (Distance): The other Distance object to compare against.

        Returns:
            bool: True if this Distance object's score value is less than or equal to
                the other Distance object's score value.
        """
        return self.score <= other.score

    def add_turns(self, turns: int) -> "Distance":
        """
        Add the given number of turns to this Distance object.

        Args:
            turns (int): The number of turns to add.

        Returns:
            Distance: A new Distance object with the updated number of turns.
        """
        return Distance(self.turns + turns, self.steps)

    def add_steps(self, steps: int) -> "Distance":
        """
        Add the given number of steps to this Distance object.

        Args:
            steps (int): The number of steps to add.

        Returns:
            Distance: A new Distance object with the updated number of steps.
        """
        return Distance(self.turns, self.steps + steps)


@define
class DistanceMap:
    """
    A class to represent the distances in four directions from a cell in the maze.

    The distances are represented by four Distance objects, each associated with
    one of the four cardinal directions (EAST, NORTH, WEST, and SOUTH). A distance
    of a certain direction represents the minimum number of turns and steps
    required to reach the target and face the given direction.
    """

    EAST: Distance = field(factory=Distance)
    NORTH: Distance = field(factory=Distance)
    WEST: Distance = field(factory=Distance)
    SOUTH: Distance = field(factory=Distance)

    @classmethod
    def from_direction(cls, direction: Direction, distance: Distance) -> "DistanceMap":
        """
        Create a DistanceMap object from a direction and a distance.

        Args:
            direction (Direction): The direction to set the distance for.
            distance (Distance): The distance to set for the given direction.

        Returns:
            DistanceMap: A DistanceMap object with the given direction and distance.
        """
        distance_map = {
            direction.name: distance,
            direction.opposite.name: distance.add_turns(2),
            direction.left.name: distance.add_turns(1),
            direction.right.name: distance.add_turns(1),
        }

        return cls(**distance_map)

    @cached_property
    def distance(self) -> Distance:
        """
        Return the minimum distance between the east, north, west, and south directions.

        Returns:
            Distance: The minimum distance
        """
        return min(self.EAST, self.NORTH, self.WEST, self.SOUTH)

    def __lt__(self, other: "DistanceMap") -> bool:
        """
        Compare this distance map with another by their distance values to determine
        if it is less than.

        Returns True if all of the directions have a smaller value than the other.

        Args:
            other (DistanceMap): The other distance map to compare

        Returns:
            bool: True if this distance has smaller distance values
        """
        return all(
            (
                self.EAST < other.EAST,
                self.NORTH < other.NORTH,
                self.WEST < other.WEST,
                self.SOUTH < other.SOUTH,
            )
        )

    def __le__(self, other: "DistanceMap") -> bool:
        """
        Compare this distance map with another by their distance values to determine
        if it is less than or equal to.

        Returns True if any of the directions is smaller or equal to the other.

        Args:
            other (DistanceMap): The other distance map to compare

        Returns:
            bool: True if this distance has smaller distance values
        """
        return any(
            (
                self.EAST <= other.EAST,
                self.NORTH <= other.NORTH,
                self.WEST <= other.WEST,
                self.SOUTH <= other.SOUTH,
            )
        )

    def get(self, direction: Direction) -> Distance:
        """
        Get the distance for a specific direction.

        Args:
            direction (Direction): The direction to get the distance for

        Returns:
            Distance: The distance for the direction
        """
        return getattr(self, direction.name)


class Tile(Enum):
    """
    Enumeration representing different types of tiles in the maze.

    Attributes:
        WALL (str): Represents a wall with the character '#'.
        PATH (str): Represents a path with the character '.'.
        VISITED (str): Represents a visited path tile with the character 'O'.
        START (str): Represents the start tile with the character 'S'.
        END (str): Represents the end tile with the character 'E'.
    """

    WALL = "#"
    PATH = "."
    VISITED = "O"
    START = "S"
    END = "E"


@define
class Cell:
    """
    A cell in the maze.

    Attributes:
        y (int): The y-coordinate of the cell.
        x (int): The x-coordinate of the cell.
        tile (Tile): The tile type of the cell.
        distance_map (DistanceMap): Distance profile from the start of the maze.
    """

    y: int
    x: int
    tile: Tile
    distance_map: DistanceMap = field(factory=DistanceMap)

    @property
    def coordinates(self) -> tuple[int, int]:
        """
        Get the coordinates of the cell.

        Returns:
            tuple[int, int]: The coordinates of the cell
        """
        return self.y, self.x


@define
class CellPath:
    """
    A path through the maze consisting of a set of visited cells.

    Attributes:
        position (Cell): The current cell in the path.
        visited (set[tuple[int, int]]):
            The set of coordinates of cells that have been visited in this path.
        distance_map (DistanceMap):
            The distance from the start of the maze to the current cell position.
    """

    position: Cell
    visited: set[tuple[int, int]] = field(factory=set)
    distance_map: DistanceMap = field(factory=DistanceMap)

    def __lt__(self, other: "CellPath") -> bool:
        """
        Compare two cell paths by their distance from the start of the maze.

        Args:
            other (CellPath): The other cell path to compare

        Returns:
            bool: True if this cell path is closer to the start than the other cell path
        """
        return self.distance_map < other.distance_map

    def __le__(self, other: "CellPath") -> bool:
        """
        Compare two cell paths by their distance from the start of the maze.

        Args:
            other (CellPath): The other cell path to compare

        Returns:
            bool: True if this cell path is closer to or at the same distance
                as the other cell path
        """
        return self.distance_map <= other.distance_map


@define
class Maze:
    """
    A 2D grid of cells representing the maze.

    The maze is defined by a list of lists of cells, where each cell is represented
    by a tile and a distance map. The start and end of the maze are also defined.

    Attributes:
        maze (list[list[Cell]]): The 2D grid of cells representing the maze
        start (Cell): The start cell of the maze
        end (Cell): The end cell of the maze
        width (int): The width of the maze
        height (int): The height of the maze
        best_paths (list[set[tuple[int, int]]]): The best paths through the maze
    """

    maze: list[list[Cell]]
    start: Cell
    end: Cell
    width: int = field(init=False)
    height: int = field(init=False)
    best_paths: list[set[tuple[int, int]]] = field(factory=list)

    def __attrs_post_init__(self) -> None:
        """
        Initialize width and height of the maze after maze has been set.

        These values are used for convenience when checking if a cell is valid.

        Returns:
            None
        """
        self.width = len(self.maze[0])
        self.height = len(self.maze)

    @classmethod
    def from_text(cls, text: str) -> "Maze":
        """
        Create a Maze from a text string.

        The text string should be a grid of characters, where each character
        represents the type of object at that position in the maze.

        Args:
            text (str): The text string to create the Maze from

        Returns:
            Maze: The created Maze
        """
        maze = []
        for y, line in enumerate(text.splitlines()):
            maze.append([])
            for x, char in enumerate(line):
                cell = Cell(y, x, Tile(char))
                if char == Tile.START.value:
                    start_cell = cell
                elif char == Tile.END.value:
                    end_cell = cell
                maze[-1].append(cell)

        if not start_cell or not end_cell:
            raise ValueError("Start or end cell not found")

        return cls(maze, start_cell, end_cell)

    def print_map(self, path_cells: set[tuple[int, int]] | None = None) -> None:
        """
        Prints the current state of the maze to the console.

        Each cell in the maze is represented by its corresponding symbol
        from the Tile enumeration.

        Args:
            path_cells (set[tuple[int, int]] | None):
                The cells that are part of the path

        Returns:
            None
        """
        if path_cells is None:
            path_cells = set.union(*self.best_paths)
        for row in self.maze:
            for cell in row:
                if cell.tile == Tile.WALL:
                    print(Colors.blue(cell.tile.value), end="")
                elif cell.tile == Tile.START or cell.tile == Tile.END:
                    print(Colors.purple(cell.tile.value), end="")
                elif (cell.y, cell.x) in path_cells:
                    print(Colors.yellow(Tile.VISITED.value), end="")
                else:
                    print(cell.tile.value, end="")
            print("\n", end="")

    def is_within_bounds(self, y: int, x: int) -> bool:
        """
        Check if the given cell is within the bounds of the maze.

        Args:
            y (int): The y coordinate of the cell
            x (int): The x coordinate of the cell

        Returns:
            bool: True if the cell is within the bounds of the maze, False otherwise
        """
        return 0 <= y < self.height and 0 <= x < self.width

    def get_adjacent_cells(self, cell: Cell) -> Iterator[tuple[Direction, Cell]]:
        """
        Get all adjacent cells plus their directions to the given cell and yield them

        Args:
            cell (Cell): The cell to get adjacent cells for

        Returns:
            Iterator[tuple[Direction, Cell]]:
                An iterator over all adjacent cells and their directions
        """
        for direction in Direction:
            change_y, change_x = direction.value
            y, x = cell.y + change_y, cell.x + change_x
            if not self.is_within_bounds(y, x):
                continue
            if self.maze[y][x].tile != Tile.WALL:
                yield direction, self.maze[y][x]

    def find_optimal_paths(self) -> None:
        """
        Find the lowest cost paths from the start cell to the end cell in the maze.

        Uses a priority queue to find the lowest cost path to the end cell.

        Returns:
            None
        """
        path_queue: list[CellPath] = []
        best_path = CellPath(self.end)

        start_path = CellPath(
            self.start,
            {self.start.coordinates},
            DistanceMap().from_direction(Direction.EAST, Distance(0, 0)),
        )

        heapq.heappush(path_queue, start_path)

        while path_queue:
            current_path = heapq.heappop(path_queue)

            # Gets rid of paths that are already worse
            if current_path > best_path:
                continue

            # Check if path is complete
            if current_path.position == self.end:
                # * Check if lowest cost path is better
                if current_path.distance_map.distance < best_path.distance_map.distance:
                    best_path = current_path
                    self.best_paths = [current_path.visited]
                elif (
                    current_path.distance_map.distance
                    == best_path.distance_map.distance
                ):
                    self.best_paths.append(current_path.visited)
                continue

            # Explore possible moves to next cell
            for direction, cell in self.get_adjacent_cells(current_path.position):

                # Skip visited cells
                if cell.coordinates in current_path.visited:
                    continue

                next_distance = DistanceMap().from_direction(
                    direction, current_path.distance_map.get(direction).add_steps(1)
                )

                # Don't explore paths that can't be better in any direction
                if next_distance > cell.distance_map:
                    continue

                # Update cell distance if current path is better
                elif next_distance < cell.distance_map:
                    cell.distance_map = next_distance

                # Add path to next cell to queue if it can be better
                new_path = CellPath(
                    cell, current_path.visited | {cell.coordinates}, next_distance
                )

                if new_path <= best_path:
                    heapq.heappush(path_queue, new_path)


def main(test_mode: bool = False) -> None:
    """
    Main entry point for the script

    Reads the input from a file, processes data and prints the solution to
    both parts of the problem.

    Args:
        test_mode (bool, optional):
            Whether to use the test input. Defaults to False.

    Returns:
        None
    """
    maze = Maze.from_text(read_input(test_mode))

    maze.find_optimal_paths()

    best_path_cells = set.union(*maze.best_paths)

    print(f"Problem 1: {maze.end.distance_map.distance.score}")

    print(f"Problem 2: {len(best_path_cells)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", help="Use the test input", action="store_true")
    args = parser.parse_args()
    main(args.test)
