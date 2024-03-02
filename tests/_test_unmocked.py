"""Run this test in an unmocked environment."""
from __future__ import annotations

import pytest

from check_systemd import CliSource, DbusSource


@pytest.fixture
def cli() -> CliSource:
    return CliSource()


@pytest.fixture
def dbus() -> DbusSource:
    return DbusSource()


class TestGetAllUnits:
    def test_cli(self, cli: CliSource) -> None:
        for unit in cli.get_all_units():
            assert unit

    def test_cli_user(self, cli: CliSource) -> None:
        for unit in cli.get_all_units(True):
            assert unit

    def test_dbus(self, dbus: DbusSource) -> None:
        for unit in dbus.get_all_units():
            assert unit

    def test_dbus_user(self, dbus: CliSource) -> None:
        for unit in dbus.get_all_units(True):
            assert unit

    def test_compare(self, cli: CliSource, dbus: DbusSource) -> None:
        list_cli = list(cli.get_all_units())
        list_dbus = list(dbus.get_all_units())
        assert len(list_cli) == len(list_dbus)

    def test_compare_user(self, cli: CliSource, dbus: DbusSource) -> None:
        list_cli = list(cli.get_all_units(True))
        list_dbus = list(dbus.get_all_units(True))
        assert len(list_cli) == len(list_dbus)


class TestGetUnit:
    def test_cli(self) -> None:
        cli = CliSource()
        unit = cli.get_unit("ssh.service")
        assert unit.name == "ssh.service"
        assert unit.active_state == "active"
        assert unit.sub_state == "running"
        assert unit.load_state == "loaded"

    # def test_dbus(self) -> None:
    #     dbus = DbusSource()
    #     dbus.get_unit("")
