"""Backtracking solver for canonical Board objects.

Branches on the empty cell with the fewest remaining candidates rather
than scanning row-major, which prunes most dead ends immediately and
keeps ordinary puzzles fast without any constraint-propagation machinery.
"""

from typing import List, Optional

from .board import Board, find_conflicts


def solve(board: Board) -> Optional[Board]:
    """Return a solved copy of board, or None if it has no solution.

    Raises ValueError if the board already breaks sudoku's rules; callers
    with untrusted input should check find_conflicts() first.
    """
    if find_conflicts(board):
        raise ValueError("cannot solve a board that already breaks sudoku's rules")

    grid = [list(row) for row in board.rows]
    row_used = [0] * 9
    col_used = [0] * 9
    box_used = [0] * 9

    for r in range(9):
        for c in range(9):
            value = grid[r][c]
            if value:
                bit = 1 << value
                b = _box_index(r, c)
                row_used[r] |= bit
                col_used[c] |= bit
                box_used[b] |= bit

    if not _solve(grid, row_used, col_used, box_used):
        return None

    return Board(tuple(tuple(row) for row in grid))


def _box_index(row: int, col: int) -> int:
    return (row // 3) * 3 + (col // 3)


def _solve(
    grid: List[List[int]],
    row_used: List[int],
    col_used: List[int],
    box_used: List[int],
) -> bool:
    cell = _most_constrained_empty_cell(grid, row_used, col_used, box_used)
    if cell is None:
        return True  # no empty cells left

    r, c, candidates = cell
    if not candidates:
        return False

    b = _box_index(r, c)
    for value in candidates:
        bit = 1 << value
        grid[r][c] = value
        row_used[r] |= bit
        col_used[c] |= bit
        box_used[b] |= bit

        if _solve(grid, row_used, col_used, box_used):
            return True

        grid[r][c] = 0
        row_used[r] &= ~bit
        col_used[c] &= ~bit
        box_used[b] &= ~bit

    return False


def _most_constrained_empty_cell(
    grid: List[List[int]],
    row_used: List[int],
    col_used: List[int],
    box_used: List[int],
):
    """Return (row, col, candidates) for the empty cell with fewest legal
    digits, or None if the grid has no empty cells left.

    Stops early on the first cell with zero or one candidates, since
    neither the search nor a stricter choice could do better than that.
    """
    best = None
    for r in range(9):
        for c in range(9):
            if grid[r][c] != 0:
                continue
            used = row_used[r] | col_used[c] | box_used[_box_index(r, c)]
            candidates = [v for v in range(1, 10) if not used & (1 << v)]
            if best is None or len(candidates) < len(best[2]):
                best = (r, c, candidates)
                if len(candidates) <= 1:
                    return best
    return best
