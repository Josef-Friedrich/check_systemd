from __future__ import annotations

import pytest

from tests.helper import (
    MockResult,
    execute_main,
    freeze_time,
    get_popen_for_commands,
)

DAY = 60 * 60 * 24

CAPTURE_TIMES = {"v252": 1793651768, "v257": 1793651652}
"""The output of ``date +%s`` right before the outputs of
``systemctl list-timers --all`` and
``systemctl list-timers --all --output=json`` were captured: with systemd 252
on Debian 12.5 and with systemd 257 on Debian 13.7."""


def execute_on_host(
    timers_table: str,
    timers_json: str,
    additional_argv: list[str] | None = None,
) -> MockResult:
    """Execute the timers check on a host that prints ``timers_table`` for
    ``systemctl list-timers --all`` and ``timers_json`` for
    ``systemctl list-timers --all --output=json``.

    :param timers_table: A file name inside the folder ``cli_output``.
    :param timers_json: A file name inside the folder ``cli_output``.
    """
    argv = ["--timers", "--no-performance-data"]
    if additional_argv:
        argv += additional_argv

    popen = get_popen_for_commands(
        {
            "systemctl list-units --all": "systemctl-list-units_3units.txt",
            "systemd-analyze": "systemd-analyze_12.345.txt",
            "systemctl list-timers --all": timers_table,
            "systemctl list-timers --all --output=json": timers_json,
        }
    )
    return execute_main(argv=argv, popen=popen)


def execute_on_capture(
    version: str,
    days_later: float = 0,
    additional_argv: list[str] | None = None,
) -> MockResult:
    """Execute the timers check on the outputs captured with systemd
    ``version``, ``days_later`` days after the capture."""
    with freeze_time(CAPTURE_TIMES[version] + days_later * DAY):
        return execute_on_host(
            f"systemctl-list-timers_{version}.txt",
            f"systemctl-list-timers_{version}.json",
            additional_argv,
        )


def execute_with_opt_t(
    additional_argv: list[str] | None = None,
    stdout_timers_suffix: str = "1",
    warning: int | None = None,
    critical: int | None = None,
) -> MockResult:
    argv = ["--timers", "--no-performance-data"]
    if warning:
        argv += ["--timers-warning", str(warning)]
    if critical:
        argv += ["--timers-critical", str(critical)]

    if additional_argv:
        argv += additional_argv

    return execute_main(
        argv=argv,
        stdout=[
            "systemctl-list-units_3units.txt",
            "systemd-analyze_12.345.txt",
            f"systemctl-list-timers_{stdout_timers_suffix}.txt",
        ],
    )


class TestScopeTimers:
    def test_dead_timers_1(self) -> None:
        result = execute_with_opt_t()
        result.assert_critical()
        assert "SYSTEMD CRITICAL - phpsessionclean.timer" == result.first_line

    def test_dead_timers_2(self) -> None:
        result = execute_with_opt_t(stdout_timers_suffix="2")
        result.assert_critical()
        result.assert_first_line("SYSTEMD CRITICAL - dfm-auto-jf.timer, rsync.timer")

    @pytest.mark.skip(reason="use freezegun")
    def test_dead_timers_2_ok(self) -> None:
        result = execute_with_opt_t(
            stdout_timers_suffix="2", warning=2764801, critical=2764802
        )
        result.assert_ok()

    @pytest.mark.skip(reason="use freezegun")
    def test_dead_timers_2_warning(self) -> None:
        result = execute_with_opt_t(
            stdout_timers_suffix="2", warning=2764799, critical=2764802
        )
        result.assert_warn()

    @pytest.mark.skip(reason="use freezegun")
    def test_dead_timers_2_warning_equal(self) -> None:
        result = execute_with_opt_t(
            stdout_timers_suffix="2", warning=2764800, critical=2764802
        )
        result.assert_warn()

    def test_dead_timers_ok(self) -> None:
        result = execute_with_opt_t(stdout_timers_suffix="ok")
        result.assert_ok()
        result.assert_first_line("SYSTEMD OK - all")

    def test_dead_timers_exclude(self) -> None:
        result = execute_with_opt_t(
            stdout_timers_suffix="2", additional_argv=["-e", "dfm-auto-jf.timer"]
        )
        result.assert_critical()
        result.assert_first_line("SYSTEMD CRITICAL - rsync.timer")

    def test_dead_timers_exclude_multiple(self) -> None:
        result = execute_with_opt_t(
            stdout_timers_suffix="2",
            additional_argv=["-e", "dfm-auto-jf.timer", "-e", "rsync.timer"],
        )
        result.assert_ok()

    def test_dead_timers_exclude_regexp(self) -> None:
        result = execute_with_opt_t(
            stdout_timers_suffix="2",
            additional_argv=["-e", "dfm-auto-jf.timer", "-e", ".*timer"],
        )
        result.assert_ok()

    def test_all_n_a(self) -> None:
        """n/a -> not available"""
        result = execute_with_opt_t(stdout_timers_suffix="all-n-a")
        result.assert_critical()


@pytest.mark.parametrize("version", ["v252", "v257"])
class TestSystemd252AndLater:
    """systemd 252 prints ``-`` instead of ``n/a`` for a timestamp that is not
    set, and systemd 254 aligns the LEFT and PASSED columns to the right. The
    text table of these versions hides dead timers, so the check reads the
    JSON output.

    Both captures have two timers that have no next run: ``dead-test.timer``
    (``OnCalendar=2000-01-01``) never ran, and ``once-test.timer``
    (``OnActiveSec=1s``) ran once, less than 5 seconds before the capture.
    All the other timers are stock Debian timers.
    """

    def test_timer_that_never_ran(self, version: str) -> None:
        result = execute_on_capture(version)
        result.assert_critical()
        result.assert_first_line("SYSTEMD CRITICAL - dead-test.timer")

    def test_timer_that_ran_seconds_ago(self, version: str) -> None:
        result = execute_on_capture(version, additional_argv=["-e", "dead-test.timer"])
        result.assert_ok()
        result.assert_first_line("SYSTEMD OK - all")

    def test_timer_that_ran_6_days_ago(self, version: str) -> None:
        result = execute_on_capture(
            version, days_later=6.1, additional_argv=["-e", "dead-test.timer"]
        )
        result.assert_warn()
        result.assert_first_line("SYSTEMD WARNING - once-test.timer")

    def test_timer_that_ran_7_days_ago(self, version: str) -> None:
        result = execute_on_capture(
            version, days_later=7.1, additional_argv=["-e", "dead-test.timer"]
        )
        result.assert_critical()
        result.assert_first_line("SYSTEMD CRITICAL - once-test.timer")


def test_systemd_245_prints_the_table_for_output_json() -> None:
    """systemd 245 and older ignore ``--output=json`` and print the text
    table, which is parsed instead."""
    result = execute_on_host(
        "systemctl-list-timers_1.txt", "systemctl-list-timers_1.txt"
    )
    result.assert_critical()
    result.assert_first_line("SYSTEMD CRITICAL - phpsessionclean.timer")
