"""Test the D-Bus API as a data source."""

from __future__ import annotations

from unittest.mock import patch

import check_systemd


class TestDbus:
    def test_mocking(self) -> None:
        with patch("sys.exit"), patch("check_systemd.is_dbus"), patch(
            "sys.argv", ["check_systemd.py", "--dbus"]
        ):
            check_systemd.main()  # type: ignore
