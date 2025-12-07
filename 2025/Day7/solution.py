"""
Advent of Code 2025
Day 7

Full problem: https://adventofcode.com/2025/day/7

A: Count the number of times the tachyon particle's movement downwards is split
in the manifold due to a collision with a splitter object in its line of movement.

B: Count the number of alternative paths of movement made by the tachyon particle
moving downwards in all alternative timelines created by the collision with splitters.
"""

from collections import defaultdict
from collections.abc import Iterator, Mapping
from enum import StrEnum
from pathlib import Path

from attrs import define

INPUT_FILE = "input.txt"
TEST_INPUT_FILE = "test_input.txt"


class ManifoldItem(StrEnum):
    """Items that occupy space within the manifold."""

    EMPTY_SPACE = "."
    SPLITTER = "^"
    START = "S"
    TACHYON_BEAM = "|"


@define(frozen=True)
class ParticleTimeline:
    """
    A tachyon particle defined by its count in various alternative timelines.

    Attributes:
        count (int): Number of timelines the particle exists in. 0 by default.
    """

    count: int = 0

    def __add__(self, other: "ParticleTimeline") -> "ParticleTimeline":
        """
        Left side addition operator overload for joining particle timeline counts.
        Particles are joined by adding their timeline counts together.

        Returns:
            ParticleTimeline: A new instance with a sum of the timeline count values.
        """
        return ParticleTimeline(self.count + other.count)

    __radd__ = __add__


@define
class TachyonManifold:
    """
    Manifold space for a multi-timeline tachyon instance
    represented by a mapping of particle positions and timeline counts.

    Attributes:
        timelines (defaultdict[int, ParticleTimeline]):
            Dictionary mapping of horizontal positions in a cross-section of manifold
            space as integers to the timelines a particle exists there.

        min_bound (int | None):
            Minimum position value that a particle can take in the manifold space.
            None by default.

        max_bound (int | None):
            Maximum position value that a particle can take in the manifold space.
            None by default.

        split_count (int):
            Number of times a split of timelines happen due to collisions of the
            tachyon particle with splitters in the manifold. 0 by default.
    """

    timelines: defaultdict[int, ParticleTimeline]
    min_bound: int | None = None
    max_bound: int | None = None
    split_count: int = 0

    @property
    def positions(self) -> set[int]:
        """
        Returns the position indices of all timelines belonging to this manifold.

        Returns:
            set[int]: Position indices of all particle timelines as a set of integers.
        """
        return set(self.timelines)

    @property
    def timeline_count(self) -> int:
        """
        Sums up the tachyon particle timelines of this manifold and returns the count.

        Returns:
            int: Total count of all the timelines of the tachyon particle.
        """
        return sum(timeline.count for timeline in self.timelines.values())

    def remove_timeline_at(self, position: int) -> ParticleTimeline:
        """
        Finds a timeline based on the provided position, removes and returns it.

        Args:
            position (int): Position integer of the removable particle timeline.

        Returns:
            ParticleTimeline: Actual timeline removed from the manifold.

        Raises:
            KeyError: If there is no particle at the provided position.
        """
        return self.timelines.pop(position)

    def add_timelines(self, timelines: Mapping[int, ParticleTimeline]) -> None:
        """
        Joins the provided particle timelines to the manifold's stored
        timelines at the mapped positions.

        Args:
            timelines (Mapping[int, ParticleTimeline]): Mapping of particle timelines
                to positions where they are to be joined with existing timelines.

        Returns:
            None
        """
        for idx, timeline in timelines.items():
            self.timelines[idx] += timeline

    def split_timeline_at(self, position: int) -> None:
        """
        Finds a particle timeline based on the provided position, splits it to
        multiple new timelines and increments the split counter.

        Splitting entails removing the particle timeline from its originial position
        while adding a copy of it both to left and right adjacent positions.

        Args:
            position (int): Position integer of the particle timeline to split.

        Returns:
            None

        Raises:
            KeyError: If there is no particle at the provided position.
        """
        old_timeline = self.remove_timeline_at(position)

        split_positions = [
            p
            for p in (position - 1, position + 1)
            if (self.min_bound is None or self.min_bound <= p)
            and (self.max_bound is None or p <= self.max_bound)
        ]

        self.add_timelines({idx: old_timeline for idx in split_positions})

        self.split_count += 1


def read_input_lines(input_path: Path) -> Iterator[str]:
    """
    Extracts all non-empty lines line by line from the provided file input.

    Args:
        input_path (Path): Path to the file input to read.

    Yields:
        str: A content line of the input file.
    """
    with open(input_path, mode="r") as f:
        yield from (line.strip() for line in f if line.strip())


def main(test: bool = False) -> None:
    """
    Main entry point for the script.

    Reads the input from a file, calculates and prints the solution
    to both parts of the problem.

    Args:
        test (bool): Determines if the script should be run on test input.
            By default it is false, and the production input is used.

    Returns:
        None
    """
    input_path = Path(__file__).parent / (TEST_INPUT_FILE if test else INPUT_FILE)

    lines = read_input_lines(input_path)

    first_line = next(lines)
    initial_timelines = defaultdict(
        ParticleTimeline, [(first_line.index(ManifoldItem.START), ParticleTimeline(1))]
    )

    manifold = TachyonManifold(initial_timelines, 0, len(first_line) - 1)

    for line in lines:
        for col_idx in manifold.positions:
            if line[col_idx] == ManifoldItem.SPLITTER:
                manifold.split_timeline_at(col_idx)

    print(f"Problem 1: {manifold.split_count}")

    print(f"Problem 2: {manifold.timeline_count}")


if __name__ == "__main__":
    main(False)
