"""
Advent of Code 2024
Day 12

Full problem: https://adventofcode.com/2024/day/12

A: Calculate the total price of fencing all regions on the map if price is calculated as perimeter
times area

B: Calculate the total price of fencing all regions on the map if price is calculated as area
times number of sides
"""

from collections.abc import Iterator
from enum import Enum
from functools import cached_property
from itertools import pairwise
from pathlib import Path

from attrs import define, field

INPUT_FILE = "input_day12_aoc2024.txt"
TEST_INPUT_FILE = "test_input_day12_aoc2024.txt"
OUTPUT_FILE = "output_day12_aoc2024.txt"
TEST_OUTPUT_FILE = "test_output_day12_aoc2024.txt"


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


class Colors:
    """
    ANSI color codes for printing colored text in terminal

    Contains methods to wrap a given string in ANSI color codes.
    """

    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    BOLD = "\033[1m"
    END = "\033[0m"

    PALETTE = [BLACK, RED, GREEN, YELLOW, BLUE, PURPLE, CYAN]

    @classmethod
    def colored(cls, char: str) -> str:
        """
        Wraps a single ASCII character in an ANSI color code.

        The color is determined based on the character's position in
        the ascii table, cycling through a predefined palette of colors.

        Args:
            char (str): A single character to be colored.

        Returns:
            str: The input character wrapped in an ANSI color code.
        """
        if len(char) != 1:
            raise ValueError("Input must be a single character")

        color = cls.PALETTE[ord(char) % len(cls.PALETTE)]

        return f"{color}{char}{cls.END}"

    @classmethod
    def highlight(cls, char: str) -> str:
        """
        Highlight a given character in blue and bold font.

        Args:
            char: Character to be highlighted.

        Returns:
            Highlighted character.
        """
        return f"{Colors.BLUE}{Colors.BOLD}{char}{Colors.END}"


class Direction(Enum):
    """
    Enumeration representing four cardinal directions with corresponding vector movements.
    Each direction is associated with a tuple representing the change in (y, x) coordinates.
    """

    LEFT = 0, (0, -1)
    UP = 1, (-1, 0)
    RIGHT = 2, (0, 1)
    DOWN = 3, (1, 0)

    def __init__(self, index: int, direction: tuple[int, int]) -> None:
        """
        Initialize a Direction object with an index and a directional vector.

        Args:
            index (int): The index representing the direction.
            direction (tuple[int, int]): A tuple of the y and x changes for this direction.

        Returns:
            None
        """
        self.index = index
        self.y, self.x = direction

    @classmethod
    def from_index(cls, index: int) -> "Direction":
        """
        Retrieve a direction from the given index

        Args:
            index (int): The index of the direction to retrieve

        Returns:
            Direction: The direction at the given index
        """
        for direction in cls:
            if direction.index == index:
                return direction

        raise ValueError("Invalid direction index")

    @classmethod
    def iterate_counterclockwise(cls, start: "Direction") -> Iterator["Direction"]:
        """
        Iterate over all directions in a counterclockwise order from the given direction.

        Args:
            start (Direction): The direction to start from

        Yields:
            Direction: The next direction in a counterclockwise order
        """
        for i in range(len(list(Direction))):
            yield Direction.from_index((start.index - i) % 4)

    @classmethod
    def count_turns(cls, start: "Direction", end: "Direction") -> int:
        """
        Count the minimum number of turns from start to end direction.

        The number of turns is defined as the minimum of turns required
        from start to end direction either clockwise or counterclockwise.

        Args:
            start (Direction): The starting direction
            end (Direction): The ending direction

        Returns:
            int: The number of turns from start to end direction
        """
        return min((end.index - start.index) % 4, (start.index - end.index) % 4)

    def turn_right(self) -> "Direction":
        """
        Turn the direction to the right.

        Returns:
            Direction: The direction after turning right
        """
        return Direction.from_index((self.index + 1) % 4)


class PlantStatus(Enum):
    """
    Enumeration representing the different plant status types in a region.
    """

    EMPTY = "."
    OUTSIDE = "█"
    BOUNDARY = "│"
    HOLE = "@"


@define(eq=False)
class Plot:
    """
    A plot in the garden, with a location and a plant type.

    Args:
        y (int): The y-coordinate of the plot
        x (int): The x-coordinate of the plot
        plant (str): The type of plant in the plot
    """

    y: int
    x: int
    plant: str

    def __lt__(self, other: "Plot") -> bool:
        """
        Compare this plot with another plot for sorting purposes.

        Args:
            other (Plot): The other plot to compare against.

        Returns:
            bool: True if this plot is less than the other plot
            based on y-coordinate, and x-coordinate if y is the same.
        """
        return (self.y, self.x) < (other.y, other.x)


