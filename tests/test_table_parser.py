from check_systemd import TableParser
from tests.helper import convert_to_bytes


def read_stdout(file_name: str) -> str:
    return convert_to_bytes(file_name).decode("utf-8")


def get_parser():
    return TableParser(read_stdout("systemctl-list-units_v246.txt"))


class TestTableParser:
    def test_initialization(self) -> None:
        parser = get_parser()
        assert "description" in parser.header_row
        assert "systemd-tmpfiles-clean.timer" in parser.body_rows[-1]
        assert [2, 111, 10, 9, 10] == parser.column_lengths

        assert ["", "unit", "load", "active", "sub", "description"] == parser.columns

    def test_detect_column_lengths(self) -> None:
        detect = TableParser._TableParser__detect_lengths
        assert [3, 3] == detect("1  2  3")
        assert [2, 3, 3] == detect("  1  2  3  ")
        assert [2, 2, 3, 2, 3, 2] == detect("  1 1  2 2  3 3  ")

    def test_split_line_into_columns(self) -> None:
        split = TableParser._TableParser__split_row
        assert ["123", "456", "789"] == split("123456789", [3, 3])
        assert ["UNIT", "STATE", "LOAD"] == split("UNIT  STATE  LOAD  ", [6, 7])

    def test_get_row(self) -> None:
        parser = get_parser()
        row = parser.get_row(0)
        assert "" == row["column_0"]
        assert "dev-block-254:0.device" == row["unit"]
        assert "loaded" == row["load"]
        assert "active" == row["active"]
        assert "plugged" == row["sub"]
        assert "/dev/block/254:0" == row["description"]

    def test_get_row_all(self) -> None:
        parser = get_parser()
        for i in range(0, parser.row_count):
            row = parser.get_row(i)
        assert "systemd-tmpfiles-clean.timer" == row["unit"]

    def test_list_rows(self) -> None:
        parser = get_parser()
        for row in parser.list_rows():
            pass
        assert "systemd-tmpfiles-clean.timer" == row["unit"]

    def test_narrow_column_separators(self) -> None:
        parser = TableParser(read_stdout("systemctl-list-timers_all-n-a.txt"))
        row = parser.get_row(1)
        assert "n/a" == row["next"]
        assert "n/a" == row["left"]
        assert "n/a" == row["last"]
        assert "n/a" == row["passed"]
        assert "systemd-readahead-done.timer" == row["unit"]
