from __future__ import annotations

import pytest

from check_systemd import Source

Unit = Source.Unit

check_active_state = Unit._Unit__check_active_state  # type: ignore


def test_check_active_state() -> None:
    assert check_active_state("deactivating") == "deactivating"
    with pytest.raises(ValueError):
        check_active_state("invalid")


check_sub_state = Unit._Unit__check_sub_state  # type: ignore


def test_check_sub_state() -> None:
    assert check_sub_state("tentative") == "tentative"
    with pytest.raises(ValueError):
        check_sub_state("invalid")


check_load_state = Unit._Unit__check_load_state  # type: ignore


def test_check_load_state() -> None:
    assert check_load_state("loaded") == "loaded"
    with pytest.raises(ValueError):
        check_load_state("invalid")
