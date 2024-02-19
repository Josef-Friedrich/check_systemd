import unittest

from tests.helper import execute_main


class TestPerformanceData(unittest.TestCase):
    def test_ok(self) -> None:
        result = execute_main(argv=["--performance-data"])
        result.assert_ok()
        result.assert_first_line(
            "SYSTEMD OK - all "
            "| count_units=386 startup_time=12.345;60;120 "
            "units_activating=0 "
            "units_active=275 units_failed=0 units_inactive=111"
        )

    def test_dead_timers(self) -> None:
        result = execute_main(
            argv=["--timers"],
            stdout=[
                "systemctl-list-units_3units.txt",
                "systemd-analyze_12.345.txt",
                "systemctl-list-timers_1.txt",
            ],
        )
        result.assert_critical()
        result.assert_first_line(
            "SYSTEMD CRITICAL - phpsessionclean.timer "
            "| count_units=3 startup_time=12.345;60;120 "
            "units_activating=0 "
            "units_active=3 units_failed=0 units_inactive=0"
        )

    def test_options_exclude(self) -> None:
        result = execute_main(
            argv=["-e", "testX.service"],
            stdout=[
                "systemctl-list-units_failed.txt",
                "systemd-analyze_12.345.txt",
            ],
        )
        result.assert_critical()
        result.assert_first_line(
            "SYSTEMD CRITICAL - smartd.service: failed | count_units=3 "
            "startup_time=12.345;60;120 "
            "units_activating=0 units_active=1 units_failed=1 "
            "units_inactive=1"
        )


if __name__ == "__main__":
    unittest.main()
