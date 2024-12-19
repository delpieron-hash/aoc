"""
Advent of Code 2024
Day 3

A: Find the multiplications with correct syntax and sum the results

B: Find the correct multiplications that are enabled by contextual instructions
"""

import re
from pathlib import Path

INPUT_FILE = "input_day3_aoc2024.txt"


#########################
# Version 1 (regex)
#########################
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


def find_mul_instructions(text: str) -> list[str]:
    """
    Find all multiplication instructions in the given text

    Args:
        text (str): Text to search for multiplication instructions

    Returns:
        list[str]: List of multiplication instructions
    """
    # Pattern to match a valid multiplication instructions, e.g. mul(44,46)
    mul_pattern = re.compile(r"(mul\(\d+,\d+\))")

    return re.findall(mul_pattern, text)


def process_multiplication(instruction: str) -> int:
    """
    Process a multiplication instruction and return the result

    Args:
        instruction (str): Multiplication instruction

    Returns:
        int: Result of the multiplication
    """
    # Pattern to match the factors, e.g. mul(44,46) -> 44, 46
    num_pattern = re.compile(r"mul\((\d+),(\d+)\)")

    if not (match := num_pattern.match(instruction)):
        raise ValueError("Invalid multiplication instruction")

    return int(match.group(1)) * int(match.group(2))


#########################
# Version 2 (tokenizer)
#########################

from enum import Enum
from typing import Any

from attrs import define


class TokenType(Enum):
    """Enumeration of possible token types for parsing expressions."""

    NUMBER = "number"
    COMMA = "comma"
    FUNCTION_MUL = "mul"
    FUNCTION_DO = "do"
    FUNCTION_DONT = "don't"
    LPAREN = "lparen"
    RPAREN = "rparen"
    APOSTROPHE = "apostrophe"
    UNKNOWN = "unknown"


@define
class Token:
    """
    Class to represent a token in an expression.

    The token will have a type, a value and a position.

    Attributes:
        type (TokenType): The type of the token.
        value (str): The value of the token.
        position (int): The position of the token in the expression.
    """

    type: TokenType
    value: str
    position: int


class Tokenizer:
    """
    Class to tokenize a given expression.

    The Tokenizer takes a given expression and splits it into
    individual tokens. The tokens are then stored in a list
    which can be accessed by calling the `tokens` property.

    Attributes:
        text (str): The source text to tokenize.
        position (int): The current position in the source text.
        tokens (list[Token]): The list of tokens found in the source text.
    """

    def __init__(self, text: str) -> None:
        """
        Initialize a Tokenizer object.

        Args:
            text (str): The source text to tokenize.

        Returns:
            None
        """
        self.text = text
        self.position = 0
        self.tokens: list[Token] = []

    def tokenize(self) -> list[Token]:
        """
        Tokenize the source text and store the tokens in a list.

        Returns:
            list[Token]: The list of tokens found in the source text.
        """
        while self.position < len(self.text):
            char = self.text[self.position]

            if char.isdigit():
                self._handle_number()

            elif char.isalpha():
                self._handle_function_word()

            elif char == ",":
                self.tokens.append(Token(TokenType.COMMA, char, self.position))
                self.position += 1

            elif char == "(":
                self.tokens.append(Token(TokenType.LPAREN, char, self.position))
                self.position += 1

            elif char == ")":
                self.tokens.append(Token(TokenType.RPAREN, char, self.position))
                self.position += 1

            elif char == "'":
                self.tokens.append(Token(TokenType.APOSTROPHE, char, self.position))
                self.position += 1

            else:
                self.tokens.append(Token(TokenType.UNKNOWN, char, self.position))
                self.position += 1
        return self.tokens

    def _handle_number(self) -> None:
        """
        Handle a number token.

        Parses a consecutive sequence of digits from the source text
        and stores it in the tokens list as a number token.

        Returns:
            None
        """

        digits = ""
        while self.position < len(self.text) and self.text[self.position].isdigit():
            digits += self.text[self.position]
            self.position += 1
        self.tokens.append(Token(TokenType.NUMBER, digits, self.position))

    def _handle_function_word(self) -> None:
        """
        Handle a function word token.

        Parses a consecutive sequence of characters from the source text
        and stores it in the tokens list as a word token.

        Returns:
            None
        """

        position = self.position
        word = ""
        while position < len(self.text) and (
            self.text[position].isalpha() or self.text[position] == "'"
        ):
            word += self.text[position]
            position += 1

        word_type = {
            "mul": TokenType.FUNCTION_MUL,
            "do": TokenType.FUNCTION_DO,
            "don't": TokenType.FUNCTION_DONT,
        }.get(word, TokenType.UNKNOWN)

        if word_type != TokenType.UNKNOWN:
            self.tokens.append(Token(word_type, word, self.position))
            self.position += len(word)

        else:
            self.tokens.append(Token(TokenType.UNKNOWN, word[0], self.position))
            self.position += 1


