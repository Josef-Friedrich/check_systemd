"""Unit tests"""
from __future__ import annotations

from unittest.mock import patch

import pytest
from nagiosplugin import CheckError

import check_systemd
from check_systemd import SystemdUnitTypesList, execute_cli
from tests.helper import MPopen


class TestUnit:
    def test_function_format_timespan_to_seconds(self) -> None:
        _to_sec = check_systemd.format_timespan_to_seconds
        assert _to_sec("1s") == 1
        assert _to_sec("1s ago") == 1
        assert _to_sec("11s") == 11
        assert _to_sec("1min 1s") == 61
        assert _to_sec("1min 1.123s") == 61.123
        assert _to_sec("1min 2.15s") == 62.15
        assert _to_sec("34min 46.292s") == 2086.292
        assert _to_sec("2 months 8 days") == 5875200


class TestClassSystemdUnitTypesList:
    def test_initialization(self) -> None:
        unit_types = SystemdUnitTypesList("service", "timer")
        assert ["service", "timer"] == list(unit_types)

    def test_convert_to_regexp(self) -> None:
        unit_types = SystemdUnitTypesList("service", "timer")
        assert ".*\\.(service|timer)$" == unit_types.convert_to_regexp()


class TestFunctionExecuteCli:
    def test_execute_cli_stdout(self) -> None:
        with patch("check_systemd.subprocess.Popen") as Popen:
            Popen.return_value = MPopen(stdout="ok")
            stdout = execute_cli(["ls"])
        assert "ok" == stdout

    def test_execute_cli_stderr(self) -> None:
        with patch("check_systemd.subprocess.Popen") as Popen:
            Popen.side_effect = (MPopen(stdout="ok"), MPopen(stderr="Not ok"))
            stdout = execute_cli(["ls"])
            assert "ok" == stdout
            with pytest.raises(CheckError):
                execute_cli(["ls"])
