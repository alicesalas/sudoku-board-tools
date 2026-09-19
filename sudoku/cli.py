"""Command-line entry point: parse a puzzle file, print it, report conflicts.

Kept separate from board.py so the parsing/printing library has no
dependency on argparse or sys.exit conventions.
"""

import argparse
import sys
from typing import List, Optional

from .board import SudokuParseError, find_conflicts, parse_board


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="sudoku",
        description="Parse a sudoku puzzle file, print it, and report rule violations.",
    )
    parser.add_argument("path", help="path to a puzzle file (compact or bordered-grid text)")
    parser.add_argument(
        "--compact",
        action="store_true",
        help="print the board as an 81-character string instead of a bordered grid",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="don't print the board, only report conflicts",
    )
    args = parser.parse_args(argv)

    try:
        with open(args.path, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print(f"sudoku: {args.path}: {e.strerror}", file=sys.stderr)
        return 2

    try:
        board = parse_board(text)
    except SudokuParseError as e:
        print(f"sudoku: {args.path}: {e}", file=sys.stderr)
        return 2

    if not args.quiet:
        print(board.to_compact() if args.compact else board.to_pretty())

    conflicts = find_conflicts(board)
    if conflicts:
        print(f"sudoku: {args.path}: not a legal board:", file=sys.stderr)
        for conflict in conflicts:
            print(f"  {conflict}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
