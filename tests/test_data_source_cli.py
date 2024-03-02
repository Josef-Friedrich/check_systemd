"""Unit tests"""
from __future__ import annotations

from unittest.mock import patch

from check_systemd import CliSource
from tests.helper import get_mocks_for_popen


def test_collect_properties() -> None:
    with patch("check_systemd.subprocess.Popen") as Popen:
        Popen.return_value = get_mocks_for_popen("systemctl-show-nginx_active.txt")[0]
        unit = CliSource().get_unit("nginx.service")
    assert unit.name == "nginx.service"
    assert unit.active_state == "active"
    assert unit.sub_state == "running"
    assert unit.load_state == "loaded"