@define
class Area:
    """
    A 2D array of plots with plant that make up an area.

    Attributes:
        plot_map (list[list[Plot]]): The 2D map of plots in the area.
        width (int): The width of the area.
        height (int): The height of the area.
    """

    plot_map: list[list[Plot]]
    width: int = field(init=False)
    height: int = field(init=False)

    def __attrs_post_init__(self) -> None:
        """
        Initialize width and height of the area after plot_map has been set.

        These values are used for convenience when checking if a point is valid.

        Returns:
            None
        """
        self.width = len(self.plot_map[0])
        self.height = len(self.plot_map)

    def print_map(self) -> None:
        """
        Print the entire 2D plot map to the console

        Returns:
            None
        """
        for line in self.plot_map:
            for plot in line:
                print(Colors.colored(plot.plant), end="")
            print("\n", end="")

    def is_within_bounds(self, y: int, x: int) -> bool:
        """
        Check if the given y and x coordinates point to a valid plot on the mapO

        Args:
            y (int): The y coordinate
            x (int): The x coordinate

        Returns:
            bool: Whether the plot is within bounds
        """
        return 0 <= y < self.height and 0 <= x < self.width

    def get_adjacent_plots(self, plot: Plot) -> Iterator[Plot]:
        """
        Get the adjacent plots to a given plot and yield them

        The adjacent plots are those that share a side with the given plot.
        Does not include the given plot itself or diagonally adjacent plots.

        Args:
            plot (Plot): Plot to get adjacent plots for

        Returns:
            Iterator[Plot]: Iterator over adjacent plots
        """
        for y, x in [
            (plot.y - 1, plot.x),
            (plot.y, plot.x - 1),
            (plot.y, plot.x + 1),
            (plot.y + 1, plot.x),
        ]:
            if self.is_within_bounds(y, x):
                yield self.plot_map[y][x]

    def get_bounding_plots(self, plot: Plot) -> Iterator[Plot]:
        """
        Get the boundary plots to a given plot and yield them

        The boundary plots are those that share either a side
        or a corner with the given plot. Its the adjacent plots
        plus the diagonally adjacent plots.

        Args:
            plot (Plot): Plot to get adjacent plots for

        Returns:
            Iterator[Plot]: Iterator over boundary plots
        """
        for y, x in [
            (plot.y - 1, plot.x - 1),
            (plot.y - 1, plot.x),
            (plot.y - 1, plot.x + 1),
            (plot.y, plot.x - 1),
            (plot.y, plot.x + 1),
            (plot.y + 1, plot.x - 1),
            (plot.y + 1, plot.x),
            (plot.y + 1, plot.x + 1),
        ]:
            if self.is_within_bounds(y, x):
                yield self.plot_map[y][x]

    def find_region_plots(
        self, root: Plot, region: set[Plot] | None = None
    ) -> set[Plot]:
        """
        Find all plots in the same region as the given plot

        A region is defined as all plots that are adjacent to each other and
        have the same plant type.

        Args:

        Returns:
            Region: Region that contains the plot
        """
        if region is None:
            region = set([root])

        for adjacent_plot in self.get_adjacent_plots(root):
            if adjacent_plot.plant != root.plant:
                continue

            if adjacent_plot in region:
                continue

            region.add(adjacent_plot)

            region |= self.find_region_plots(adjacent_plot, region)

        return region


