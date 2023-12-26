"""Unit tests"""

import unittest
from unittest.mock import patch

from nagiosplugin import CheckError

import check_systemd
from check_systemd import SystemdUnitTypesList, execute_cli
from tests.helper import MPopen


class TestUnit(unittest.TestCase):
    def test_function_format_timespan_to_seconds(self) -> None:
        _to_sec = check_systemd.format_timespan_to_seconds
        self.assertEqual(_to_sec("1s"), 1)
        self.assertEqual(_to_sec("1s ago"), 1)
        self.assertEqual(_to_sec("11s"), 11)
        self.assertEqual(_to_sec("1min 1s"), 61)
        self.assertEqual(_to_sec("1min 1.123s"), 61.123)
        self.assertEqual(_to_sec("1min 2.15s"), 62.15)
        self.assertEqual(_to_sec("34min 46.292s"), 2086.292)
        self.assertEqual(_to_sec("2 months 8 days"), 5875200)


class TestClassSystemdUnitTypesList(unittest.TestCase):
    def test_initialization(self) -> None:
        unit_types = SystemdUnitTypesList("service", "timer")
        self.assertEqual(["service", "timer"], list(unit_types))

    def test_convert_to_regexp(self) -> None:
        unit_types = SystemdUnitTypesList("service", "timer")
        self.assertEqual(".*\\.(service|timer)$", unit_types.convert_to_regexp())


class TestFunctionExecuteCli(unittest.TestCase):
    def test_execute_cli_stdout(self) -> None:
        with patch("check_systemd.subprocess.Popen") as Popen:
            Popen.return_value = MPopen(stdout="ok")
            stdout = execute_cli(["ls"])
        self.assertEqual("ok", stdout)

    def test_execute_cli_stderr(self) -> None:
        with patch("check_systemd.subprocess.Popen") as Popen:
            Popen.side_effect = (MPopen(stdout="ok"), MPopen(stderr="Not ok"))
            stdout = execute_cli(["ls"])
            self.assertEqual("ok", stdout)
            with self.assertRaises(CheckError):
                execute_cli(["ls"])


if __name__ == "__main__":
    unittest.main()
