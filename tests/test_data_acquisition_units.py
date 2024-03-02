"""Tests related to data acquisition of systemd units."""

from __future__ import annotations

from typing import Sequence

from check_systemd import Unit, UnitCache, UnitNameFilter

unit_modem_manager = Unit(
    name="ModemManager.service",
    active_state="active",
    sub_state="sub",
    load_state="load",
)
unit_mongod = Unit(
    name="mongod.service", active_state="failed", sub_state="sub", load_state="load"
)
unit_mysql = Unit(
    name="mysql.service", active_state="active", sub_state="sub", load_state="load"
)
unit_named = Unit(
    name="named.service", active_state="active", sub_state="sub", load_state="load"
)
unit_networking = Unit(
    name="networking.mount", active_state="active", sub_state="sub", load_state="load"
)
unit_nginx = Unit(
    name="nginx.service", active_state="active", sub_state="sub", load_state="load"
)
unit_nmdb = Unit(
    name="nmbd.timer", active_state="active", sub_state="sub", load_state="load"
)
unit_php = Unit(
    name="php7.4-fpm.service", active_state="active", sub_state="sub", load_state="load"
)


class TestClassUnit:
    def test_initialization(self) -> None:
        unit = Unit(
            name="test.service",
            active_state="active",
            sub_state="sub",
            load_state="load",
        )
        assert "test.service" == unit.name
        assert "active" == unit.active_state
        assert "sub" == unit.sub_state
        assert "load" == unit.load_state
        assert "active" == unit.active_state


class TestClassUnitCache:
    unit_cache: UnitCache

    def setup_method(self) -> None:
        self.unit_cache = UnitCache()
        self.unit_cache.add_unit(unit_modem_manager)
        self.unit_cache.add_unit(unit_mongod)
        self.unit_cache.add_unit(unit_mysql)
        self.unit_cache.add_unit(unit_named)
        self.unit_cache.add_unit(unit_networking)
        self.unit_cache.add_unit(unit_nginx)
        self.unit_cache.add_unit(unit_modem_manager)
        self.unit_cache.add_unit(unit_nmdb)
        self.unit_cache.add_unit(unit_php)

    def list(
        self,
        include: str | Sequence[str] | None = None,
        exclude: str | Sequence[str] | None = None,
    ) -> list[str]:
        units: list[str] = []
        for unit in self.unit_cache.list(include=include, exclude=exclude):
            units.append(unit.name)
        return units

    def test_method_add_with_kwargs(self) -> None:
        assert 8 == self.unit_cache.count
        unit = self.unit_cache.add_unit(
            name="test.service",
            active_state="active",
            sub_state="running",
            load_state="loaded",
        )
        assert unit.name == "test.service"
        assert 9 == self.unit_cache.count

    def test_method_get(self) -> None:
        unit = self.unit_cache.get(name="ModemManager.service")
        assert unit
        assert "ModemManager.service" == unit.name

    def test_method_list(self) -> None:
        units = self.list()
        assert 8 == len(units)

    def test_method_list_include(self) -> None:
        units = self.list(include="XXX")
        assert 0 == len(units)

        units = self.list(include="named.service")
        assert 1 == len(units)

        units = self.list(include="n.*")
        assert 4 == len(units)

    def test_method_list_include_multiple(self) -> None:
        units = self.list(include=("n.*", "p.*"))
        assert 5 == len(units)

    def test_method_list_exclude(self) -> None:
        units = self.list(exclude="named.service")
        assert 7 == len(units)

        units = self.list(exclude=r".*\.(mount|timer)")
        assert 6 == len(units)

    def test_method_list_exclude_multiple(self) -> None:
        units = self.list(exclude=("named.service", "nmbd.timer"))
        assert 6 == len(units)

    def test_method_count_by_states(self) -> None:
        counter = self.unit_cache.count_by_states(
            ("active_state:active", "active_state:failed")
        )
        assert counter["active_state:active"] == 7
        assert counter["active_state:failed"] == 1


class TestClassUnitNameFilter:
    def setup_method(self) -> None:
        self.filter = UnitNameFilter()
        self.filter.add("ModemManager.service")
        self.filter.add("mongod.service")
        self.filter.add("mysql.service")
        self.filter.add("named.service")
        self.filter.add("networking.mount")
        self.filter.add("nginx.service")
        self.filter.add("nmbd.timer")
        self.filter.add("php7.4-fpm.service")

    def list(
        self,
        include: str | Sequence[str] | None = None,
        exclude: str | Sequence[str] | None = None,
    ):
        unit_names: list[str] = []
        for unit_name in self.filter.list(include=include, exclude=exclude):
            unit_names.append(unit_name)
        return unit_names

    def test_initialization_with_arg(self) -> None:
        filter = UnitNameFilter(["test1.service", "test2.service"])
        assert 2 == len(filter.get())

    def test_method_list(self) -> None:
        units = self.list()
        assert 8 == len(units)

    def test_method_list_include(self) -> None:
        units = self.list(include="XXX")
        assert 0 == len(units)

        units = self.list(include="named.service")
        assert 1 == len(units)

        units = self.list(include="n.*")
        assert 4 == len(units)

    def test_method_list_include_multiple(self) -> None:
        units = self.list(include=("n.*", "p.*"))
        assert 5 == len(units)

    def test_method_list_exclude(self) -> None:
        units = self.list(exclude="named.service")
        assert 7 == len(units)

        units = self.list(exclude=r".*\.(mount|timer)")
        assert 6 == len(units)

    def test_method_list_exclude_multiple(self) -> None:
        units = self.list(exclude=("named.service", "nmbd.timer"))
        assert 6 == len(units)

    def test_method_list_include_exclude_empty_list(self) -> None:
        units = self.list(include=[], exclude=[])
        assert 8 == len(units)
