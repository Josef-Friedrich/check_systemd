"""Run this test in an unmocked environment."""

from __future__ import annotations

import pytest

from check_systemd import CliSource, DbusSource, Source


@pytest.fixture
def cli() -> CliSource:
    return CliSource()


@pytest.fixture
def dbus() -> DbusSource:
    return DbusSource()


class TestGetAllUnits:
    def test_cli(self, cli: Source) -> None:
        for unit in cli.get_all_units():
            assert unit

    def test_cli_user(self, cli: Source) -> None:
        cli.set_user(True)
        for unit in cli.get_all_units():
            assert unit

    def test_dbus(self, dbus: Source) -> None:
        for unit in dbus.get_all_units():
            assert unit

    def test_dbus_user(self, dbus: Source) -> None:
        dbus.set_user(True)
        for unit in dbus.get_all_units():
            assert unit

    def test_compare(self, cli: Source, dbus: Source) -> None:
        list_cli = list(cli.get_all_units())
        list_dbus = list(dbus.get_all_units())
        assert len(list_cli) == len(list_dbus)

    def test_compare_user(self, cli: Source, dbus: DbusSource) -> None:
        cli.set_user(True)
        dbus.set_user(True)
        list_cli = list(cli.get_all_units())
        list_dbus = list(dbus.get_all_units())
        assert len(list_cli) == len(list_dbus)


class TestGetAllUnitsCached:
    def test_cli(self, cli: Source) -> None:
        cache = cli.get_all_units_cached()
        assert cache.count > 0

    def test_cli_user(self, cli: Source) -> None:
        cli.set_user(True)
        cache = cli.get_all_units_cached()
        assert cache.count > 0


class TestGetUnit:
    def test_cli(self, cli: Source) -> None:
        unit = cli.get_unit("ssh.service")
        assert unit.name == "ssh.service"
        assert unit.active_state == "active"
        assert unit.sub_state == "running"
        assert unit.load_state == "loaded"

    def test_dbus(self, dbus: Source) -> None:
        unit = dbus.get_unit("ssh.service")
        assert unit.name == "ssh.service"
        assert unit.active_state == "active"
        assert unit.sub_state == "running"
        assert unit.load_state == "loaded"


class TestGetStartupTime:
    def assert_startup_time(self, source: Source) -> None:
        startup_time = source.get_startup_time()
        assert startup_time
        assert startup_time > 0

    def test_cli(self, cli: Source) -> None:
        self.assert_startup_time(cli)

    def test_dbus(self, dbus: Source) -> None:
        self.assert_startup_time(dbus)

    def test_compare(self, cli: Source, dbus: Source) -> None:
        assert cli.get_startup_time() == dbus.get_startup_time()


class TestDbus:
    def test_method_get_userspace_timestamp_monotonic(self, dbus: DbusSource) -> None:
        assert dbus._DbusSource__userspace_timestamp_monotonic > 0  # type: ignore
