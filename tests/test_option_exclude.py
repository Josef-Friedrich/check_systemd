from __future__ import annotations

from tests.helper import MockResult, execute_main


def execute_with_opt_e(argv: list[str], unit_suffix: str = "failed") -> MockResult:
    return execute_main(
        argv=argv,
        stdout=[
            "systemctl-list-units_{}.txt".format(unit_suffix),
            "systemd-analyze_12.345.txt",
        ],
    )


class TestOptionExclude:
    def test_known_service(self) -> None:
        result = execute_with_opt_e(
            argv=["-e", "smartd.service", "--no-performance-data"],
            unit_suffix="failed",
        )
        result.assert_ok()
        result.assert_first_line("SYSTEMD OK - all")

    def test_unknown_service(self) -> None:
        result = execute_with_opt_e(
            argv=["-e", "testX.service", "--no-performance-data"],
            unit_suffix="failed",
        )
        result.assert_critical()
        result.assert_first_line("SYSTEMD CRITICAL - smartd.service: failed")

    def test_regexp(self) -> None:
        result = execute_with_opt_e(
            argv=["-e", "user@\\d+\\.service", "--no-performance-data"],
            unit_suffix="regexp-excludes",
        )
        result.assert_ok()
        result.assert_first_line("SYSTEMD OK - all")

    def test_regexp_dot(self) -> None:
        result = execute_with_opt_e(
            argv=["-e", ".*", "--no-performance-data"],
            unit_suffix="regexp-excludes",
        )
        result.assert_unknown()

    def test_invalid_regexp(self) -> None:
        result = execute_with_opt_e(
            argv=["-e", "*service"],
            unit_suffix="ok",
        )
        result.assert_unknown()
        result.assert_first_line(
            "SYSTEMD UNKNOWN: check_systemd.CheckSystemdRegexpError: "
            "Invalid regular expression: '*service'"
        )
