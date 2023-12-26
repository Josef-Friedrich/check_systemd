import unittest

from tests.helper import MPopen, execute_main


class TestBootupNotFinished(unittest.TestCase):
    def test_bootup_not_finished(self) -> None:
        result = execute_main(
            argv=["--no-performance-data"],
            popen=(
                MPopen(stdout="systemctl-list-units_ok.txt"),
                MPopen(returncode=1, stderr="systemd-analyze_not-finished.txt"),
            ),
        )
        result.assert_ok()
        result.assert_first_line("SYSTEMD OK - all")

    def test_bootup_not_finished_verbose(self) -> None:
        self.maxDiff = None
        result = execute_main(
            argv=["--verbose"],
            popen=(
                MPopen(stdout="systemctl-list-units_ok.txt"),
                MPopen(returncode=1, stderr="systemd-analyze_not-finished.txt"),
            ),
        )

        result.assert_ok()
        self.assertIn("SYSTEMD OK - all\n", result.output)


if __name__ == "__main__":
    unittest.main()
