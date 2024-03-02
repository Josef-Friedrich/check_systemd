"""Unit tests"""

from __future__ import annotations

import check_systemd
from check_systemd import SystemdUnitTypesList


class TestMethodConvertToSec:
    def convert(self, value: str) -> float:
        return check_systemd.CliSource._CliSource__convert_to_sec(value)  # type: ignore

    def test_one_digits(self) -> None:
        assert self.convert("1s") == 1

    def test_one_digit_ago(self) -> None:
        assert self.convert("1s ago") == 1

    def test_two_digits(self) -> None:
        assert self.convert("11s") == 11

    def test_multiple_units(self) -> None:
        assert self.convert("1min 1s") == 61

    def test_float(self) -> None:
        assert self.convert("1min 1.123s") == 61.123

    def test_non_float_and_float(self) -> None:
        assert self.convert("1min 2.15s") == 62.15

    def test_min_sec(self) -> None:
        assert self.convert("34min 46.292s") == 2086.292

    def test_months_days(self) -> None:
        assert self.convert("2 months 8 days") == 5875200


class TestClassSystemdUnitTypesList:
    def test_initialization(self) -> None:
        unit_types = SystemdUnitTypesList("service", "timer")
        assert ["service", "timer"] == list(unit_types)

    def test_convert_to_regexp(self) -> None:
        unit_types = SystemdUnitTypesList("service", "timer")
        assert ".*\\.(service|timer)$" == unit_types.convert_to_regexp()
