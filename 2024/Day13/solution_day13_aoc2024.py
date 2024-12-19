"""
Advent of Code 2024
Day 13

Full problem: https://adventofcode.com/2024/day/13

A: Find the total optimal token cost to win all possible machine prizes

B: Find the total optimal token cost to win all possible machine prizes with 
absurdly large prize target values
"""

import re
from collections.abc import Iterator
from enum import Enum, auto
from pathlib import Path

from attrs import define, field

INPUT_FILE = "input_day13_aoc2024.txt"
TEST_INPUT_FILE = "test_input_day13_aoc2024.txt"
OUTPUT_FILE = "output_day13_aoc2024.txt"
TEST_OUTPUT_FILE = "test_output_day13_aoc2024.txt"


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


def read_machines(input_txt: str) -> Iterator[re.Match[str]]:
    """
    Iterate over all machine definitions in the input text.

    Args:
        input_txt: The text to search for machine definitions

    Yields:
        re.Match[str]: A match object for each machine definition
    """
    return re.finditer(TextPattern.MACHINE.pattern, input_txt)


class TextPattern(Enum):
    """
    Enum class for text patterns in the input text.
    """

    BUTTON = auto(), re.compile(r"Button [A|B]: X\+(\d+), Y\+(\d+)")
    TARGET = auto(), re.compile(r"Prize: X\=(\d+), Y\=(\d+)")
    MACHINE = (
        auto(),
        re.compile(
            r"(Button A: X\+\d+, Y\+\d+)\n(Button B: X\+\d+, Y\+\d+)\n(Prize: X\=\d+, Y\=\d+)"
        ),
    )

    @property
    def pattern(self):
        """
        The regular expression pattern for this text pattern.

        Returns:
            re.Pattern: The regular expression pattern
        """
        return self.value[1]


