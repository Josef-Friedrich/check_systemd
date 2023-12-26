import unittest

from check_systemd import TableParser
from tests.helper import convert_to_bytes


def read_stdout(file_name: str) -> str:
    return convert_to_bytes(file_name).decode("utf-8")


def get_parser():
    return TableParser(read_stdout("systemctl-list-units_v246.txt"))


class TestTableParser(unittest.TestCase):
    def test_initialization(self) -> None:
        parser = get_parser()
        self.assertIn("description", parser.header_row)
        self.assertIn("systemd-tmpfiles-clean.timer", parser.body_rows[-1])
        self.assertEqual([2, 111, 10, 9, 10], parser.column_lengths)

        self.assertEqual(
            ["", "unit", "load", "active", "sub", "description"], parser.columns
        )

    def test_detect_column_lengths(self) -> None:
        detect = TableParser._TableParser__detect_lengths
        self.assertEqual([3, 3], detect("1  2  3"))
        self.assertEqual([2, 3, 3], detect("  1  2  3  "))
        self.assertEqual([2, 2, 3, 2, 3, 2], detect("  1 1  2 2  3 3  "))

    def test_split_line_into_columns(self) -> None:
        split = TableParser._TableParser__split_row
        self.assertEqual(["123", "456", "789"], split("123456789", [3, 3]))
        self.assertEqual(
            ["UNIT", "STATE", "LOAD"], split("UNIT  STATE  LOAD  ", [6, 7])
        )

    def test_get_row(self) -> None:
        parser = get_parser()
        row = parser.get_row(0)
        self.assertEqual("", row["column_0"])
        self.assertEqual("dev-block-254:0.device", row["unit"])
        self.assertEqual("loaded", row["load"])
        self.assertEqual("active", row["active"])
        self.assertEqual("plugged", row["sub"])
        self.assertEqual("/dev/block/254:0", row["description"])

    def test_get_row_all(self) -> None:
        parser = get_parser()
        for i in range(0, parser.row_count):
            row = parser.get_row(i)
        self.assertEqual("systemd-tmpfiles-clean.timer", row["unit"])

    def test_list_rows(self) -> None:
        parser = get_parser()
        for row in parser.list_rows():
            pass
        self.assertEqual("systemd-tmpfiles-clean.timer", row["unit"])

    def test_narrow_column_separators(self) -> None:
        parser = TableParser(read_stdout("systemctl-list-timers_all-n-a.txt"))
        row = parser.get_row(1)
        self.assertEqual("n/a", row["next"])
        self.assertEqual("n/a", row["left"])
        self.assertEqual("n/a", row["last"])
        self.assertEqual("n/a", row["passed"])
        self.assertEqual("systemd-readahead-done.timer", row["unit"])


if __name__ == "__main__":
    unittest.main()
