from tests.helper import execute_main


def execute(argv, units_suffix="ok"):
    return execute_main(
        argv=argv,
        stdout=[
            "systemctl-list-units_{}.txt".format(units_suffix),
            "systemd-analyze_12.345.txt",
        ],
    )


class TestOk:
    def test_ok(self) -> None:
        result = execute(argv=["--no-performance-data"])
        result.assert_ok()
        result.assert_first_line("SYSTEMD OK - all")

    def test_multiple_units(self) -> None:
        result = execute_main(argv=["--no-performance-data"])
        result.assert_ok()
        result.assert_first_line("SYSTEMD OK - all")


class TestFailure:
    def test_failure(self) -> None:
        result = execute(argv=["--no-performance-data"], units_suffix="failed")
        result.assert_critical()
        result.assert_first_line("SYSTEMD CRITICAL - smartd.service: failed")


class TestMultipleFailure:
    def test_failure_multiple(self) -> None:
        result = execute(
            argv=["--no-performance-data"], units_suffix="multiple-failure"
        )
        result.assert_critical()
        if result.first_line:
            assert "rtkit-daemon.service: failed" in result.first_line
            assert "smartd.service: failed" in result.first_line
