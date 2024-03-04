"""Tests related to data acquisition of systemd units."""

from __future__ import annotations

from typing import Sequence

from check_systemd import Source

Unit = Source.Unit
Cache = Source.Cache
NameFilter = Source.NameFilter

unit_modem_manager = Unit(
    name="ModemManager.service",
    active_state="active",
    sub_state="running",
    load_state="loaded",
)
unit_mongod = Unit(
    name="mongod.service",
    active_state="failed",
    sub_state="running",
    load_state="loaded",
)
unit_mysql = Unit(
    name="mysql.service",
    active_state="active",
    sub_state="running",
    load_state="loaded",
)
unit_named = Unit(
    name="named.service",
    active_state="active",
    sub_state="running",
    load_state="loaded",
)
unit_networking = Unit(
    name="networking.mount",
    active_state="active",
    sub_state="mounting-done",
    load_state="loaded",
)
unit_nginx = Unit(
    name="nginx.service",
    active_state="active",
    sub_state="running",
    load_state="loaded",
)
unit_nmdb = Unit(
    name="nmbd.timer", active_state="active", sub_state="running", load_state="loaded"
)
unit_php = Unit(
    name="php7.4-fpm.service",
    active_state="active",
    sub_state="running",
    load_state="loaded",
)


class TestClassUnit:
    def test_initialization(self) -> None:
        unit = Unit(
            name="test.service",
            active_state="active",
            sub_state="running",
            load_state="loaded",
        )
        assert "test.service" == unit.name
        assert "active" == unit.active_state
        assert "running" == unit.sub_state
        assert "loaded" == unit.load_state
        assert "active" == unit.active_state


class TestClassCache:
    unit_cache: Source.Cache[Unit]

    def setup_method(self) -> None:
        self.unit_cache = Source.Cache[Unit]()
        self.unit_cache.add(unit_modem_manager.name, unit_modem_manager)
        self.unit_cache.add(unit_mongod.name, unit_mongod)
        self.unit_cache.add(unit_mysql.name, unit_mysql)
        self.unit_cache.add(unit_named.name, unit_named)
        self.unit_cache.add(unit_networking.name, unit_networking)
        self.unit_cache.add(unit_nginx.name, unit_nginx)
        self.unit_cache.add(unit_modem_manager.name, unit_modem_manager)
        self.unit_cache.add(unit_nmdb.name, unit_nmdb)
        self.unit_cache.add(unit_php.name, unit_php)

    def filter(
        self,
        include: str | Sequence[str] | None = None,
        exclude: str | Sequence[str] | None = None,
    ) -> list[str]:
        units: list[str] = []
        for unit in self.unit_cache.filter(include=include, exclude=exclude):
            units.append(unit.name)
        return units

    def test_iterator(self) -> None:
        units = list(self.unit_cache)
        assert units[0].name == "ModemManager.service"

    def test_method_get(self) -> None:
        unit = self.unit_cache.get(name="ModemManager.service")
        assert unit
        assert "ModemManager.service" == unit.name

    def test_method_list(self) -> None:
        units = self.filter()
        assert 8 == len(units)

    def test_method_list_include(self) -> None:
        units = self.filter(include="XXX")
        assert 0 == len(units)

        units = self.filter(include="named.service")
        assert 1 == len(units)

        units = self.filter(include="n.*")
        assert 4 == len(units)

    def test_method_list_include_multiple(self) -> None:
        units = self.filter(include=("n.*", "p.*"))
        assert 5 == len(units)

    def test_method_list_exclude(self) -> None:
        units = self.filter(exclude="named.service")
        assert 7 == len(units)

        units = self.filter(exclude=r".*\.(mount|timer)")
        assert 6 == len(units)

    def test_method_list_exclude_multiple(self) -> None:
        units = self.filter(exclude=("named.service", "nmbd.timer"))
        assert 6 == len(units)

    def test_method_count_by_states(self) -> None:
        counter = self.unit_cache.count_by_states(
            ("active_state:active", "active_state:failed")
        )
        assert counter["active_state:active"] == 7
        assert counter["active_state:failed"] == 1


class TestClassNameFilter:
    __filter: NameFilter

    def setup_method(self) -> None:
        self.__filter = NameFilter()
        self.__filter.add("php7.4-fpm.service")
        self.__filter.add("ModemManager.service")
        self.__filter.add("mongod.service")
        self.__filter.add("mysql.service")
        self.__filter.add("named.service")
        self.__filter.add("networking.mount")
        self.__filter.add("nginx.service")
        self.__filter.add("nmbd.timer")

    def filter(
        self,
        include: str | Sequence[str] | None = None,
        exclude: str | Sequence[str] | None = None,
    ) -> list[str]:
        unit_names: list[str] = []
        for unit_name in self.__filter.filter(include=include, exclude=exclude):
            unit_names.append(unit_name)
        return unit_names

    def test_initialization_with_arg(self) -> None:
        filter = NameFilter(["test1.service", "test2.service"])
        assert 2 == len(filter.get())

    def test_iterator(self) -> None:
        names: list[str] = []
        for name in self.__filter:
            names.append(name)
        assert names == [
            "ModemManager.service",
            "mongod.service",
            "mysql.service",
            "named.service",
            "networking.mount",
            "nginx.service",
            "nmbd.timer",
            "php7.4-fpm.service",
        ]

    def test_method_list(self) -> None:
        units = self.filter()
        assert 8 == len(units)

    def test_method_list_include(self) -> None:
        units = self.filter(include="XXX")
        assert 0 == len(units)

        units = self.filter(include="named.service")
        assert 1 == len(units)

        units = self.filter(include="n.*")
        assert 4 == len(units)

    def test_method_list_include_multiple(self) -> None:
        units = self.filter(include=("n.*", "p.*"))
        assert 5 == len(units)

    def test_method_list_exclude(self) -> None:
        units = self.filter(exclude="named.service")
        assert 7 == len(units)

        units = self.filter(exclude=r".*\.(mount|timer)")
        assert 6 == len(units)

    def test_method_list_exclude_multiple(self) -> None:
        units = self.filter(exclude=("named.service", "nmbd.timer"))
        assert 6 == len(units)

    def test_method_list_include_exclude_empty_list(self) -> None:
        units = self.filter(include=[], exclude=[])
        assert 8 == len(units)
