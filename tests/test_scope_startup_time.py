from __future__ import annotations

from tests.helper import execute_main


class TestScopeStartupTime:
    def test_option_critical(self) -> None:
        result = execute_main(argv=["-c", "1", "--no-performance-data"])
        result.assert_critical()
        result.assert_first_line(
            "SYSTEMD CRITICAL - startup_time is 12.35 (outside range 0:1)"
        )

    def test_option_warning(self) -> None:
        result = execute_main(argv=["-w", "2", "--no-performance-data"])
        result.assert_warn()
        result.assert_first_line(
            "SYSTEMD WARNING - startup_time is 12.35 (outside range 0:2)"
        )

    def test_option_no_startup_time_long(self) -> None:
        result = execute_main(
            argv=["-c", "1", "--no-startup-time", "--no-performance-data"]
        )
        result.assert_ok()
        result.assert_first_line("SYSTEMD OK - all")

    def test_option_no_startup_time_short(self) -> None:
        result = execute_main(argv=["-c", "1", "-n"])
        result.assert_ok()