@define
class Region(Area):
    """
    A 2D array of plots with plant that make up a region.

    Attributes:
        plot_map (list[list[Plot]]): The 2D map of plots in the region.
        garden_plots (set[Plot]): The set of garden plots belonging to the region
        region_plots (set[Plot]): The set of plots in the region
            with coordinates normalized to the region
        plant (str): The type of plant in the region
        width (int): The width of the region.
        height (int): The height of the region.
    """

    plot_map: list[list[Plot]]
    garden_plots: set[Plot]
    region_plots: set[Plot]
    plant: str
    width: int = field(init=False)
    height: int = field(init=False)

    def __attrs_post_init__(self) -> None:
        """
        Initialize width and height of the region after plot_map has been set.

        Fill the plots that are outside of the region with the OUTSIDE_REGION value.
        Those will be used to determine the outer boundary of the region

        Fill the plots that are inside the region with the HOLE value.
        Those will be used to determine the subregions contained by this region

        Returns:
            None
        """
        super().__attrs_post_init__()
        self.fill_exterior()
        self.fill_interior()

    @classmethod
    def from_plots(cls, garden_plots: set[Plot], plant: str) -> "Region":
        """
        Create a region area from a set of plots

        Args:
            garden_plots (set[Plot]): The set of garden plots belonging to the region
            plant (str): The type of plant in the region

        Returns:
            RegionArea: The region area
        """
        plot_yxs = [(plot.y, plot.x) for plot in garden_plots]

        y_sorted = sorted(plot_yxs, key=lambda p: p[0])
        min_y = y_sorted[0][0]
        max_y = y_sorted[-1][0]

        x_sorted = sorted(plot_yxs, key=lambda p: p[1])
        min_x = x_sorted[0][1]
        max_x = x_sorted[-1][1]

        normalised_map: list[list[Plot]] = []
        normalised_plots: set[Plot] = set()

        for normalised_y, y in enumerate(range(min_y - 1, max_y + 2)):
            normalised_map.append([])
            for normalised_x, x in enumerate(range(min_x - 1, max_x + 2)):
                if (y, x) in plot_yxs:
                    normalised_plot = Plot(normalised_y, normalised_x, plant)
                    normalised_map[-1].append(normalised_plot)
                    normalised_plots.add(normalised_plot)
                else:
                    normalised_map[-1].append(
                        Plot(normalised_y, normalised_x, PlantStatus.EMPTY.value)
                    )

        return cls(normalised_map, garden_plots, normalised_plots, plant)

    @cached_property
    def size(self) -> int:
        """
        The size of the region.

        This is the number of planted plots of the region.
        """
        return len(self.garden_plots)

    @property
    def perimeter_length(self) -> int:
        """
        The length of the perimeter of the region.

        This is the number of sides of garden plots in the region that touch
        or are adjacent to another region (with another plant type) in the garden.

        Returns:
            int: The length of the perimeter
        """
        return sum(
            4
            - sum(
                1
                for adjacent_plot in self.get_adjacent_plots(p)
                if adjacent_plot.plant == self.plant
            )
            for p in self.region_plots
        )

    @property
    def perimeter_price(self) -> int:
        """
        The total price of fence required for this region based on perimeter length.

        This is the product of the region's size and total perimeter length.

        Returns:
            int: The perimeter-based price of fencing
        """
        return self.size * self.perimeter_length

    @property
    def sides(self) -> int:
        """
        The total number of sides of the region, including both the exterior and
        all interior sides.

        Returns:
            int: The total number of sides of the region
        """
        return self.outer_sides + self.inner_sides

    @property
    def sides_price(self) -> int:
        """
        The total price of fence required for this region based on side count.

        This is the product of the region's size and total number of sides.
        """
        return self.size * (self.outer_sides + self.inner_sides)

    @property
    def inner_regions(self) -> list["Region"]:
        """
        Return the subregions of the region.

        Returns:
            list["RegionArea"]: The subregions of the region
        """
        inner_regions: list[Region] = []
        visited_plots: set[Plot] = set()

        for line in self.plot_map:
            for plot in line:

                if plot.plant != PlantStatus.HOLE.value:
                    continue

                if plot in visited_plots:
                    continue

                subregion = Region.from_plots(
                    self.find_region_plots(plot), PlantStatus.HOLE.value
                )

                visited_plots |= subregion.garden_plots
                inner_regions.append(subregion)

        return inner_regions

    @property
    def inner_sides(self) -> int:
        """
        Count the number of sides of the region that are adjacent to the interior

        Returns:
            int: The number of sides of the region
        """
        return sum(region.outer_sides for region in self.inner_regions)

    @property
    def outer_sides(self) -> int:
        """
        Count the number of sides of the region that are adjacent to the exterior

        Returns:
            int: The number of sides of the region
        """
        # Start at the second boundary plot (on top of first region plot) adn go clockwise
        start_plot = sorted(self.boundary_plots)[1]
        start_direction = Direction.RIGHT

        plot = start_plot
        direction = start_direction

        boundary_turns = [start_direction]
        while True:
            next_plot, next_direction = self.next_boundary_plot(plot, direction)
            boundary_turns.append(next_direction)
            plot = next_plot
            direction = next_direction

            if plot == start_plot:
                break

        return sum(Direction.count_turns(a, b) for a, b in pairwise(boundary_turns))

    @cached_property
    def boundary_plots(self) -> set[Plot]:
        """
        Return the plots that are on the boundary of the region.

        Returns:
            set[Plot]: The plots that are on the boundary of the region
        """
        return {
            plot for line in self.plot_map for plot in line if self.is_boundary(plot)
        }

    def print_boundary_map(self) -> None:
        """
        Print the map of the region with boundary plots marked.

        Prints the map of the region with plots on the boundary marked with
        the PlantStatus.BOUNDARY.value character, and other plots marked with
        the plant type.

        Returns:
            None
        """
        for line in self.plot_map:
            for plot in line:
                if plot in self.boundary_plots:
                    print(Colors.colored(PlantStatus.BOUNDARY.value), end="")
                else:
                    print(Colors.colored(plot.plant), end="")
            print("\n", end="")

    def is_boundary(self, plot: Plot) -> bool:
        """
        Check if the region is a boundary region

        Returns:
            bool: True if the region is a boundary region, False otherwise
        """
        if plot.plant != PlantStatus.OUTSIDE.value:
            return False

        for plot in self.get_bounding_plots(plot):
            if plot in self.region_plots:
                return True

        return False

    def fill_exterior(self, start: Plot | None = None) -> None:
        """
        Fill the exterior of the region starting from a given plot

        Args:
            start (Plot): The plot to start filling with

        Returns:
            None
        """
        if start is None:
            # Top left corner always external due to normalization
            start = self.plot_map[0][0]

        for adjacent_plot in self.get_adjacent_plots(start):
            if adjacent_plot.plant != PlantStatus.EMPTY.value:
                continue

            adjacent_plot.plant = PlantStatus.OUTSIDE.value
            self.fill_exterior(adjacent_plot)

    def fill_interior(self) -> None:
        """
        Fill the interior holes of the region

        Returns:
            None
        """
        for line in self.plot_map:
            for plot in line:
                if plot.plant == PlantStatus.EMPTY.value:
                    plot.plant = PlantStatus.HOLE.value

    def next_boundary_plot(
        self, start: Plot, facing: Direction
    ) -> tuple[Plot, Direction]:
        """
        Find the next plot on the boundary of the region in a counterclockwise order.

        Starting from the given plot and direction, this method finds the next plot
        along the boundary by iterating counterclockwise. If a boundary plot is found,
        it returns the plot and the direction to face.

        Args:
            start (Plot): The plot to start from.
            facing (Direction): The current facing direction.

        Returns:
            tuple[Plot, Direction]: A tuple containing the next boundary plot and the
            direction to face.

        Raises:
            ValueError: If no boundary plot is found.
        """

        for direction in Direction.iterate_counterclockwise(facing.turn_right()):
            next_plot = self.plot_map[start.y + direction.y][start.x + direction.x]
            if next_plot in self.boundary_plots:
                return next_plot, direction

        raise ValueError("No boundary plot found")


