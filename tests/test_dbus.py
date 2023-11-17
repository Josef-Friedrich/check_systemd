"""Test the D-Bus API as a data source."""

import unittest
from unittest.mock import patch

import check_systemd


class TestDbus(unittest.TestCase):
    def test_mocking(self) -> None:
        with patch("sys.exit"), patch("check_systemd.is_gi"), patch(
            "check_systemd.DbusManager"
        ), patch("sys.argv", ["check_systemd.py", "--dbus"]):
            check_systemd.main()


if __name__ == "__main__":
    unittest.main()
