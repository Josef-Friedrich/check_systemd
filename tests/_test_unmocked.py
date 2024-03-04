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


class TestPropertyAllUnits:
    def test_cli(self, cli: Source) -> None:
        assert cli.units.count > 0

    def test_cli_user(self, cli: Source) -> None:
        cli.set_user(True)
        assert cli.units.count > 0

    def test_compare(self, cli: Source, dbus: Source) -> None:
        assert cli.units.count == dbus.units.count

    def test_compare_user(self, cli: Source, dbus: DbusSource) -> None:
        cli.set_user(True)
        dbus.set_user(True)
        assert cli.units.count == dbus.units.count


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


class TestPropertyStartupTime:
    def assert_startup_time(self, source: Source) -> None:
        startup_time = source.startup_time
        assert startup_time
        assert startup_time > 0

    def test_cli(self, cli: Source) -> None:
        self.assert_startup_time(cli)

    def test_dbus(self, dbus: Source) -> None:
        self.assert_startup_time(dbus)

    def test_compare(self, cli: Source, dbus: Source) -> None:
        assert cli.startup_time == dbus.startup_time


class TestPropertyAllTimers:
    def test_dbus(self, dbus: Source) -> None:
        for timer in dbus.timers.filter():
            print(timer)

    def test_compare(self, cli: Source, dbus: Source) -> None:
        assert cli.timers.count == dbus.timers.count


class TestDbus:
    def test_method_get_userspace_timestamp_monotonic(self, dbus: DbusSource) -> None:
        assert dbus._DbusSource__userspace_timestamp_monotonic > 0  # type: ignore