@define
class Score:
    """
    A class to represent a score with x and y coordinates.

    Attributes:
        x (int): The x coordinate value of the score.
        y (int): The y coordinate value of the score.
    """

    x: int = field(converter=int)
    y: int = field(converter=int)

    @classmethod
    def from_input(cls, input_txt: str) -> "Score":
        """
        Create a Score instance from a regex match object.

        Args:
            input_txt (str): A string containing a machine definition

        Returns:
            Score: A Score instance configured using the parsed input data
        """
        if (match := re.search(TextPattern.TARGET.pattern, input_txt)) is None:
            raise ValueError("No match for target score pattern")

        if len(values := match.groups()) != 2:
            raise ValueError("Target score pattern has incorrect number of groups")

        return cls(values[0], values[1])

    def __add__(self, score: "Score") -> "Score":
        """
        Return a new Score that is the sum of this and the other Score

        Args:
            score (Score): The other Score to add

        Returns:
            Score: A new Score with the added x and y values
        """
        return Score(self.x + score.x, self.y + score.y)

    def __sub__(self, score: "Score") -> "Score":
        """
        Return a new Score that is the difference of this and the other Score

        Args:
            score (Score): The other Score to subtract

        Returns:
            Score: A new Score with the subtracted x and y values
        """
        return Score(self.x - score.x, self.y - score.y)

    def __mul__(self, multiplier: int | float) -> "Score":
        """
        Return a new Score that is the product of this and the given multiplier

        Args:
            multiplier (int | float): The value to multiply by

        Returns:
            Score: A new Score with the multiplied x and y values
        """
        return Score(self.x * multiplier, self.y * multiplier)

    def __floordiv__(self, divisor: "Score") -> int:
        """
        Return the integer floor division of this Score by the given divisor Score.

        The result is the minimum of the floor division of the x values and
        the floor division of the y values.

        Args:
            divisor: The value to divide by

        Returns:
            int: The floor division result
        """
        return min(self.x // divisor.x, self.y // divisor.y)

    def __lt__(self, other: "Score") -> bool:
        """
        Compare this score with another score to determine if it is less than.

        Args:
            other (Score): The other score to compare against.

        Returns:
            bool: True if this score is less than the other score based on
            both x and y values.
        """
        return self.x < other.x and self.y < other.y


@define(eq=False)
class Button:
    """
    A button on a machine.

    Attributes:
        token_cost (int): The cost in tokens to press the button.
        score (Score): The score gained by pressing the button.
    """

    token_cost: int
    score: Score

    @classmethod
    def from_input(cls, cost: int, input_txt: str) -> "Button":
        if (match := re.search(TextPattern.BUTTON.pattern, input_txt)) is None:
            raise ValueError("No match for button pattern")

        if len(values := match.groups()) != 2:
            raise ValueError("Button score pattern has incorrect number of groups")

        return cls(token_cost=cost, score=Score(values[0], values[1]))

    def __add__(self, other: "Button") -> "Button":
        """
        Return a new Button that is the sum of this and the other Button

        Args:
            other (Button): The other Button to add

        Returns:
            Button: A new Button with the added token cost and score
        """
        return Button(self.token_cost + other.token_cost, self.score + other.score)

    def __lt__(self, other: "Button") -> bool:
        """
        Compare this button with another button to determine if it is less than.

        Args:
            other (Button): The other button to compare against.

        Returns:
            bool: True if this button's score is less than the other button's score.
        """
        return self.score < other.score

    def is_more_efficient(self, other: "Button") -> bool:
        """
        Determine if this button produces the larger score per token

        Compares the buttons on a score per token cost basis and return True
        if this button is more cost efficient in producing scores. Otherwise
        returns False.

        Args:
            other (Button): The other button to compare against.

        Returns:
            bool: True if this button is more cost efficient, otherwise False
        """
        token_ratio = self.token_cost / other.token_cost
        if self.score > other.score * token_ratio:
            return True

        return False

    def reach_target(
        self, start: Score, target: Score, combination: dict["Button", int]
    ) -> tuple[Score, dict["Button", int]]:
        """
        Calculate how many times this button can be pressed to reach or exceed
        the target score from a starting score, and update the combination accordingly.

        Args:
            start (Score): The initial score before pressing the button.
            target (Score): The target score to reach.
            combination (dict[Button, int]): A dictionary that keeps track of how many
                times each button is pressed.

        Returns:
            tuple: A tuple containing the new score after pressing the button and
            the updated combination dictionary.
        """
        count = (target - start) // self.score
        new_score = Score(
            start.x + self.score.x * count, start.y + self.score.y * count
        )
        combination[self] += count

        return (new_score, combination)


@define
class Equation:
    """
    A class to represent an equation composed of two buttons and a result value.

    Attributes:
        btn_a (int): The first button.
        btn_b (int): The second button.
        result (int): The result of the equation.
    """

    btn_a: int
    btn_b: int
    result: int

    def __sub__(self, other: "Equation") -> "Equation":
        """
        Return a new Equation that is the difference of this and the other Equation

        Args:
            equation (Equation): The other Equation to subtract

        Returns:
            Equation: A new Equation with subtracted component and result values
        """
        return Equation(
            self.btn_a - other.btn_a,
            self.btn_b - other.btn_b,
            self.result - other.result,
        )

    def __mul__(self, multiplier: int) -> "Equation":
        """
        Return a new Equation that is the product of this and the given multiplier

        Args:
            multiplier (int): The value to multiply by

        Returns:
            Equation: A new Eqaution with the multiplied component and result values
        """
        return Equation(
            self.btn_a * multiplier, self.btn_b * multiplier, self.result * multiplier
        )


@define
class Machine:
    """
    A class to represent a claw machine with buttons and target scores.

    Attributes:
        target (Score): The target score to reach.
        increased_target (Score): The increased target score for more challenging scenarios.
        btn_a (Button): The first button configuration.
        btn_b (Button): The second button configuration.
        winners (list[dict[Button, int]]): A list of winning button press combinations.
    """

    target: Score
    increased_target: Score = field(init=False)
    btn_a: Button
    btn_b: Button
    winners: list[dict[Button, int]] = field(factory=list)

    def __attrs_post_init__(self) -> None:
        """
        Initialize increased target based on original target score

        Returns:
            None
        """
        self.increased_target = self.target + Score(10000000000000, 10000000000000)

    @classmethod
    def from_input(cls, input_match: re.Match[str]) -> "Machine":
        """
        Create a Machine instance from a regex match object.

        The match object should contain three groups corresponding to the
        configurations of button A, button B, and the target score.

        Args:
            input_match (re.Match[str]): A regex match object containing the input data.

        Returns:
            Machine: A Machine instance configured using the parsed input data.
        """
        if len(values := input_match.groups()) != 3:
            raise ValueError("Machine pattern has incorrect number of groups")

        btn_a = Button.from_input(3, values[0])
        btn_b = Button.from_input(1, values[1])
        target = Score.from_input(values[2])

        return cls(target, btn_a, btn_b)

    def solve_btn_equations(self, increased: bool = False) -> None:
        """
        Solve for the combinations of button presses that reach the target score.

        Args:
            increased (bool, optional): Whether to use the increased target score
                or the original target score. Defaults to False.

        Returns:
            None
        """
        target = self.target if not increased else self.increased_target
        self.winners = []

        eq1 = Equation(
            self.btn_a.score.x,
            self.btn_b.score.x,
            target.x,
        )
        eq2 = Equation(
            self.btn_a.score.y,
            self.btn_b.score.y,
            target.y,
        )

        diff_eq = eq1 * eq2.btn_b - eq2 * eq1.btn_b

        if diff_eq.btn_b != 0:
            raise ValueError("Something went wrong during normalization")

        # Equations are parallel but never intersect
        if diff_eq.btn_a == 0 and diff_eq.result != 0:
            return

        # Scalar multiple equations allow for infinite solutions
        if diff_eq.btn_a == 0:
            combination = {self.btn_a: 0, self.btn_b: 0}
            efficient_btn = (
                self.btn_a if self.btn_a.is_more_efficient(self.btn_b) else self.btn_b
            )

            _, combination = efficient_btn.reach_target(
                Score(0, 0), target, combination
            )
            self.winners += [{**combination}]
            return

        btn_a = diff_eq.result / diff_eq.btn_a
        btn_b = (eq1.result - eq1.btn_a * btn_a) / eq1.btn_b

        # Negative pressing not possible
        if btn_a < 0 or btn_b < 0:
            return

        # Cannot press non-integer times
        if not (btn_a.is_integer() and btn_b.is_integer()):
            return

        self.winners += [{self.btn_a: int(btn_a), self.btn_b: int(btn_b)}]

    def find_winning_combinations(self, increased: bool = False) -> None:
        """
        Find all combinations of button presses that reach the target score
        and store them in the `winners` attribute.

        Args:
            increased (bool, optional): Whether to use the increased target score
                or the original target score. Defaults to False.

        Returns:
            None
        """
        self.winners = []
        combination = {self.btn_a: 0, self.btn_b: 0}
        target = self.target if not increased else self.increased_target

        larger_btn, smaller_btn = sorted([self.btn_a, self.btn_b])

        score, combination = larger_btn.reach_target(Score(0, 0), target, combination)
        score, combination = smaller_btn.reach_target(score, target, combination)

        for _ in range(combination[larger_btn]):
            if score == target and combination not in self.winners:
                self.winners += [{**combination}]
            else:
                score -= larger_btn.score
                combination[larger_btn] -= 1
                score, combination = smaller_btn.reach_target(
                    score, target, combination
                )

    def combination_cost(self, combination: dict[Button, int]) -> int:
        """
        Calculate the total cost of a combination of button presses.

        Args:
            combination: A dictionary mapping each button to its number of presses

        Returns:
            int: The total token cost of the combination
        """
        return sum(button.token_cost * combination[button] for button in combination)

    def lowest_cost(self):
        """
        Return the lowest cost to win the prize for this machine.

        If there are no winning combinations, return 0.

        Returns:
            int: The lowest cost to win in tokens.
        """
        if not self.winners:
            return 0

        return min(self.combination_cost(combination) for combination in self.winners)


def main() -> None:
    """
    Main entry point for the script

    Reads the input from a file, processes data and prints the solution to
    both parts of the problem.

    Returns:
        None
    """
    txt_input = read_input(False).strip()

    machines = [Machine.from_input(match) for match in read_machines(txt_input)]

    for machine in machines:
        machine.find_winning_combinations()
    p1_total_optimal_cost = sum(machine.lowest_cost() for machine in machines)
    print(f"Problem 1: {p1_total_optimal_cost}")

    for machine in machines:
        machine.solve_btn_equations(increased=True)
    p2_total_optimal_cost = sum(machine.lowest_cost() for machine in machines)
    print(f"Problem 2: {p2_total_optimal_cost}")


if __name__ == "__main__":
    main()
