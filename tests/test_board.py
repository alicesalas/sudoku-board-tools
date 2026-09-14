import unittest

from sudoku import (
    Board,
    SudokuParseError,
    find_conflicts,
    format_board,
    is_valid,
    parse_board,
)

EMPTY_ROW = (0, 0, 0, 0, 0, 0, 0, 0, 0)
EMPTY_BOARD_ROWS = tuple(EMPTY_ROW for _ in range(9))

SOLVED_COMPACT = (
    "534678912"
    "672195348"
    "198342567"
    "859761423"
    "426853791"
    "713924856"
    "961537284"
    "287419635"
    "345286179"
)
SOLVED_ROWS = (
    (5, 3, 4, 6, 7, 8, 9, 1, 2),
    (6, 7, 2, 1, 9, 5, 3, 4, 8),
    (1, 9, 8, 3, 4, 2, 5, 6, 7),
    (8, 5, 9, 7, 6, 1, 4, 2, 3),
    (4, 2, 6, 8, 5, 3, 7, 9, 1),
    (7, 1, 3, 9, 2, 4, 8, 5, 6),
    (9, 6, 1, 5, 3, 7, 2, 8, 4),
    (2, 8, 7, 4, 1, 9, 6, 3, 5),
    (3, 4, 5, 2, 8, 6, 1, 7, 9),
)

SOLVED_GRID = """\
5 3 4 | 6 7 8 | 9 1 2
6 7 2 | 1 9 5 | 3 4 8
1 9 8 | 3 4 2 | 5 6 7
------+-------+------
8 5 9 | 7 6 1 | 4 2 3
4 2 6 | 8 5 3 | 7 9 1
7 1 3 | 9 2 4 | 8 5 6
------+-------+------
9 6 1 | 5 3 7 | 2 8 4
2 8 7 | 4 1 9 | 6 3 5
3 4 5 | 2 8 6 | 1 7 9
"""


class ParseValidCasesTest(unittest.TestCase):
    """Table-driven: inputs that must parse to a specific board."""

    CASES = [
        ("compact 81-char, dots for empty", "." * 81, EMPTY_BOARD_ROWS),
        ("compact 81-char, zeros for empty", "0" * 81, EMPTY_BOARD_ROWS),
        ("compact 81-char, solved board", SOLVED_COMPACT, SOLVED_ROWS),
        ("box-bordered grid", SOLVED_GRID, SOLVED_ROWS),
        (
            "grid with leading/trailing blank lines",
            "\n\n" + SOLVED_GRID + "\n\n",
            SOLVED_ROWS,
        ),
        (
            "grid with windows line endings",
            SOLVED_GRID.replace("\n", "\r\n"),
            SOLVED_ROWS,
        ),
        (
            "grid without box separator lines",
            "\n".join(
                line for line in SOLVED_GRID.splitlines() if "-" not in line
            ),
            SOLVED_ROWS,
        ),
        (
            "grid with no spaces between digits",
            "\n".join(
                line.replace(" ", "") for line in SOLVED_GRID.splitlines()
            ),
            SOLVED_ROWS,
        ),
        (
            "compact string with surrounding whitespace",
            f"  {SOLVED_COMPACT}  \n",
            SOLVED_ROWS,
        ),
    ]

    def test_parses_to_expected_rows(self):
        for name, text, expected_rows in self.CASES:
            with self.subTest(case=name):
                board = parse_board(text)
                self.assertEqual(board.rows, expected_rows)


class ParseInvalidCasesTest(unittest.TestCase):
    """Table-driven: inputs that must be rejected with SudokuParseError."""

    CASES = [
        ("empty string", ""),
        ("only whitespace", "   \n\n  "),
        ("too few rows", "\n".join(["." * 9] * 8)),
        ("too many rows", "\n".join(["." * 9] * 10)),
        ("compact string too short", "." * 80),
        ("compact string too long", "." * 82),
        ("row too short", "\n".join(["." * 9] * 8 + ["." * 8])),
        ("row too long", "\n".join(["." * 9] * 8 + ["." * 10])),
        ("letter in place of digit", "\n".join(["........X"] + ["." * 9] * 8)),
        ("negative sign", "\n".join(["12345678-"] + ["." * 9] * 8)),
        ("invalid character in the middle of a full-length compact string", "1" * 40 + "X" + "1" * 40),
    ]

    def test_raises_parse_error(self):
        for name, text in self.CASES:
            with self.subTest(case=name):
                with self.assertRaises(SudokuParseError):
                    parse_board(text)


class RoundTripTest(unittest.TestCase):
    def test_pretty_printed_board_parses_back_to_same_rows(self):
        board = parse_board(SOLVED_COMPACT)
        reparsed = parse_board(format_board(board))
        self.assertEqual(board, reparsed)

    def test_compact_round_trip(self):
        board = parse_board(SOLVED_COMPACT)
        self.assertEqual(board.to_compact(), SOLVED_COMPACT)


class ConflictDetectionTest(unittest.TestCase):
    """Table-driven: boards that parse fine but break sudoku's rules."""

    def _board_from_rows(self, rows):
        return Board(tuple(rows))

    def test_solved_board_has_no_conflicts(self):
        board = self._board_from_rows(SOLVED_ROWS)
        self.assertEqual(find_conflicts(board), [])
        self.assertTrue(is_valid(board))

    def test_empty_board_has_no_conflicts(self):
        board = self._board_from_rows(EMPTY_BOARD_ROWS)
        self.assertEqual(find_conflicts(board), [])
        self.assertTrue(is_valid(board))

    def test_duplicate_in_row_is_reported(self):
        rows = list(SOLVED_ROWS)
        rows[0] = (5, 5, 4, 6, 7, 8, 9, 1, 2)  # was 5 3 4 ..., now two 5s
        board = self._board_from_rows(rows)
        conflicts = find_conflicts(board)
        self.assertIn("duplicate 5 in row 0", conflicts)
        self.assertFalse(is_valid(board))

    def test_duplicate_in_column_is_reported(self):
        rows = list(SOLVED_ROWS)
        rows[1] = (5,) + rows[1][1:]  # column 0 already has a 5 in row 0
        board = self._board_from_rows(rows)
        conflicts = find_conflicts(board)
        self.assertIn("duplicate 5 in column 0", conflicts)

    def test_duplicate_in_box_is_reported(self):
        # Two 5s in the top-left box, in different rows and columns, so
        # this exercises the box check without also tripping row/column
        # checks.
        rows = [list(r) for r in EMPTY_BOARD_ROWS]
        rows[0][0] = 5
        rows[1][1] = 5
        board = self._board_from_rows(rows)
        conflicts = find_conflicts(board)
        self.assertIn("duplicate 5 in box (0, 0)", conflicts)
        self.assertNotIn("duplicate 5 in row 0", conflicts)
        self.assertNotIn("duplicate 5 in column 0", conflicts)


if __name__ == "__main__":
    unittest.main()
