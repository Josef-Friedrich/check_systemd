import unittest

from tests.helper import execute_main


def execute_with_opt_t(
    additional_argv=None, stdout_timers_suffix="1", warning=None, critical=None
):
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
            "systemctl-list-timers_{}.txt".format(stdout_timers_suffix),
        ],
    )


class TestScopeTimers(unittest.TestCase):
    def test_dead_timers_1(self) -> None:
        result = execute_with_opt_t()
        result.assert_critical()
        self.assertEqual("SYSTEMD CRITICAL - phpsessionclean.timer", result.first_line)

    def test_dead_timers_2(self) -> None:
        result = execute_with_opt_t(stdout_timers_suffix="2")
        result.assert_critical()
        result.assert_first_line("SYSTEMD CRITICAL - dfm-auto-jf.timer, " "rsync.timer")

    def test_dead_timers_2_ok(self) -> None:
        result = execute_with_opt_t(
            stdout_timers_suffix="2", warning=2764801, critical=2764802
        )
        result.assert_ok()

    def test_dead_timers_2_warning(self) -> None:
        result = execute_with_opt_t(
            stdout_timers_suffix="2", warning=2764799, critical=2764802
        )
        result.assert_warn()

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


if __name__ == "__main__":
    unittest.main()
