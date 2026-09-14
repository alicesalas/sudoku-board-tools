"""Parsing, validating, and printing sudoku boards.

Puzzle files show up in the wild in two shapes: a single 81-character
line, or a 9-line grid decorated with box borders (pipes, dashes, plus
signs). This module accepts either, strips the decoration, and produces
a canonical Board. It does not solve puzzles.
"""

from typing import List, Tuple

Row = Tuple[int, int, int, int, int, int, int, int, int]


class SudokuParseError(ValueError):
    """Raised when input text cannot be parsed as a sudoku board."""


class Board:
    """An immutable 9x9 grid of digits 1-9, with 0 meaning empty."""

    __slots__ = ("rows",)

    def __init__(self, rows: Tuple[Row, ...]):
        self.rows = rows

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Board) and self.rows == other.rows

    def __repr__(self) -> str:
        return f"Board({self.rows!r})"

    def cell(self, row: int, col: int) -> int:
        return self.rows[row][col]

    def to_compact(self) -> str:
        """Render as an 81-character string, '0' for empty cells."""
        return "".join(str(cell) for row in self.rows for cell in row)

    def to_pretty(self) -> str:
        return format_board(self)


# Lines made up entirely of these characters are box-border decoration,
# not data, and are dropped before parsing (e.g. "------+-------+------").
_DECORATION_CHARS = set("-+| ")
_EMPTY_CHARS = set(".0")
_DIGIT_CHARS = set("123456789")


def parse_board(text: str) -> Board:
    """Parse a sudoku board from text.

    Accepts either a single 81-character line (digits 1-9, with '.' or
    '0' for empty cells) or a 9-line grid. Grid lines may include '|'
    column separators and '-'/'+' box-border rows; that decoration is
    stripped before parsing. Raises SudokuParseError on malformed input.
    """
    significant_lines: List[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if set(line) <= _DECORATION_CHARS:
            continue
        cleaned = line.replace("|", "").replace(" ", "")
        if not cleaned:
            continue
        significant_lines.append(cleaned)

    # A single 81-char line is the compact form; split it into 9 rows
    # so the rest of the parser only ever deals with one shape.
    if len(significant_lines) == 1 and len(significant_lines[0]) == 81:
        compact = significant_lines[0]
        significant_lines = [compact[i * 9 : i * 9 + 9] for i in range(9)]

    if len(significant_lines) != 9:
        raise SudokuParseError(
            f"expected 9 rows of data, found {len(significant_lines)}"
        )

    rows = []
    for r, line in enumerate(significant_lines):
        if len(line) != 9:
            raise SudokuParseError(
                f"row {r} has {len(line)} cells, expected 9: {line!r}"
            )
        cells = []
        for c, ch in enumerate(line):
            if ch in _EMPTY_CHARS:
                cells.append(0)
            elif ch in _DIGIT_CHARS:
                cells.append(int(ch))
            else:
                raise SudokuParseError(
                    f"invalid character {ch!r} at row {r}, column {c}"
                )
        rows.append(tuple(cells))

    return Board(tuple(rows))


def format_board(board: Board) -> str:
    """Render a board as a 9x9 grid with box separators."""
    lines = []
    for r, row in enumerate(board.rows):
        if r != 0 and r % 3 == 0:
            lines.append("------+-------+------")
        cells = ["." if v == 0 else str(v) for v in row]
        groups = (" ".join(cells[0:3]), " ".join(cells[3:6]), " ".join(cells[6:9]))
        lines.append(" | ".join(groups))
    return "\n".join(lines)


def find_conflicts(board: Board) -> List[str]:
    """Return human-readable rule violations; empty list if the board is valid.

    A board can parse cleanly but still break sudoku's rules (duplicate
    digit in a row, column, or 3x3 box), which is a separate concern
    from whether the text was well-formed.
    """
    conflicts: List[str] = []

    for r, row in enumerate(board.rows):
        conflicts.extend(_duplicates_in_group(row, f"row {r}"))

    for c in range(9):
        column = tuple(board.rows[r][c] for r in range(9))
        conflicts.extend(_duplicates_in_group(column, f"column {c}"))

    for br in range(3):
        for bc in range(3):
            box = tuple(
                board.rows[br * 3 + dr][bc * 3 + dc]
                for dr in range(3)
                for dc in range(3)
            )
            conflicts.extend(_duplicates_in_group(box, f"box ({br}, {bc})"))

    return conflicts


def _duplicates_in_group(values: Tuple[int, ...], label: str) -> List[str]:
    seen = set()
    duplicates = []
    for value in values:
        if value == 0:
            continue
        if value in seen:
            duplicates.append(f"duplicate {value} in {label}")
        else:
            seen.add(value)
    return duplicates


def is_valid(board: Board) -> bool:
    return not find_conflicts(board)
