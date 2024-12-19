"""
Advent of Code 2024
Day 9

Full problem: https://adventofcode.com/2024/day/9

A: Calculate the checksum of the disk map after compacting the disk by individual blocks

B: Calculate the checksum of the disk map after compacting the disk by block groups
"""

import heapq
from pathlib import Path

from attrs import define

INPUT_FILE = "input_day9_aoc2024.txt"
TEST_INPUT_FILE = "test_input_day9_aoc2024.txt"
OUTPUT_FILE = "output_day9_aoc2024.txt"
TEST_OUTPUT_FILE = "test_output_day9_aoc2024.txt"


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


@define
class DataBlock:
    """
    A class to represent a data block on the disk map.

    Attributes:
        id_num (int): The file index of the data block.
    """

    id_num: int


@define(order=True)
class BlockGroup:
    """
    A group of neighbouring data blocks on the disk map with identical block values.

    Attributes:
        size (int): The size of the groupin data blocks.
        data (DataBlock | None): The data contained in the data blocks.
    """

    size: int
    data: DataBlock | None


class Disk:
    """
    A class to represent a disk with a given map string.

    Attributes:
        map_str (str): The disk map string used to initialize the Disk object.
        disk_size (int): The size of the processed disk map.
    """

    def __init__(self, map_str: str) -> None:
        """
        Initialize the Disk object with a given disk map string.

        Args:
            map_str (str): The disk map string to initialize the Disk object with.
            disk_size_blocks (int): The size of the processed disk map in data blocks.

        Returns:
            None
        """
        self.map_str = map_str
        self.disk_blocksize = self.process_disk_blockmap()
        self.disk_groups = self.process_disk_groupmap()

    def process_disk_blockmap(self) -> int:
        """
        Process a disk map into a list of DataBlock objects

        The disk map is processed such that each character in the string is
        converted into a number. If the character index is even, the number is
        divided by two and this value represents its index as a DataBlock.
        If the character index is odd, the number represents empty space
        and is stored as None.

        Args:
            None

        Returns:
            int: The size of the processed disk map
        """
        self.disk_blocks: list[DataBlock | None] = []
        self.empty_block_ids: list[int] = []
        head_idx = 0

        for idx, char in enumerate(self.map_str):
            value = int(char)

            # Note: values alternate between data blocks and empty spaces
            data = DataBlock(idx // 2) if idx % 2 == 0 else None

            if data is None:
                self.empty_block_ids += range(head_idx, head_idx + value)

            head_idx += value
            self.disk_blocks += [data] * value

        return len(self.disk_blocks)

    def compress_blocks(self) -> int:
        """
        Compress the disk by filling in empty spaces with DataBlocks from the back

        Args:
            None

        Returns:
            int: The number of empty spaces filled during compression
        """
        replace_count = 0

        heapq.heapify(self.empty_block_ids)

        for idx, block in enumerate(self.disk_blocks[::-1]):
            if block is None:
                continue

            # Get block index and lowest index of empty space
            block_idx = self.disk_blocksize - idx - 1
            empty_idx = heapq.heappop(self.empty_block_ids)

            # Break if further compression is not possible
            if block_idx < empty_idx:
                break

            # Swap empty space with datablock
            self.disk_blocks[empty_idx], self.disk_blocks[block_idx] = block, None

            # Add index of replaced block to empty spaces
            heapq.heappush(self.empty_block_ids, block_idx)

            replace_count += 1

        return replace_count

    def calc_block_checksum(self) -> int:
        """
        Calculate the checksum of the disk blockmap

        The checksum is calculated by multiplying the index of each data block
        by its index in the blockmap.

        Args:
            None

        Returns:
            int: The checksum of the map
        """
        return sum(
            map_idx * block.id_num
            for map_idx, block in enumerate(self.disk_blocks)
            if block is not None
        )

    def print_blockmap(self) -> None:
        """
        Prints the current state of the disk blockmap

        Prints the current state of the blockmap, where each number represents
        the index of a data block and each '.' represents a gap of free space.

        Returns:
            None
        """
        for data in self.disk_blocks:
            if isinstance(data, DataBlock):
                print(data.id_num, end="")
            else:
                print(".", end="")
        print()

    def process_disk_groupmap(self) -> list[BlockGroup]:
        """
        Process a disk map into a list of BlockGroup objects

        Each character in the disk map string is processed to create a BlockGroup
        object. The object's start index is determined by the character's index,
        its size by the character's value, and its data attribute by whether
        the character index is even or odd, where even indicates a data block
        and odd indicates empty space.

        Args:
            None

        Returns:
            list[BlockGroup]: A list of BlockGroup objects
        """
        block_groups = []

        for idx, char in enumerate(self.map_str):
            value = int(char)

            # Note: values alternate between data blocks and empty spaces
            data = DataBlock(idx // 2) if idx % 2 == 0 else None

            block_groups.append(BlockGroup(value, data))

        return block_groups

    def find_first_empty_space(self, size: int) -> int | None:
        """
        Find the first empty space with at least the given size

        Args:
            size (int): The minimum size of the empty space

        Returns:
            int| None: The index of the first empty space with at least the
            given size, or None if no empty space with the given size is found
        """
        for idx, group in enumerate(self.disk_groups):
            if group.data is None and group.size >= size:
                return idx

    def replace_blockgroup(self, group: BlockGroup) -> None:
        """
        Move a group of data blocks into a fitting group of empty space

        Args:
            group (BlockGroup): The group of data blocks to move

        Returns:
            None
        """
        # Invalid group for replacement
        if group.data is None:
            return

        # No replacement possible
        if (empty_idx := self.find_first_empty_space(group.size)) is None:
            return

        # Replacement would not result in further compression
        if (group_idx := self.disk_groups.index(group)) < empty_idx:
            return

        empty_size = self.disk_groups[empty_idx].size

        if group.size == empty_size:
            self.disk_groups[empty_idx].data = group.data
            self.disk_groups[group_idx].data = None

        elif group.size < empty_size:
            remainder = BlockGroup(empty_size - group.size, None)
            self.disk_groups[empty_idx].data = group.data
            self.disk_groups[empty_idx].size = group.size
            self.disk_groups[group_idx].data = None
            self.disk_groups.insert(empty_idx + 1, remainder)

    def compress_groups(self) -> None:
        """
        Compress the disk groupmap

        Iterates over the list of BlockGroup objects in reverse order once and
        attempts to move each group into the first fitting group of empty space.

        Returns:
            None
        """
        for group in [g for g in self.disk_groups if g.data][::-1]:
            self.replace_blockgroup(group)

    def calc_group_checksum(self) -> int:
        """
        Calculate the checksum of the disk groupmap

        The checksum is calculated by multiplying the index of each data block
        by its index in the groupmap.

        Args:
            None

        Returns:
            int: The checksum of the map
        """
        checksum = 0
        head_idx = 0
        for data in self.disk_groups:
            if isinstance(data.data, DataBlock):
                checksum += sum(
                    data.data.id_num * i for i in range(head_idx, head_idx + data.size)
                )
            head_idx += data.size
        return checksum

    def print_groupmap(self) -> None:
        """
        Prints the current state of the disk groupmap

        Prints the current state of the groupmap, where each number represents
        the index of a data block and each '.' represents a gap of free space.

        Returns:
            None
        """
        for data in self.disk_groups:
            if isinstance(data.data, DataBlock):
                print(f"{data.data.id_num}" * data.size, end="")
            else:
                print("." * data.size, end="")
        print()


def main() -> None:
    """
    Main entry point for the script

    Reads the input from a file, processes data and prints the solution to
    both parts of the problem.

    Returns:
        None
    """
    txt_input = read_input(False).strip()

    disk = Disk(txt_input)

    disk.compress_blocks()

    print(f"Problem 1: {disk.calc_block_checksum()}")

    disk.compress_groups()

    print(f"Problem 2: {disk.calc_group_checksum()}")


if __name__ == "__main__":
    main()
