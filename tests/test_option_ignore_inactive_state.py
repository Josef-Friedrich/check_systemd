from __future__ import annotations

from tests.helper import execute_main


class TestOptionIgnoreInactiveState:
    def test_with(self) -> None:
        result = execute_main(
            argv=["--unit", "ansible-pull.service"],
            stdout=[
                "systemctl-list-units_inactive.txt",
                "systemctl-show-ansible-pull_inactive.txt",
                "systemd-analyze_12.345.txt",
            ],
        )
        result.assert_ok()
        result.assert_first_line(
            "SYSTEMD OK - ansible-pull.service: inactive | "
            "count_units=2 startup_time=12.3;60;120 "
            "units_activating=0 units_active=1 units_failed=0 units_inactive=1"
        )

    def test_ok(self) -> None:
        result = execute_main(
            argv=["--ignore-inactive-state", "--unit", "ansible-pull.service"],
            stdout=[
                "systemctl-list-units_inactive.txt",
                "systemctl-show-ansible-pull_inactive.txt",
                "systemd-analyze_12.345.txt",
            ],
        )
        result.assert_ok()
        result.assert_first_line(
            "SYSTEMD OK - ansible-pull.service: inactive | "
            "count_units=2 startup_time=12.3;60;120 "
            "units_activating=0 units_active=1 units_failed=0 units_inactive=1"
        )
