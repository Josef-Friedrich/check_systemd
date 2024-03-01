from __future__ import annotations

from tests.helper import execute_main


def execute_with_opt_u(argv: list[str], list_units: str = "ok"):
    if "--no-performance-data" not in argv:
        argv.append("--no-performance-data")
    return execute_main(
        argv=argv,
        stdout=[
            "systemctl-list-units_{}.txt".format(list_units),
            "systemctl-show-nginx_active.txt",
            "systemd-analyze_12.345.txt",
        ],
    )


class TestOptionUnit:
    def test_ok(self) -> None:
        result = execute_with_opt_u(argv=["--unit", "nginx.service"], list_units="ok")
        result.assert_ok()
        result.assert_first_line("SYSTEMD OK - nginx.service: active")

    def test_failed(self) -> None:
        result = execute_with_opt_u(
            argv=["--unit", "smartd.service"], list_units="failed"
        )
        result.assert_critical()
        result.assert_first_line("SYSTEMD CRITICAL - smartd.service: failed")

    def test_different_unit_name(self) -> None:
        result = execute_with_opt_u(argv=["--unit", "XXXXX.service"], list_units="ok")
        result.assert_unknown()
        result.assert_first_line(
            "SYSTEMD UNKNOWN: ValueError: Please verify your --include-* and "
            "--exclude-* options. No units have been added for testing."
        )
