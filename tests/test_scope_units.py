import unittest

from tests.helper import execute_main


def execute(argv, units_suffix="ok"):
    return execute_main(
        argv=argv,
        stdout=[
            "systemctl-list-units_{}.txt".format(units_suffix),
            "systemd-analyze_12.345.txt",
        ],
    )


class TestOk(unittest.TestCase):
    def test_ok(self) -> None:
        result = execute(argv=["--no-performance-data"])
        result.assert_ok()
        result.assert_first_line("SYSTEMD OK - all")

    def test_multiple_units(self) -> None:
        result = execute_main(argv=["--no-performance-data"])
        result.assert_ok()
        result.assert_first_line("SYSTEMD OK - all")


class TestFailure(unittest.TestCase):
    def test_failure(self) -> None:
        result = execute(argv=["--no-performance-data"], units_suffix="failed")
        result.assert_critical()
        result.assert_first_line("SYSTEMD CRITICAL - smartd.service: failed")


class TestMultipleFailure(unittest.TestCase):
    def test_failure_multiple(self) -> None:
        result = execute(
            argv=["--no-performance-data"], units_suffix="multiple-failure"
        )
        result.assert_critical()
        if result.first_line:
            self.assertIn("rtkit-daemon.service: failed", result.first_line)
            self.assertIn("smartd.service: failed", result.first_line)


if __name__ == "__main__":
    unittest.main()
