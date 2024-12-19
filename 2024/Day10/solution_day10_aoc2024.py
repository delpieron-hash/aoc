"""
Advent of Code 2024
Day 10

A: Sum up the total number of hiking trails in the map leading to a distinct trailend

B: Sum up the total number of hiking trails in the map with a distinct trailpath
"""

from collections.abc import Iterator
from pathlib import Path

from attrs import define

INPUT_FILE = "input_day10_aoc2024.txt"
TEST_INPUT_FILE = "test_input_day10_aoc2024.txt"
OUTPUT_FILE = "output_day10_aoc2024.txt"
TEST_OUTPUT_FILE = "test_output_day10_aoc2024.txt"


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
class Point:
    """
    A point in the 2D trail map.

    Attributes:
        y (int): The y coordinate
        x (int): The x coordinate
        height (int): The height at the point
    """

    y: int
    x: int
    height: int


@define
class TrailMap:
    """
    A 2D trail map.

    Attributes:
        trailmap (list[list[Point]]): The 2D trail map
        width (int): The width of the trail map
        height (int): The height of the trail map
    """

    trailmap: list[list[Point]]
    width: int
    height: int

    @classmethod
    def from_text(cls, text: str) -> "TrailMap":
        """
        Create a TrailMap from a text string.

        The text string should be a grid of numbers, where each number represents
        the height of the point at that position in the trail map.

        Args:
            text (str): The text string to create the TrailMap from

        Returns:
            TrailMap: The created TrailMap
        """
        trailmap = []

        for y, line in enumerate(text.splitlines()):
            trailmap.append([])
            for x, height in enumerate(line):
                trailmap[y].append(Point(y, x, int(height)))

        return cls(trailmap, len(trailmap[0]), len(trailmap))

    def print_map(self) -> None:
        """
        Prints the trail map to the console

        Returns:
            None
        """
        for row in self.trailmap:
            for point in row:
                print(point.height, end="")
            print("\n", end="")

    def is_valid_point(self, y: int, x: int) -> bool:
        """
        Check if given coordinates are within the bounds of the trail map

        Args:
            y (int): The y coordinate
            x (int): The x coordinate

        Returns:
            bool: True if the coordinates fall within the map, False otherwise
        """
        return 0 <= y < self.height and 0 <= x < self.width

    def get_adjacent_points(self, point: Point) -> Iterator[Point]:
        """
        Get all adjacent points to a given point in the trail map

        Args:
            point (Point): The point to get adjacent points for

        Returns:
            Iterator[Point]: An iterator over all adjacent points
        """
        for y, x in (
            (point.y - 1, point.x),
            (point.y, point.x - 1),
            (point.y, point.x + 1),
            (point.y + 1, point.x),
        ):
            if not self.is_valid_point(y, x):
                continue

            yield self.trailmap[y][x]

    def find_trailheads(self) -> list[Point]:
        """Return a list of all trailheads in the trail map.

        A trailhead is defined as any point in the map with a height of 0.

        Returns:
            list[Point]: A list containing all trailhead points.
        """
        return [point for row in self.trailmap for point in row if point.height == 0]

    def get_next_step(
        self, point: Point, trailends: set[Point] | None = None
    ) -> set[Point] | None:
        """
        Explore the hiking trail from the current point recursively until reaching a trailend.

        A valid trail consists of a sequence of adjacent points, starting at a trailhead
        (height 0), with each step having a height increase of exactly 1, culminating
        at a trailend (height 9).

        If the current point is a trailend, it is added to the trailends set. If no further
        steps can be taken, return None. Otherwise, return the set of trailends reached.

        Args:
            point (Point): The starting point on the trail.
            trailends (set[Point] | None): A collection of reached trailends.

        Returns:
            set[Point] | None:
                The set of trailends reached or None if no further steps are possible.
        """
        if trailends is None:
            trailends = set()

        if point.height == 9:
            trailends.add(point)

        for adjacent_point in self.get_adjacent_points(point):
            if adjacent_point.height - point.height != 1:
                continue

            self.get_next_step(adjacent_point, trailends)

        return trailends

    def get_next_step_with_path(
        self,
        point: Point,
        path: list[Point] | None = None,
        trails: set[tuple[Point, ...]] | None = None,
    ) -> set[tuple[Point, ...]] | None:
        """
        Explore the hiking trail from a starting point, maintaining the path taken.

        The trail is a series of consecutive points beginning at a trailhead (height 0)
        and ascending in height by exactly 1 per step until reaching a trailend (height 9).

        If no further steps can be taken, return None. If a trailend is reached, return
        the set of paths traversed to reach the trailend.

        Args:
            point (Point): Current location on the trail.
            path (list[Point] | None): The path traversed to reach the current point.
            trails (set[tuple[Point, ...]] | None): Collection of completed trail paths.

        Returns:
            set[tuple[Point, ...]] | None:
                The set of paths to trailends or None if no further steps are possible.
        """
        if trails is None:
            trails = set()

        if path is None:
            path = []

        path.append(point)

        for adjacent_point in self.get_adjacent_points(point):
            if adjacent_point.height - point.height == 1:
                if adjacent_point.height == 9:
                    trails.add(tuple(path + [adjacent_point]))
                else:
                    self.get_next_step_with_path(adjacent_point, path, trails)

        return trails

    def count_head_score(self, point: Point, use_path: bool = False) -> int:
        """
        Count the trail score for a given point in the trail map.

        The trail score is the number of valid hiking trails that can be reached
        from the trailhead. A hiking trail is a sequence of adjacent points
        starting from a trailhead (height 0) with a height difference of 1 or less
        that leads to a trailend (height 9). The trail score can be calculated
        in two ways: either by counting all distinct trails (use_path = True)
        or by counting all distinct trailends (use_path = False).

        Args:
            point (Point): The point to count the trail score for
            use_path (bool): Whether to count distinct trails or trailends

        Returns:
            int: The trail score for the point
        """
        if point.height != 0:
            raise ValueError("Point is not a trailhead")

        find_trail = self.get_next_step_with_path if use_path else self.get_next_step

        if trailends := find_trail(point):
            return len(trailends)

        return 0

    def sum_map_trailscore(self, use_path: bool = False) -> int:
        """
        Sum up the total trail score of all trailheads in the trail map

        Args:
            use_path (bool): Whether to use the trail path for the count

        Returns:
            int: The total trail score of all trailheads in the trail map
        """
        return sum(
            self.count_head_score(point, use_path) for point in self.find_trailheads()
        )


def main() -> None:
    """
    Main entry point for the script

    Reads the input from a file, processes data and prints the solution to
    both parts of the problem.

    Returns:
        None
    """
    txt_input = read_input(False).strip()

    trailmap = TrailMap.from_text(txt_input)

    p1_trailscore = trailmap.sum_map_trailscore()

    print(f"Problem 1: {p1_trailscore}")

    p2_trailscore = trailmap.sum_map_trailscore(True)

    print(f"Problem 2: {p2_trailscore}")


if __name__ == "__main__":
    main()