class Parser:
    """
    Parses a list of tokens to extract specific patterns or expressions.

    The Parser takes a list of tokens and processes them to identify
    and extract meaningful expressions, such as multiplication operations.

    Attributes:
        tokens (list[Token]): The list of tokens to be parsed.
        token_position (int): The current position in the token list.
    """

    def __init__(self, tokens: list[Token]) -> None:
        """
        Initialize a Parser object.

        Args:
            tokens (list[Token]): The list of tokens to be parsed.

        Returns:
            None
        """
        self.tokens = tokens
        self.token_position = 0
        self.context_enabled = True

    def parse(self, context_aware: bool) -> list[Any]:
        """
        Parse the list of tokens and return a list of extracted expressions.

        Args:
            context_aware (bool): Whether to use context-aware parsing.

        Returns:
            list[Any]: A list of strings of the form "A*B"
        """
        results = []

        while self.token_position < len(self.tokens):
            token = self.tokens[self.token_position]

            if token.type == TokenType.FUNCTION_MUL:
                if valid_expression := self._parse_multiplication(context_aware):
                    results.append(valid_expression)
                self.token_position += 1

            elif token.type == TokenType.FUNCTION_DO:
                if self._parse_context(TokenType.FUNCTION_DO):
                    self.context_enabled = True
                self.token_position += 1

            elif token.type == TokenType.FUNCTION_DONT:
                if self._parse_context(TokenType.FUNCTION_DONT):
                    self.context_enabled = False
                self.token_position += 1

            else:
                self.token_position += 1

        return results

    def _parse_multiplication(self, context_aware: bool) -> tuple[int, int] | None:
        """
        Parse a multiplication expression and return the two numbers that are being multiplied

        Args:
            context_aware (bool): Whether to check for context-aware parsing

        Returns:
            tuple[int, int] | None: A tuple of the two numbers that are being multiplied
        """

        if context_aware and not self.context_enabled:
            return None

        position = self.token_position
        if position + 5 >= len(self.tokens):
            return None

        if (
            self.tokens[position].type == TokenType.FUNCTION_MUL
            and self.tokens[position + 1].type == TokenType.LPAREN
            and self.tokens[position + 2].type == TokenType.NUMBER
            and self.tokens[position + 3].type == TokenType.COMMA
            and self.tokens[position + 4].type == TokenType.NUMBER
            and self.tokens[position + 5].type == TokenType.RPAREN
        ):
            return (
                int(self.tokens[position + 2].value),
                int(self.tokens[position + 4].value),
            )

        return None

    def _parse_context(self, context: TokenType) -> bool:
        """
        Parse a context and return True if it is valid

        Args:
            context (TokenType): The context to parse

        Returns:
            bool: True if it is a valid context, False otherwise
        """
        position = self.token_position

        if position + 3 >= len(self.tokens):
            return False

        if (
            self.tokens[position].type == context
            and self.tokens[position + 1].type == TokenType.LPAREN
            and self.tokens[position + 2].type == TokenType.RPAREN
        ):
            return True

        return False


def main() -> None:
    """
    Main entry point for the script

    Reads the input from a file, processes data and prints the solution to
    both parts of the problem.

    Returns:
        None
    """
    text_src = read_input()

    mul_instructions = find_mul_instructions(text_src)
    sum_results = sum(process_multiplication(inst) for inst in mul_instructions)
    print(f"Problem 1 (regex): {sum_results}")

    tokenizer = Tokenizer(text_src)
    tokenizer.tokenize()

    all_multiplications = Parser(tokenizer.tokens).parse(False)
    sum_all_multiplications = sum(num0 * num1 for num0, num1 in all_multiplications)
    print(f"Problem 1 (tokenized): {sum_all_multiplications}")

    enabled_multiplications = Parser(tokenizer.tokens).parse(True)
    sum_enabled_multiplications = sum(
        num0 * num1 for num0, num1 in enabled_multiplications
    )
    print(f"Problem 2: {sum_enabled_multiplications}")


if __name__ == "__main__":
    main()
