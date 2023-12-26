import unittest

from tests.helper import execute_main


class TestVersion246(unittest.TestCase):
    def test_version_246(self) -> None:
        result = execute_main(
            argv=["--no-performance-data"],
            stdout=[
                "systemctl-list-units_v246.txt",
                "systemd-analyze_12.345.txt",
            ],
        )
        result.assert_critical()
        result.assert_first_line("SYSTEMD CRITICAL - nm-wait-online.service: failed")


if __name__ == "__main__":
    unittest.main()
