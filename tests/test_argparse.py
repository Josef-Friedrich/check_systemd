"""Test the command line interface. The CLI interface is implemented with
argparse."""
from __future__ import annotations

import io
import subprocess
from contextlib import redirect_stderr

import pytest

import check_systemd
from check_systemd import get_argparser
from tests.helper import execute_main


class TestFromFunction:
    def test_default(self) -> None:
        opts = get_argparser().parse_args([])
        assert "cli" == opts.data_source

    def test_dbus(self) -> None:
        opts = get_argparser().parse_args(["--dbus"])
        assert "dbus" == opts.data_source

    def test_cli(self) -> None:
        opts = get_argparser().parse_args(["--cli"])
        assert "cli" == opts.data_source

    def test_exclusive_cli_dbus(self) -> None:
        dev_null = io.StringIO()
        with pytest.raises(SystemExit) as cm, redirect_stderr(dev_null):
            get_argparser().parse_args(["--cli", "--dbus"])
        assert cm.value.code == 2


class TestWithMocking:
    def test_without_arguments(self) -> None:
        result = execute_main()
        result.assert_ok()

    def test_help_short(self) -> None:
        result = execute_main(argv=["-h"])
        assert "usage: check_systemd" in result.output

    def test_help_long(self) -> None:
        result = execute_main(argv=["--help"])
        assert "usage: check_systemd" in result.output

    def test_version_short(self) -> None:
        result = execute_main(argv=["-V"])
        assert "check_systemd " + check_systemd.__version__ in result.output

    def test_version_long(self) -> None:
        result = execute_main(argv=["--version"])
        assert "check_systemd " + check_systemd.__version__ in result.output


class TestWithSubprocess:
    def test_help(self) -> None:
        process = subprocess.run(
            ["./check_systemd.py", "--help"], encoding="utf-8", stdout=subprocess.PIPE
        )
        assert process.returncode == 0
        assert "usage: check_systemd" in process.stdout

    def test_version(self) -> None:
        process = subprocess.run(
            ["./check_systemd.py", "--version"],
            encoding="utf-8",
            stdout=subprocess.PIPE,
        )
        assert process.returncode == 0
        assert "check_systemd " + check_systemd.__version__ in process.stdout

    def test_exclusive_cli_dbus(self) -> None:
        process = subprocess.run(
            ["./check_systemd.py", "--cli", "--dbus"],
            encoding="utf-8",
            stderr=subprocess.PIPE,
        )
        assert process.returncode == 2
        assert (
            "error: argument --dbus: not allowed with argument --cli" in process.stderr
        )

    def test_entry_point(self) -> None:
        process = subprocess.run(
            ["check_systemd", "--help"], encoding="utf-8", stdout=subprocess.PIPE
        )
        assert process.returncode == 0
        assert "check_systemd" in process.stdout