@define
class Garden(Area):
    """
    A 2D array of plots with plant that make up a garden.
    The garden is divided into regions of the same plant type.

    Attributes:
        plot_map (list[list[Plot]]): The 2D map of plots in the garden.
        width (int): The width of the garden.
        height (int): The height of the garden.
        regions (list[Region]): The list of regions in the garden.
        regioned_plots (set[Plot]): The set of plots in the regions.
    """

    plot_map: list[list[Plot]]
    width: int = field(init=False)
    height: int = field(init=False)

    @classmethod
    def from_text(cls, text: str) -> "Garden":
        """
        Create a garden from text input

        Args:
            text (str): Text input

        Returns:
            Garden: Garden object
        """
        plot_map = []
        for y, line in enumerate(text.splitlines()):
            plot_map.append([])
            for x, plot in enumerate(line):
                plot_map[-1].append(Plot(y, x, plot))

        return cls(plot_map)

    @cached_property
    def regions(self) -> list[Region]:
        """
        Find all regions in the garden and calculate their perimeter

        Returns:
            list[RegionArea]: List of regions
        """
        regions: list[Region] = []
        visited_plots: set[Plot] = set()

        for line in self.plot_map:
            for plot in line:

                # Skip plots that are already part of a region
                if plot in visited_plots:
                    continue

                # Find and set up the region that the plot is in
                region = Region.from_plots(self.find_region_plots(plot), plot.plant)

                visited_plots |= region.garden_plots
                regions.append(region)

        return regions


def main() -> None:
    """
    Main entry point for the script

    Reads the input from a file, processes data and prints the solution to
    both parts of the problem.

    Returns:
        None
    """
    txt_input = read_input(False).strip()

    garden = Garden.from_text(txt_input)

    p1_garden_fencing_cost = sum(region.perimeter_price for region in garden.regions)
    print(f"Problem 1: {p1_garden_fencing_cost}")

    p2_garden_fencing_cost = sum(region.sides_price for region in garden.regions)
    print(f"Problem 2: {p2_garden_fencing_cost}")


if __name__ == "__main__":
    main()
