"""Unit tests"""

from __future__ import annotations

from unittest.mock import patch

from check_systemd import CliSource, Source
from tests.helper import MPopen, freeze_time, get_mocks_for_popen

Timer = Source.Timer


def test_collect_properties() -> None:
    with patch("check_systemd.subprocess.Popen") as Popen:
        Popen.return_value = get_mocks_for_popen("systemctl-show-nginx_active.txt")[0]
        unit = CliSource().get_unit("nginx.service")
    assert unit.name == "nginx.service"
    assert unit.active_state == "active"
    assert unit.sub_state == "running"
    assert unit.load_state == "loaded"


def read_timers(stdout: str, now: float) -> dict[str, Timer]:
    """Read the timers from the output of ``systemctl list-timers`` at the
    time ``now``.

    :param stdout: A string or a file name inside the folder ``cli_output``.
    :param now: Seconds since the epoch.
    """
    with patch("check_systemd.subprocess.Popen") as Popen, freeze_time(now):
        Popen.return_value = MPopen(stdout=stdout)
        timers = CliSource().timers
    assert Popen.call_args.args[0] == [
        "systemctl",
        "list-timers",
        "--all",
        "--output=json",
    ]
    return {timer.name: timer for timer in timers}


class TestTimers:
    """``next`` and ``last`` are the seconds until the next run and the
    seconds since the last run, or ``None`` if there is no such run."""

    def test_json_v257(self) -> None:
        timers = read_timers("systemctl-list-timers_v257.json", now=1793651652)
        assert timers["logrotate.timer"] == Timer(
            name="logrotate.timer", next=353, last=130
        )
        assert timers["once-test.timer"] == Timer(
            name="once-test.timer", next=None, last=3
        )
        assert timers["dead-test.timer"] == Timer(
            name="dead-test.timer", next=None, last=None
        )

    def test_json_v252(self) -> None:
        timers = read_timers("systemctl-list-timers_v252.json", now=1793651768)
        assert timers["dpkg-db-backup.timer"] == Timer(
            name="dpkg-db-backup.timer", next=12232, last=None
        )
        assert timers["dead-test.timer"] == Timer(
            name="dead-test.timer", next=None, last=None
        )

    def test_json_without_timers(self) -> None:
        assert read_timers("[]\n", now=1793651652) == {}

    def test_table_of_systemd_245(self) -> None:
        """systemd 245 and older ignore ``--output=json`` and print the text
        table."""
        timers = read_timers("systemctl-list-timers_1.txt", now=1793651652)
        assert timers["systemd-tmpfiles-clean.timer"] == Timer(
            name="systemd-tmpfiles-clean.timer", next=72000, last=13140
        )
        assert timers["phpsessionclean.timer"] == Timer(
            name="phpsessionclean.timer", next=None, last=5529600
        )
