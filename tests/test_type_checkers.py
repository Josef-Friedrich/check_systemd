import pytest

from check_systemd import (
    _check_active_state,  # type: ignore
    _check_load_state,  # type: ignore
    _check_sub_state,  # type: ignore
)


def test_check_active_state() -> None:
    assert _check_active_state("deactivating") == "deactivating"
    assert _check_active_state("invalid") is None


def test_check_sub_state() -> None:
    assert _check_sub_state("tentative") == "tentative"
    assert _check_sub_state("invalid") is None


def test_check_load_state() -> None:
    assert _check_load_state("loaded") == "loaded"
    assert _check_load_state("invalid") is None
