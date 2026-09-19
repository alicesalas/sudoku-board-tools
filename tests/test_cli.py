import contextlib
import io
import os
import tempfile
import unittest

from sudoku.cli import main

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

DUPLICATE_ROW_COMPACT = "5" + SOLVED_COMPACT[1:]  # row 0 now has two 5s


class CliTestCase(unittest.TestCase):
    def _write_temp_file(self, text):
        fd, path = tempfile.mkstemp(suffix=".txt")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        self.addCleanup(os.remove, path)
        return path

    def _run(self, argv):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = main(argv)
        return code, stdout.getvalue(), stderr.getvalue()


class ValidBoardTest(CliTestCase):
    def test_prints_pretty_grid_by_default(self):
        path = self._write_temp_file(SOLVED_COMPACT)
        code, out, err = self._run([path])
        self.assertEqual(code, 0)
        self.assertIn("5 3 4 | 6 7 8 | 9 1 2", out)
        self.assertEqual(err, "")

    def test_compact_flag_prints_single_line(self):
        path = self._write_temp_file(SOLVED_COMPACT)
        code, out, err = self._run([path, "--compact"])
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), SOLVED_COMPACT)

    def test_quiet_flag_suppresses_board_output(self):
        path = self._write_temp_file(SOLVED_COMPACT)
        code, out, err = self._run([path, "--quiet"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "")
        self.assertEqual(err, "")


class ConflictTest(CliTestCase):
    def test_conflicts_are_reported_on_stderr_with_exit_code_1(self):
        path = self._write_temp_file(DUPLICATE_ROW_COMPACT)
        code, out, err = self._run([path])
        self.assertEqual(code, 1)
        self.assertIn("not a legal board", err)
        self.assertIn("duplicate 5 in row 0", err)
        # The board still gets printed; conflicts are a separate concern.
        self.assertNotEqual(out, "")


class ParseErrorTest(CliTestCase):
    def test_malformed_input_returns_exit_code_2(self):
        path = self._write_temp_file("not a valid puzzle")
        code, out, err = self._run([path])
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("expected 9 rows", err)

    def test_missing_file_returns_exit_code_2(self):
        code, out, err = self._run(["/no/such/path/puzzle.txt"])
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("/no/such/path/puzzle.txt", err)


if __name__ == "__main__":
    unittest.main()
