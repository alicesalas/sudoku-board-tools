# sudoku-board-tools

Sudoku puzzle text shows up in a handful of shapes depending on where it
came from: a single 81-character line, a 9-line grid with box borders
copied out of a forum post, a grid with no borders at all. Before you can
do anything useful with a puzzle (solve it, generate variations, store
it) you need to turn that text into a real 9x9 grid and know whether it's
actually well-formed.

This library does that part: parse messy puzzle text into a canonical
`Board`, tell you exactly what's wrong with it if it isn't valid, and
print it back out in a readable format. It does not solve puzzles.

## Usage

```python
from sudoku import parse_board, format_board, find_conflicts

text = """
5 3 . | . 7 . | . . .
6 . . | 1 9 5 | . . .
. 9 8 | . . . | . 6 .
------+-------+------
8 . . | . 6 . | . . 3
4 . . | 8 . 3 | . . 1
7 . . | . 2 . | . . 6
------+-------+------
. 6 . | . . . | 2 8 .
. . . | . 4 4 | 5 . 9
. . . | . 8 . | . 7 9
"""

board = parse_board(text)
print(format_board(board))

conflicts = find_conflicts(board)
if conflicts:
    print("not a legal board:")
    for c in conflicts:
        print(f"  {c}")
```

The parser also accepts the compact one-line form, with either `.` or
`0` for empty cells:

```python
from sudoku import parse_board

board = parse_board(
    "530070000600195000098000060800060003400803001700020006060000280000419005000080"
)
```

Malformed input raises `SudokuParseError` with a message pointing at the
row and column that's wrong:

```python
from sudoku import parse_board, SudokuParseError

try:
    parse_board("only one line, not 81 chars")
except SudokuParseError as e:
    print(e)  # expected 9 rows of data, found 1
```

Note the distinction between two different failure modes:

- **`SudokuParseError`** — the text itself is broken (wrong number of
  rows, wrong row length, a character that isn't a digit or `.`).
- **`find_conflicts()`** — the text parsed fine, but the puzzle it
  describes breaks sudoku's rules (the same digit appears twice in a
  row, column, or 3x3 box). This is a normal, non-exceptional return
  value, since checking a candidate solution for correctness is a
  legitimate thing to do.

## Format details

The parser strips whitespace, `|` column separators, and `-`/`+`
box-border lines before it does anything else, so grids copied from
different sources tend to just work. What it does *not* tolerate: a
puzzle that isn't 9 rows of 9 cells each, or a character that isn't
`1`-`9`, `.`, or `0`.

## Development

No dependencies, no build step. Run the tests with:

```
python -m unittest discover tests
```

## License

MIT, see LICENSE.
