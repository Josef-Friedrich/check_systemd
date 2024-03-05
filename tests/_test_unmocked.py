"""Run this test in an unmocked environment."""

from __future__ import annotations

import pytest

from check_systemd import CliSource, GiSource, Source


@pytest.fixture
def cli() -> CliSource:
    return CliSource()


@pytest.fixture
def gi() -> GiSource:
    return GiSource()


class TestPropertyAllUnits:
    def test_cli(self, cli: Source) -> None:
        assert cli.units.count > 0

    def test_cli_user(self, cli: Source) -> None:
        cli.set_user(True)
        assert cli.units.count > 0

    def test_compare(self, cli: Source, gi: Source) -> None:
        assert cli.units.count == gi.units.count

    def test_compare_user(self, cli: Source, gi: GiSource) -> None:
        cli.set_user(True)
        gi.set_user(True)
        assert cli.units.count == gi.units.count


class TestGetUnit:
    def test_cli(self, cli: Source) -> None:
        unit = cli.get_unit("ssh.service")
        assert unit.name == "ssh.service"
        assert unit.active_state == "active"
        assert unit.sub_state == "running"
        assert unit.load_state == "loaded"

    def test_gi(self, gi: Source) -> None:
        unit = gi.get_unit("ssh.service")
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

    def test_gi(self, gi: Source) -> None:
        self.assert_startup_time(gi)

    def test_compare(self, cli: Source, gi: Source) -> None:
        assert cli.startup_time == gi.startup_time


class TestPropertyTimers:
    def test_gi(self, gi: Source) -> None:
        for timer in gi.timers:
            assert timer.name

    @pytest.mark.skip(reason="Fix later")
    def test_compare(self, cli: Source, gi: Source) -> None:
        assert cli.timers.count == gi.timers.count
        assert list(gi.timers) == list(cli.timers)


class TestClassGiSource:
    def test_subclass_unit_proxy(
        self,
    ) -> None:
        unit = GiSource.UnitProxy(name="ssh.service")

        assert unit.object_path == "/org/freedesktop/systemd1/unit/ssh_2eservice"
        assert unit.interface_name == "org.freedesktop.systemd1.Unit"
        assert unit.active_state == "active"
        assert unit.sub_state == "running"
        assert unit.load_state == "loaded"

    def test_method_get_userspace_timestamp_monotonic(self, gi: GiSource) -> None:
        assert gi._GiSource__userspace_timestamp_monotonic > 0  # type: ignore
