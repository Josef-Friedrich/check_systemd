"""Unit tests"""
from __future__ import annotations

from unittest.mock import patch

from check_systemd import _collect_properties  # type: ignore
from tests.helper import get_mocks_for_popen


def test_collect_properties() -> None:
    with patch("check_systemd.subprocess.Popen") as Popen:
        Popen.return_value = get_mocks_for_popen("systemctl-show-nginx_active.txt")[0]
        properties = _collect_properties("unit")
    assert properties["Id"] == "nginx.service"
    assert properties["ActiveState"] == "active"
    assert properties["SubState"] == "running"
    assert properties["LoadState"] == "loaded"
