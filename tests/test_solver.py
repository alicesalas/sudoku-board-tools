import unittest

from sudoku import Board, parse_board, solve

# A well-known example puzzle (widely reproduced in solver test suites)
# with a unique solution, used here to check that solve() finds it.
PUZZLE_COMPACT = (
    "003020600"
    "900305001"
    "001806400"
    "008102900"
    "700000008"
    "006708200"
    "002609500"
    "800203009"
    "005010300"
)
SOLUTION_COMPACT = (
    "483921657"
    "967345821"
    "251876493"
    "548132976"
    "729564138"
    "136798245"
    "372689514"
    "814253769"
    "695417382"
)


class SolveTest(unittest.TestCase):
    def test_solves_puzzle_with_unique_solution(self):
        puzzle = parse_board(PUZZLE_COMPACT)
        solved = solve(puzzle)
        self.assertEqual(solved.to_compact(), SOLUTION_COMPACT)

    def test_already_solved_board_returns_equal_board(self):
        board = parse_board(SOLUTION_COMPACT)
        self.assertEqual(solve(board), board)

    def test_empty_board_is_solvable(self):
        board = parse_board("0" * 81)
        solved = solve(board)
        self.assertIsNotNone(solved)
        self.assertEqual(solved.to_compact().count("0"), 0)

    def test_board_that_already_breaks_the_rules_raises(self):
        rows = list(parse_board(SOLUTION_COMPACT).rows)
        rows[0] = (5,) + rows[0][1:]  # duplicate 5 in row 0
        board = Board(tuple(rows))
        with self.assertRaises(ValueError):
            solve(board)

    def test_board_with_no_solution_returns_none(self):
        # Row 0 forces column 8's last cell to be 9 (it's the only digit
        # missing from the row), but column 8 already has a 9 elsewhere.
        # No rule is directly broken (no repeated digit in any row,
        # column, or box), yet no assignment can satisfy both facts.
        rows = [[0] * 9 for _ in range(9)]
        rows[0] = [1, 2, 3, 4, 5, 6, 7, 8, 0]
        rows[5][8] = 9
        board = Board(tuple(tuple(row) for row in rows))
        self.assertEqual(solve(board), None)


if __name__ == "__main__":
    unittest.main()
