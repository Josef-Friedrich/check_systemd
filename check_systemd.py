#!/usr/bin/env python3

"""
``check_system`` is a `Nagios <https://www.nagios.org>`_ / `Icinga
<https://icinga.com>`_ monitoring plugin to check systemd. This Python script
will report a degraded system to your monitoring solution. It can also be used
to monitor individual systemd services (with the ``-u, --unit`` parameter) and
timers units (with the ``-t, --dead-timers`` parameter).

To learn more about the project, please visit the repository on `Github
<https://github.com/Josef-Friedrich/check_systemd>`_.

Monitoring scopes
=================

* ``units``: State of unites
* ``timers``: Timers
* ``startup_time``: Startup time
* ``performance_data``: Performance data

Data sources
============

* D-Bus (``dbus``)
* Command line interface (``cli``)

This plugin is based on a Python package named `nagiosplugin
<https://pypi.org/project/nagiosplugin/>`_. ``nagiosplugin`` has a fine-grained
class model to separate concerns. A Nagios / Icinga plugin must perform these
three steps: data `acquisition`, `evaluation` and `presentation`.
``nagiosplugin`` provides for this three steps three classes: ``Resource``,
``Context``, ``Summary``. ``check_systemd`` extends this three model classes in
the following subclasses:

Acquisition (``Resource``)
==========================

* :class:`UnitsResource` (``context=units``)
* :class:`TimersResource` (``context=timers``)
* :class:`StartupTimeResource` (``context=startup_time``)
* :class:`PerformanceDataResource` (``context=performance_data``)

Evaluation (``Context``)
========================

* :class:`UnitsContext` (``context=units``)
* :class:`TimersContext` (``context=timers``)
* :class:`StartupTimeContext` (``context=timers``)
* :class:`PerformanceDataContext` (``context=performance_data``)

Presentation (``Summary``)
==========================

* :class:`SystemdSummary`
"""

from __future__ import annotations

import argparse
import logging
import re
import subprocess
from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import (
    Any,
    Generator,
    Generic,
    Iterable,
    Literal,
    MutableSequence,
    NamedTuple,
    Optional,
    Sequence,
    TypeVar,
    Union,
    cast,
    get_args,
    overload,
)

try:
    import nagiosplugin
    from nagiosplugin.check import Check
    from nagiosplugin.context import Context, ScalarContext
    from nagiosplugin.error import CheckError
    from nagiosplugin.metric import Metric
    from nagiosplugin.performance import Performance
    from nagiosplugin.range import Range
    from nagiosplugin.resource import Resource
    from nagiosplugin.result import Result, Results
    from nagiosplugin.state import Critical, Ok, ServiceState, Warn
    from nagiosplugin.summary import Summary
except ImportError:
    print("Failed to import the NagiosPlugin library.")
    exit(3)

is_dbus = True

try:
    # Look for gi https://gnome.pages.gitlab.gnome.org/pygobject
    from gi.repository.Gio import BusType, DBusProxy, DBusProxyFlags
except ImportError:
    # Fallback to the command line interface source.
    is_dbus = False


__version__: str = "4.1.0"

ActiveState = Literal[
    "active", "reloading", "inactive", "failed", "activating", "deactivating"
]
"""From the `D-Bus interface of systemd documentation
<https://www.freedesktop.org/software/systemd/man/org.freedesktop.systemd1.html#Properties1>`_:

``ActiveState`` contains a state value that reflects whether the unit
is currently active or not. The following states are currently defined:

* ``active``,
* ``reloading``,
* ``inactive``,
* ``failed``,
* ``activating``, and
* ``deactivating``.

``active`` indicates that unit is active (obviously...).

``reloading`` indicates that the unit is active and currently reloading
its configuration.

``inactive`` indicates that it is inactive and the previous run was
successful or no previous run has taken place yet.

``failed`` indicates that it is inactive and the previous run was not
successful (more information about the reason for this is available on
the unit type specific interfaces, for example for services in the
Result property, see below).

``activating`` indicates that the unit has previously been inactive but
is currently in the process of entering an active state.

Conversely ``deactivating`` indicates that the unit is currently in the
process of deactivation.
"""


SubState = Literal[
    "abandoned",
    "activating-done",
    "activating",
    "active",
    "auto-restart",
    "cleaning",
    "condition",
    "deactivating-sigkill",
    "deactivating-sigterm",
    "deactivating",
    "dead",
    "elapsed",
    "exited",
    "failed",
    "final-sigkill",
    "final-sigterm",
    "final-watchdog",
    "listening",
    "mounted",
    "mounting-done",
    "mounting",
    "plugged",
    "reload",
    "remounting-sigkill",
    "remounting-sigterm",
    "remounting",
    "running",
    "start-chown",
    "start-post",
    "start-pre",
    "start",
    "stop-post",
    "stop-pre-sigkill",
    "stop-pre-sigterm",
    "stop-pre",
    "stop-sigkill",
    "stop-sigterm",
    "stop-watchdog",
    "stop",
    "tentative",
    "unmounting-sigkill",
    "unmounting-sigterm",
    "unmounting",
    "waiting",
]
"""From the `D-Bus interface of systemd documentation
<https://www.freedesktop.org/software/systemd/man/org.freedesktop.systemd1.html#Properties1>`_:

``SubState`` encodes states of the same state machine that
``ActiveState`` covers, but knows more fine-grained states that are
unit-type-specific. Where ``ActiveState`` only covers six high-level
states, ``SubState`` covers possibly many more low-level
unit-type-specific states that are mapped to the six high-level states.
Note that multiple low-level states might map to the same high-level
state, but not vice versa. Not all high-level states have low-level
counterparts on all unit types.

All sub states are listed in the file `basic/unit-def.c
<https://github.com/systemd/systemd/blob/main/src/basic/unit-def.c>`_
of the systemd source code:

* automount: ``dead``, ``waiting``, ``running``, ``failed``
* device: ``dead``, ``tentative``, ``plugged``
* mount: ``dead``, ``mounting``, ``mounting-done``, ``mounted``,
    ``remounting``, ``unmounting``, ``remounting-sigterm``,
    ``remounting-sigkill``, ``unmounting-sigterm``,
    ``unmounting-sigkill``, ``failed``, ``cleaning``
* path: ``dead``, ``waiting``, ``running``, ``failed``
* scope: ``dead``, ``running``, ``abandoned``, ``stop-sigterm``,
    ``stop-sigkill``, ``failed``
* service: ``dead``, ``condition``, ``start-pre``, ``start``,
    ``start-post``, ``running``, ``exited``, ``reload``, ``stop``,
    ``stop-watchdog``, ``stop-sigterm``, ``stop-sigkill``, ``stop-post``,
    ``final-watchdog``, ``final-sigterm``, ``final-sigkill``, ``failed``,
    ``auto-restart``, ``cleaning``
* slice: ``dead``, ``active``
* socket: ``dead``, ``start-pre``, ``start-chown``, ``start-post``,
    ``listening``, ``running``, ``stop-pre``, ``stop-pre-sigterm``,
    ``stop-pre-sigkill``, ``stop-post``, ``final-sigterm``,
    ``final-sigkill``, ``failed``, ``cleaning``
* swap: ``dead``, ``activating``, ``activating-done``, ``active``,
    ``deactivating``, ``deactivating-sigterm``, ``deactivating-sigkill``,
    ``failed``, ``cleaning``
* target:``dead``, ``active``
* timer: ``dead``, ``waiting``, ``running``, ``elapsed``, ``failed``
"""


LoadState = Literal[
    "stub", "loaded", "not-found", "bad-setting", "error", "merged", "masked"
]
"""
`src/basic/unit-def.c#L95-L103 <https://github.com/systemd/systemd/blob/1f901c24530fb9b111126381a6ea101af8040e65/src/basic/unit-def.c#L95-L103>`_

From the `D-Bus interface of systemd documentation
<https://www.freedesktop.org/software/systemd/man/org.freedesktop.systemd1.html#Properties1>`_:

``LoadState`` contains a state value that reflects whether the
configuration file of this unit has been loaded. The following states
are currently defined:

* ``loaded``,
* ``error`` and
* ``masked``.

``loaded`` indicates that the configuration was successfully loaded.

``error`` indicates that the configuration failed to load, the
``LoadError`` field contains information about the cause of this
failure.

``masked`` indicates that the unit is currently masked out (i.e.
symlinked to /dev/null or suchlike).

Note that the ``LoadState`` is fully orthogonal to the ``ActiveState``
(see below) as units without valid loaded configuration might be active
(because configuration might have been reloaded at a time where a unit
was already active).
"""

UnitType = Literal[
    "service",
    "service",
    "socket",
    "target",
    "device",
    "mount",
    "automount",
    "timer",
    "swap",
    "path",
    "slice",
    "scope",
]


T = TypeVar("T")
"""For UnitCache. Can not be an inner typevar because of pylance"""


class Logger:
    """A wrapper around the Python logging module with 3 debug logging levels.

    1. ``-d``: info
    2. ``-dd``: debug
    3. ``-ddd``: verbose
    """

    __logger: logging.Logger

    __BLUE = "\x1b[0;34m"
    __PURPLE = "\x1b[0;35m"
    __CYAN = "\x1b[0;36m"
    __RESET = "\x1b[0m"

    __INFO = logging.INFO
    __DEBUG = logging.DEBUG
    __VERBOSE = 5

    def __init__(self) -> None:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        logging.basicConfig(handlers=[handler])
        self.__logger = logging.getLogger(__name__)

    def set_level(self, level: int) -> None:
        # NOTSET=0
        # custom level: VERBOSE=5
        # DEBUG=10
        # INFO=20
        # WARN=30
        # ERROR=40
        # CRITICAL=50
        if level == 1:
            self.__logger.setLevel(logging.INFO)
        elif level == 2:
            self.__logger.setLevel(logging.DEBUG)
        elif level > 2:
            self.__logger.setLevel(5)

    def __log(self, level: int, color: str, msg: str, *args: object) -> None:
        a: list[str] = []
        for arg in args:
            a.append(color + str(arg) + self.__RESET)
        self.__logger.log(level, msg, *a)

    def info(self, msg: str, *args: object) -> None:
        """Log on debug level ``1``: ``-d``.

        :param msg: A message format string. Note that this means that you can
            use keywords in the format string, together with a single
            dictionary argument. No ``%`` formatting operation is performed on
            ``msg`` when no args are supplied.
        :param args: The arguments which are merged into ``msg`` using the
            string formatting operator.
        """
        self.__log(self.__INFO, self.__BLUE, msg, *args)

    def debug(self, msg: str, *args: object) -> None:
        """Log on debug level ``2``: ``-dd``.

        :param msg: A message format string. Note that this means that you can
            use keywords in the format string, together with a single
            dictionary argument. No ``%`` formatting operation is performed on
            ``msg`` when no args are supplied.
        :param args: The arguments which are merged into ``msg`` using the
            string formatting operator.
        """
        self.__log(self.__DEBUG, self.__PURPLE, msg, *args)

    def verbose(self, msg: str, *args: object) -> None:
        """Log on debug level ``3``: ``-ddd``

        :param msg: A message format string. Note that this means that you can
            use keywords in the format string, together with a single
            dictionary argument. No ``%`` formatting operation is performed on
            ``msg`` when no args are supplied.
        :param args: The arguments which are merged into ``msg`` using the
            string formatting operator.
        """
        self.__log(self.__VERBOSE, self.__CYAN, msg, *args)

    def show_levels(self) -> None:
        msg = "log level %s (%s): %s"
        self.info(msg, 1, "info", "-d")
        self.debug(msg, 2, "debug", "-dd")
        self.verbose(msg, 3, "verbose", "-ddd")


logger = Logger()


class Source:
    class BaseUnit:
        name: str
        """The name of the system unit, for example ``nginx.service``. In the
        command line table of the command ``systemctl list-units`` is the
        column containing unit names titled with “UNIT”.
        """

    class Unit(BaseUnit):
        """This class bundles all state related informations of a systemd unit in a
        object. This class is inherited by the class ``DbusUnit`` and the
        attributes are overwritten by properties.
        """

        active_state: ActiveState

        sub_state: SubState

        load_state: LoadState

        @staticmethod
        def __check_active_state(state: object) -> ActiveState:
            states: tuple[ActiveState] = get_args(ActiveState)
            if state in states:
                # https://github.com/python/mypy/issues/9718
                return state  # type: ignore
            raise ValueError(f"Invalid active state: {state}")

        @staticmethod
        def __check_sub_state(state: object) -> SubState:
            states: tuple[SubState] = get_args(SubState)
            if state in states:
                return state  # type: ignore
            raise ValueError(f"Invalid sub state: {state}")

        @staticmethod
        def __check_load_state(state: object) -> LoadState:
            states: tuple[LoadState] = get_args(LoadState)
            if state in states:
                return state  # type: ignore
            raise ValueError(f"Invalid load state: {state}")

        def __init__(
            self,
            name: str,
            active_state: Optional[object] = None,
            sub_state: Optional[object] = None,
            load_state: Optional[object] = None,
        ) -> None:
            self.name = name
            self.active_state = self.__check_active_state(active_state)
            self.sub_state = self.__check_sub_state(sub_state)
            self.load_state = self.__check_load_state(load_state)

            logger.debug(
                "Create unit object: name: %s, active_state: %s, sub_state: %s, load_state: %s",
                self.name,
                self.active_state,
                self.sub_state,
                self.load_state,
            )

        def convert_to_exitcode(self) -> ServiceState:
            """Convert the different systemd states into a Nagios compatible
            exit code.

            :return: A Nagios compatible exit code: 0, 1, 2, 3
            """
            if opts.expected_state and opts.expected_state.lower() != self.active_state:
                return Critical
            if self.load_state == "error" or self.active_state == "failed":
                return Critical
            return Ok

    @dataclass
    class Timer(BaseUnit):
        """
        # Dbus doc
        # readonly t NextElapseUSecRealtime = ...;
        # readonly t NextElapseUSecMonotonic = ...;
        # readonly t LastTriggerUSec = ...;
        # readonly t LastTriggerUSecMonotonic = ...;
        # NextElapseUSecRealtime contains the next elapsation point on the CLOCK_REALTIME clock in miscroseconds since the epoch, or 0 if this timer event does not include at least one calendar event.

        # Similarly, NextElapseUSecMonotonic contains the next elapsation point on the CLOCK_MONOTONIC clock in microseconds since the epoch, or 0 if this timer event does not include at least one monotonic event.

        # https://github.com/systemd/systemd/blob/e0270bab43a4c37028ee32ae853037df22999767/src/systemctl/systemctl-list-units.c#L668-L671'
        # TABLE_TIMESTAMP, t->next_elapse,
        # TABLE_TIMESTAMP_LEFT, t->next_elapse,
        # TABLE_TIMESTAMP, t->last_trigger.realtime,
        # TABLE_TIMESTAMP_RELATIVE_MONOTONIC, t->last_trigger.monotonic,


        # https://github.com/systemd/systemd/blob/e0270bab43a4c37028ee32ae853037df22999767/src/core/dbus-timer.c#L111
        # SD_BUS_PROPERTY("NextElapseUSecRealtime", "t", bus_property_get_usec, offsetof(Timer, next_elapse_realtime), SD_BUS_VTABLE_PROPERTY_EMITS_CHANGE),
        # SD_BUS_PROPERTY("NextElapseUSecMonotonic", "t", property_get_next_elapse_monotonic, 0, SD_BUS_VTABLE_PROPERTY_EMITS_CHANGE),
        # BUS_PROPERTY_DUAL_TIMESTAMP("LastTriggerUSec", offsetof(Timer, last_trigger), SD_BUS_VTABLE_PROPERTY_EMITS_CHANGE),
        """

        name: str
        last: Optional[int]
        """Timestamp"""

        next: Optional[int]
        """Timestamp"""

    class NameFilter:
        """This class stores all system unit names (e. g. ``nginx.service`` or
        ``fstrim.timer``) and provides a interface to filter the names by regular
        expressions."""

        __unit_names: set[str]

        def __init__(self, unit_names: Sequence[str] = ()) -> None:
            self.__unit_names = set(unit_names)

        def __iter__(self) -> Generator[str, None, None]:
            for name in sorted(self.__unit_names):
                yield name

        @staticmethod
        def match(unit_name: str, regexes: str | Sequence[str]) -> bool:
            """
            Match multiple regular expressions against a unit name.

            :param unit_name: The unit name to be matched.

            :param regexes: A single regular expression (``include='.*service'``) or a
                list of regular expressions (``include=('.*service', '.*mount')``).

            :return: True if one regular expression matches"""
            if isinstance(regexes, str):
                regexes = [regexes]
            for regex in regexes:
                try:
                    if re.match(regex, unit_name):
                        return True
                except Exception:
                    raise CheckSystemdRegexpError(
                        "Invalid regular expression: '{}'".format(regex)
                    )
            return False

        def add(self, unit_name: str) -> None:
            """Add one unit name.

            :param unit_name: The name of the unit, for example ``apt.timer``.
            """
            self.__unit_names.add(unit_name)

        def get(self) -> set[str]:
            """Get all stored unit names."""
            return self.__unit_names

        def filter(
            self,
            include: str | Sequence[str] | None = None,
            exclude: str | Sequence[str] | None = None,
        ) -> Generator[str, None, None]:
            """
            List all unit names or apply filters (``include`` or ``exclude``) to
            the list of unit names.

            :param include: If the unit name matches the provided regular
                expression, it is included in the list of unit names. A single
                regular expression (``include='.*service'``) or a list of regular
                expressions (``include=('.*service', '.*mount')``).

            :param exclude: If the unit name matches the provided regular
                expression, it is excluded from the list of unit names. A single
                regular expression (``exclude='.*service'``) or a list of regular
                expressions (``exclude=('.*service', '.*mount')``).
            """
            match = Source.NameFilter.match
            for name in sorted(self.__unit_names):
                output: Optional[str] = name
                if include and not match(name, include):
                    output = None

                if output and exclude and match(name, exclude):
                    output = None

                if output:
                    yield output

    class Cache(Generic[T]):
        """This class is a container class for systemd units."""

        __units: dict[str, T]

        __name_filter: Source.NameFilter

        def __init__(self) -> None:
            self.__units = {}
            self.__name_filter = Source.NameFilter()

        def __iter__(self) -> Generator[T, None, None]:
            for name in self.__name_filter:
                yield self.__units[name]

        def add(self, name: str, unit: T) -> None:
            self.__units[name] = unit
            self.__name_filter.add(name)

        def get(self, name: Optional[str] = None) -> T | None:
            if name:
                return self.__units[name]
            return None

        def filter(
            self,
            include: str | Sequence[str] | None = None,
            exclude: str | Sequence[str] | None = None,
        ) -> Generator[T, None, None]:
            """
            List all units or apply filters (``include`` or ``exclude``) to
            the list of unit.

            :param include: If the unit name matches the provided regular
                expression, it is included in the list of unit names. A single
                regular expression (``include='.*service'``) or a list of regular
                expressions (``include=('.*service', '.*mount')``).

            :param exclude: If the unit name matches the provided regular
                expression, it is excluded from the list of unit names. A single
                regular expression (``exclude='.*service'``) or a list of regular
                expressions (``exclude=('.*service', '.*mount')``).
            """
            for name in self.__name_filter.filter(include=include, exclude=exclude):
                yield self.__units[name]

        @property
        def count(self) -> int:
            return len(self.__units)

        def count_by_states(
            self,
            states: Sequence[str],
            include: str | Sequence[str] | None = None,
            exclude: str | Sequence[str] | None = None,
        ) -> dict[str, int]:
            states_normalized: list[dict[str, str]] = []
            counter: dict[str, int] = {}
            for state_spec in states:
                # state_proerty:state_value
                # for example: active_state:failed
                state_property = state_spec.split(":")[0]
                state_value = state_spec.split(":")[1]
                state: dict[str, str] = {
                    "property": state_property,
                    "value": state_value,
                    "spec": state_spec,
                }
                states_normalized.append(state)
                counter[state_spec] = 0

            for unit in self.filter(include=include, exclude=exclude):
                for state in states_normalized:
                    if getattr(unit, state["property"]) == state["value"]:
                        counter[state["spec"]] += 1

            return counter

    _user: bool = False

    def _round_1(
        self,
        value: float,
    ) -> float:
        return round(value, 1)

    def _usec_to_sec(
        self,
        usec: int,
    ) -> int:
        return int(usec / 1_000_000)

    @staticmethod
    def get_interface_name_from_unit_name(unit_name: str) -> str:
        """
        :param name: for example apt-daily.service

        :return: org.freedesktop.systemd1.Service
        """
        name_segments = unit_name.split(".")
        interface_name = name_segments[-1]
        return "org.freedesktop.systemd1.{}".format(interface_name.title())

    @staticmethod
    def get_interface_name_from_object_path(object_path: str) -> str:
        """
        :param object_path: for example
            ``/org/freedesktop/systemd1/unit/apt_2ddaily_2eservice``

        :return: org.freedesktop.systemd1.Service
        """
        name_segments = object_path.split("_2e")
        interface_name = name_segments[-1]
        return "org.freedesktop.systemd1.{}".format(interface_name.title())

    @staticmethod
    def is_unit_type(unit_name_or_object_path: str, type_name: UnitType) -> bool:
        return (
            re.match(".*(\\.|_2e)" + type_name + "$", unit_name_or_object_path)
            is not None
        )

    def set_user(self, user: bool) -> None:
        self._user = user

    @abstractmethod
    def get_unit(self, name: str) -> Source.Unit: ...

    @property
    @abstractmethod
    def _all_units(self) -> Generator[Source.Unit, Any, None]: ...

    @property
    def units(self) -> Source.Cache[Source.Unit]:
        cache: Source.Cache[Source.Unit] = Source.Cache()
        for unit in self._all_units:
            cache.add(unit.name, unit)
        return cache

    @property
    @abstractmethod
    def startup_time(self) -> float | None: ...

    @property
    @abstractmethod
    def _all_timers(self) -> list[Source.Timer]: ...

    @property
    def timers(self) -> Source.Cache[Source.Timer]:
        cache: Source.Cache[Source.Timer] = Source.Cache()
        for timer in self._all_timers:
            cache.add(timer.name, timer)
        return cache


class CliSource(Source):
    class Table:
        """This class reads the text tables that some systemd commands like
        ``systemctl list-units`` or ``systemctl list-timers`` produce."""

        header_row: str
        body_rows: list[str]
        column_lengths: list[int]
        columns: list[str]

        def __init__(self, stdout: str) -> None:
            """
            :param stdout: The standard output of certain systemd command line
            utilities.
            :param expected_column_headers: The expected column headers
            (for example ``('UNIT', 'LOAD', 'ACTIVE')``)
            """
            rows: list[str] = stdout.splitlines()
            self.header_row = CliSource.Table.__normalize_header(rows[0])
            self.column_lengths = CliSource.Table.__detect_lengths(self.header_row)
            self.columns = CliSource.Table.__split_row(
                self.header_row, self.column_lengths
            )
            counter = 0
            for line in rows:
                # The table footer is separted by a blank line
                if line == "":
                    break
                counter += 1
            self.body_rows = rows[1:counter]

        @staticmethod
        def __normalize_header(header_row: str) -> str:
            """Normalize the header row

            :param header_row: The first line of a systemd table output.
            """
            return header_row.lower()

        @staticmethod
        def __detect_lengths(header_row: str) -> list[int]:
            """
            :param header_row: The first line of a systemd table output.

            :return: A list of column lengths in number of characters.
            """
            column_lengths: list[int] = []
            match = re.search(r"^ +", header_row)
            if match:
                whitespace_prefix_length = match.end()
                column_lengths.append(whitespace_prefix_length)
                header_row = header_row[whitespace_prefix_length:]

            word = 0
            space = 0

            for char in header_row:
                if word and space >= 1 and char != " ":
                    column_lengths.append(word + space)
                    word = 0
                    space = 0

                if char == " ":
                    space += 1
                else:
                    word += 1

            return column_lengths

        @staticmethod
        def __split_row(line: str, column_lengths: list[int]) -> list[str]:
            columns: list[str] = []
            right = 0
            for length in column_lengths:
                left = right
                right = right + length
                columns.append(line[left:right].strip())
            columns.append(line[right:].strip())
            return columns

        @property
        def row_count(self) -> int:
            """The number of rows. Only the body rows are counted. The header row
            is not taken into account."""
            return len(self.body_rows)

        def check_header(self, column_header: Sequence[str]) -> None:
            """Check if the specified column names are present in the header row of
            the text table. Raise an exception if not.

            :param column_headers: The expected column headers
              (for example ``('UNIT', 'LOAD', 'ACTIVE')``)
            """
            for column_name in column_header:
                if self.header_row.find(column_name.lower()) == -1:
                    msg = (
                        "The column heading '{}' couldn’t found in the "
                        "table header. Possibly the table layout of systemctl "
                        "has changed."
                    )
                    raise ValueError(msg.format(column_name))

        def get_row(self, row_number: int) -> dict[str, str]:
            """Retrieve a table row as a dictionary. The keys are taken from the
            header row. The first row number is 0.

            :param row_number: The index number of the table row starting at 0.

            """
            body_columns = CliSource.Table.__split_row(
                self.body_rows[row_number], self.column_lengths
            )

            result: dict[str, str] = {}

            index = 0
            for column in self.columns:
                if column == "":
                    key = "column_{}".format(index)
                else:
                    key = column
                result[key] = body_columns[index]
                index += 1
            return result

        def list_rows(self) -> Generator[dict[str, str], None, None]:
            """List all rows."""
            for i in range(0, self.row_count):
                yield self.get_row(i)

    @staticmethod
    def __execute_cli(args: str | Sequence[str]) -> str | None:
        """Execute a command on the command line (cli = command line interface))
        and capture the stdout. This is a wrapper around ``subprocess.Popen``.

        :param args: A list of programm arguments.

        :raises nagiosplugin.CheckError: If the command produces some stderr output
        or if an OSError exception occurs.

        :return: The stdout of the command.
        """
        try:
            p = subprocess.Popen(
                args,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )
            stdout, stderr = p.communicate()
            logger.debug("Execute command on the command line: %s", " ".join(args))
        except OSError as e:
            raise CheckError(e)

        if p.returncode != 0:
            raise CheckError(
                "The command exits with a none-zero return code ({})".format(
                    p.returncode
                )
            )

        if stderr:
            raise CheckError(stderr)

        if stdout:
            result = stdout.decode("utf-8")
            logger.verbose("stdout:\n%s", result)
            return result
        return None

    @staticmethod
    def __convert_to_sec(fmt_timespan: str) -> float:
        """Convert a timespan format string to seconds. Take a look at the
        systemd `time-util.c
        <https://github.com/systemd/systemd/blob/master/src/basic/time-util.c>`_
        source code.

        :param fmt_timespan: for example ``2.345s`` or ``3min 45.234s`` or
        ``34min left`` or ``2 months 8 days``

        :return: The seconds
        """
        for replacement in [
            ["years", "y"],
            ["months", "month"],
            ["weeks", "w"],
            ["days", "d"],
        ]:
            fmt_timespan = fmt_timespan.replace(" " + replacement[0], replacement[1])
        seconds = {
            "y": 31536000,  # 365 * 24 * 60 * 60
            "month": 2592000,  # 30 * 24 * 60 * 60
            "w": 604800,  # 7 * 24 * 60 * 60
            "d": 86400,  # 24 * 60 * 60
            "h": 3600,  # 60 * 60
            "min": 60,
            "s": 1,
            "ms": 0.001,
        }
        result: float = 0
        for span in fmt_timespan.split():
            match = re.search(r"([\d\.]+)([a-z]+)", span)
            if match:
                value = match.group(1)
                unit = match.group(2)
                result += float(value) * seconds[unit]
        return round(float(result), 3)

    @staticmethod
    def __convert_to_timestamp(date_format: str) -> int:
        return int(
            datetime.strptime(date_format, "%a %Y-%m-%d %H:%M:%S %Z").timestamp()
        )

    def get_unit(self, name: str) -> Source.Unit:
        stdout = CliSource.__execute_cli(
            [
                "systemctl",
                "show",
                "--property",
                "Id",
                "--property",
                "ActiveState",
                "--property",
                "SubState",
                "--property",
                "LoadState",
                name,
            ]
        )
        if stdout is None:
            raise CheckSystemdError(f"The unit '{name}' couldn't be found.")
        rows = stdout.splitlines()

        properties: dict[str, str] = {}
        for row in rows:
            index_equal_sign = row.index("=")
            properties[row[:index_equal_sign]] = row[index_equal_sign + 1 :]

        logger.debug("Properties of unit '%s': %s", name, properties)

        return Source.Unit(
            name=properties["Id"],
            active_state=properties["ActiveState"],
            sub_state=properties["SubState"],
            load_state=properties["LoadState"],
        )

    @property
    def _all_units(self) -> Generator[Source.Unit, None, None]:
        command = ["systemctl", "list-units", "--all"]
        if self._user:
            command += ["--user"]
        stdout = CliSource.__execute_cli(command)
        if stdout:
            table_parser = self.Table(stdout)
            table_parser.check_header(("unit", "active", "sub", "load"))
            for row in table_parser.list_rows():
                yield self.Unit(
                    name=row["unit"],
                    active_state=row["active"],
                    sub_state=row["sub"],
                    load_state=row["load"],
                )

    @property
    def startup_time(self) -> float | None:
        stdout = None
        try:
            stdout = CliSource.__execute_cli(["systemd-analyze"])
        except CheckError:
            pass

        if stdout:
            # First line:
            # Startup finished in 1.672s (kernel) + 21.378s (userspace) =
            # 23.050s

            # On raspian no second line
            # Second line:
            # graphical.target reached after 1min 2.154s in userspace
            match = re.search(r"reached after (.+) in userspace", stdout)

            if not match:
                match = re.search(r" = (.+)\n", stdout)

            # Output when boot process is not finished:
            # Bootup is not yet finished. Please try again later.
            if match:
                return self._round_1(CliSource.__convert_to_sec(match.group(1)))
        return None

    @property
    def _all_timers(self) -> list[Source.Timer]:
        """https://github.com/systemd/systemd/blob/e0270bab43a4c37028ee32ae853037df22999767/src/systemctl/systemctl-list-units.c#L641-L689"""
        stdout = CliSource.__execute_cli(["systemctl", "list-timers", "--all"])

        # NEXT                          LEFT
        # Sat 2020-05-16 15:11:15 CEST  34min left

        # LAST                          PASSED
        # Sat 2020-05-16 14:31:56 CEST  4min 20s ago

        # UNIT             ACTIVATES
        # apt-daily.timer  apt-daily.service
        timers: list[Source.Timer] = []
        if stdout:
            table_parser = CliSource.Table(stdout)
            table_parser.check_header(("unit", "left", "passed"))

            for row in table_parser.list_rows():
                name = row["unit"]

                next: Optional[int] = None
                last: Optional[int] = None

                def convert(value: str) -> int:
                    return int(CliSource.__convert_to_sec(value))

                if row["left"] != "n/a":
                    next = convert(row["left"])
                if row["passed"] != "n/a":
                    last = convert(row["passed"])

                timers.append(Source.Timer(name=name, next=next, last=last))
        return timers


class GiSource(CliSource):
    """
    Data source via D-Bus using the ``gi`` (GObject introspection) package.

    TODO Intherit from DataSource if the full Dbus Api is implemented

    This class holds the main entry point object of the D-Bus systemd API. See
    the section `The Manager Object
    <https://www.freedesktop.org/software/systemd/man/org.freedesktop.systemd1.html#The%20Manager%20Object>`_
    in the systemd D-Bus API.
    """

    class UnitTuple(NamedTuple):
        name: str
        """The primary unit name as string, for example ``dbus.service``"""

        description: str
        """The human readable description string, for example ``D-Bus System Message Bus``"""

        load_state: LoadState
        """The load state (i.e. whether the unit file has been loaded successfully), for example ``loaded``"""

        active_state: ActiveState
        """The active state (i.e. whether the unit is currently started or not), for example ``active``"""

        sub_state: SubState
        """The sub state (a more fine-grained version of the active state that is specific to the unit type, which the active state is not), for example ``running``"""

        followed_by: str
        """A unit that is being followed in its state by this unit, if there is any, otherwise the empty string, for example ``''``"""

        unit_object_path: str
        """The unit object path, for example ``/org/freedesktop/systemd1/unit/dbus_2eservice``"""

        job_id: str
        """If there is a job queued for the job unit, the numeric job id, 0 otherwise, for example ``0``"""

        job_type: str
        """The job type as string, for example ``''``"""

        job_object_path: str
        """The job object path, for example ``/``"""

    class Proxy:
        _object_path: str
        _interface_name: str
        _user: bool = False
        __proxy: Optional[DBusProxy] = None

        def __init__(
            self, object_path: str, interface_name: str, user: bool = False
        ) -> None:
            self._object_path = object_path
            self._interface_name = interface_name
            self._user = user

        @property
        def _bus_type(self) -> BusType:
            if not BusType is not None:
                raise Exception("The package PyGObject (gi) is not available.")
            return BusType.SESSION if self._user else BusType.SYSTEM

        @property
        def _proxy(self) -> DBusProxy:
            if self.__proxy is None:
                if DBusProxy is None or DBusProxyFlags is None:
                    raise Exception("The package PyGObject (gi) is not available.")
                self.__proxy = DBusProxy.new_for_bus_sync(
                    self._bus_type,
                    DBusProxyFlags.NONE,
                    None,
                    "org.freedesktop.systemd1",
                    self._object_path,
                    self._interface_name,
                    None,
                )
            return self.__proxy

        def get(self, name: str) -> Any:
            variant = self._proxy.get_cached_property(name)
            if variant is not None:
                value = variant.unpack()
                logger.verbose(
                    "Get property '%s' from object path %s of interface %s: %s",
                    name,
                    self._object_path,
                    self._interface_name,
                    value,
                )
                return value

        @property
        def object_path(self) -> str:
            return self._object_path

        @property
        def interface_name(self) -> str:
            return self._interface_name

    class ManagerProxy(Proxy):
        def __init__(self, user: bool = False) -> None:
            super().__init__(
                "/org/freedesktop/systemd1", "org.freedesktop.systemd1.Manager", user
            )

        @property
        def default_target(self) -> str:
            return self._proxy.GetDefaultTarget()  # type: ignore

        @property
        def userspace_timestamp_monotonic(self) -> int:
            return self.get("UserspaceTimestampMonotonic")

        def get_object_path(self, name: str) -> str:
            return self._proxy.GetUnit("(s)", name)  # type: ignore
            # return self._proxy.call_sync('GetUnit', Variant('(s)', name), DBusCallFlags.NONE, -1, None)

        @property
        def units(self) -> list[GiSource.UnitTuple]:
            return self._proxy.ListUnits()  # type: ignore

    class UnitProxy(Proxy):
        def __init__(
            self,
            name: Optional[str] = None,
            object_path: Optional[str] = None,
            user: bool = False,
        ) -> None:
            if not object_path and name:
                object_path = GiSource.get_manager(user).get_object_path(name)
            if not object_path:
                raise ValueError("Either name or object_path must be set.")
            super().__init__(object_path, "org.freedesktop.systemd1.Unit", user)

        @property
        def active_state(self) -> str:
            return self.get("ActiveState")

        @property
        def sub_state(self) -> str:
            return self.get("SubState")

        @property
        def load_state(self) -> str:
            return self.get("LoadState")

        @property
        def active_enter_timestamp_monotonic(self) -> int:
            return self.get("ActiveEnterTimestampMonotonic")

    class TimerProxy(UnitProxy):
        __timer_proxy: Optional[GiSource.Proxy] = None

        @property
        def _timer_proxy(self) -> GiSource.Proxy:
            if not self.__timer_proxy:
                self.__timer_proxy = GiSource.Proxy(
                    self._object_path, "org.freedesktop.systemd1.Timer", self._user
                )
            return self.__timer_proxy

        @property
        def last(self) -> int:
            """Timestamp in microseconds"""
            return self._timer_proxy.get("LastTriggerUSecMonotonic")

        @property
        def next(self) -> int:
            """Timestamp in microseconds"""
            return self._timer_proxy.get("NextElapseUSecMonotonic")

    __system_manager: Optional[ManagerProxy] = None
    __user_manager: Optional[ManagerProxy] = None

    @classmethod
    def get_manager(cls, user: bool = False) -> ManagerProxy:
        if user:
            if not cls.__user_manager:
                cls.__user_manager = cls.ManagerProxy(user)
            return cls.__user_manager
        else:
            if not cls.__system_manager:
                cls.__system_manager = cls.ManagerProxy(user)
            return cls.__system_manager

    @property
    def manager(self) -> ManagerProxy:
        return self.get_manager(self._user)

    @property
    def _all_units(self) -> Generator[Source.Unit, None, None]:
        for (
            name,
            _,
            load_state,
            active_state,
            sub_state,
            _,
            _,
            _,
            _,
            _,
        ) in self.manager.units:
            yield self.Unit(
                name=name,
                active_state=active_state,
                sub_state=sub_state,
                load_state=load_state,
            )

    @property
    def startup_time(self) -> float | None:
        """`src/analyze/analyze-time-data.c <https://github.com/systemd/systemd/blob/1f901c24530fb9b111126381a6ea101af8040e65/src/analyze/analyze-time-data.c#L141-L197>`"""
        unit = GiSource.UnitProxy(self.manager.default_target)
        # ... ActiveEnterTimestamp,
        # ActiveEnterTimestampMonotonic ... contain
        # CLOCK_REALTIME and CLOCK_MONOTONIC 64-bit microsecond timestamps of
        # the last time a unit left the inactive state, entered the active
        # state, .... The fields are 0 in case
        # such a transition has not yet been recorded on this boot.

        enter_timestamp = unit.active_enter_timestamp_monotonic
        if not enter_timestamp:
            return None
        return self._round_1(
            (enter_timestamp - self.manager.userspace_timestamp_monotonic) / 1_000_000
        )

    @property
    def _all_timers(self) -> list[Source.Timer]:
        timers: list[Source.Timer] = []
        for (
            name,
            _,
            _,
            _,
            _,
            _,
            unit_object_path,
            _,
            _,
            _,
        ) in self.manager.units:
            if name.endswith(".timer"):
                timer = GiSource.TimerProxy(object_path=unit_object_path)

                def _to_timestamp(usec: int) -> Optional[int]:
                    result: Optional[int] = None
                    if timer.last > 0:
                        result = self._usec_to_sec(usec)
                    return result

                timers.append(
                    Source.Timer(
                        name=name,
                        next=_to_timestamp(timer.next),
                        last=_to_timestamp(timer.last),
                    )
                )
        return timers


class OptionContainer:
    """This class has the same attributes as the ``Namespace`` instance
    returned by the ``argparse`` package."""

    verbose: int
    debug: int

    # scope: units
    ignore_inactive_state: bool
    include: list[str] = []
    include_unit: Optional[str]
    include_type: list[str]
    exclude: list[str] = []
    exclude_unit: list[str]
    exclude_type: list[str]
    expected_state: str | None

    # scope: timers
    scope_timers: bool
    timers_warning: int

    timers_critical: int

    # scope: startup_time
    scope_startup_time: bool
    warning: int
    """``-w``, ``--warning``"""

    critical: int
    """``-c``, ``--critical``"""

    # backend
    data_source: Optional[Literal["dbus", "cli"]]

    user: bool = False
    """``--user``"""

    # performance_data
    performance_data: bool

    def __init__(self) -> None:
        self.include = []
        self.exclude = []
        self.unit = None
        self.data_source = None


opts = OptionContainer()
"""
We make is variable global to be able to access the command line arguments
everywhere in the plugin. In this variable the result of `parse_args()
<https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.parse_args>`_
is stored. It is an instance of the
`argparse.Namespace
<https://docs.python.org/3/library/argparse.html#argparse.Namespace>`_ class.
This variable is initialized in the main function. The variable is
intentionally not named ``args`` to avoid confusion with ``*args`` (Non-Keyword
Arguments).
"""


# Unit abstraction ############################################################


class CheckSystemdError(Exception):
    """Base class for exceptions in this module. All exceptions are caught by
    the decorator ``@nagiosplugin.guarded()`` on the main function and printed
    out nicely."""

    pass


class CheckSystemdRegexpError(CheckSystemdError):
    """Raised when an invalid regular expression is specified."""

    pass


class SystemdUnitTypesList(MutableSequence[str]):
    unit_types: list[str]

    def __init__(self, *args: str) -> None:
        self.unit_types = list()
        self.__all_types = (
            "service",
            "socket",
            "target",
            "device",
            "mount",
            "automount",
            "timer",
            "swap",
            "path",
            "slice",
            "scope",
        )
        self.extend(list(args))

    def __len__(self) -> int:
        return len(self.unit_types)

    def __getitem__(self, index: int | slice) -> Any:
        if isinstance(index, int):
            return self.unit_types[index]

    def __delitem__(self, index: int | slice) -> None:
        del self.unit_types[index]

    @overload
    def __setitem__(self, index: int, unit_type: str) -> None: ...

    @overload
    def __setitem__(self, index: slice, unit_type: Iterable[str]) -> None: ...

    def __setitem__(self, index: int | slice, unit_type: str | Iterable[str]) -> None:
        if isinstance(index, int) and isinstance(unit_type, str):
            self.__check_type(unit_type)
            self.unit_types[index] = unit_type

    def __str__(self) -> str:
        return str(self.unit_types)

    def insert(self, index: int, value: str) -> None:
        self.__check_type(value)
        self.unit_types.insert(index, value)

    def __check_type(self, type: str) -> None:
        if type not in self.__all_types:
            raise ValueError(
                "The given type '{}' is not a valid systemd " "unit type.".format(type)
            )

    def convert_to_regexp(self):
        return r".*\.({})$".format("|".join(self.unit_types))


Units = Source.Cache[Source.Unit]

# scope: units ################################################################


class UnitsResource(Resource):
    units: Units

    def __init__(self, units: Units) -> None:
        self.units = units

    def probe(self) -> Generator[Metric, None, None]:
        counter = 0
        for unit in self.units.filter(include=opts.include, exclude=opts.exclude):
            yield Metric(name=unit.name, value=unit, context="units")
            counter += 1

        if counter == 0:
            raise ValueError(
                "Please verify your --include-* and --exclude-* "
                "options. No units have been added for "
                "testing."
            )


class UnitsContext(Context):
    def __init__(self) -> None:
        super().__init__("units")

    def evaluate(self, metric: Metric, resource: Resource) -> Result:
        """Determines state of a given metric.

        :param metric: associated metric that is to be evaluated
        :param resource: resource that produced the associated metric
            (may optionally be consulted)

        :returns: :class:`~.result.Result`
        """
        if isinstance(metric.value, Source.Unit):
            unit = metric.value
            exitcode = unit.convert_to_exitcode()
            if exitcode != 0:
                hint = "{}: {}".format(metric.name, unit.active_state)
                return self.result_cls(exitcode, metric=metric, hint=hint)

        if metric.value:
            hint = "{}: {}".format(metric.name, metric.value)
        else:
            hint = metric.name

        # The option -u is not specifed
        if not metric.value:
            return self.result_cls(Ok, metric=metric, hint=hint)

        if opts.ignore_inactive_state and metric.value == "failed":
            return self.result_cls(Critical, metric=metric, hint=hint)
        elif not opts.ignore_inactive_state and metric.value != "active":
            return self.result_cls(Critical, metric=metric, hint=hint)
        else:
            return self.result_cls(Ok, metric=metric, hint=hint)


# scope: timers ###############################################################


class TimersResource(Resource):
    """
    Resource that calls ``systemctl list-timers --all`` on the command line to
    get informations about dead / inactive timers. There is one type of systemd
    “degradation” which is normally not detected: dead / inactive timers.

    :param list excludes: A list of systemd unit names to exclude from the
      checks.
    """

    source: Source

    name = "SYSTEMD"

    def __init__(self, source: Source) -> None:
        self.source = source

    def probe(self) -> Generator[Metric, None, None]:
        for timer in self.source.timers.filter(exclude=opts.exclude):
            state = Ok
            if timer.next is None:
                if timer.last is None:
                    state = Critical
                elif timer.last >= opts.timers_critical:
                    state = Critical
                elif timer.last >= opts.timers_warning:
                    state = Warn
            yield Metric(name=timer.name, value=state, context="timers")


class TimersContext(Context):
    def __init__(self) -> None:
        super().__init__("timers")

    def evaluate(self, metric: Metric, resource: Resource):
        """Determines state of a given metric.

        :param metric: associated metric that is to be evaluated
        :param resource: resource that produced the associated metric
            (may optionally be consulted)

        :returns: :class:`~.result.Result`
        """
        return self.result_cls(metric.value, metric=metric, hint=metric.name)


# scope: startup_time #########################################################


class StartupTimeResource(Resource):
    """Resource that calls ``systemd-analyze`` on the command line to get
    informations about the startup time.

    `src/analyze/analyze-time-data.c <https://github.com/systemd/systemd/blob/1f901c24530fb9b111126381a6ea101af8040e65/src/analyze/analyze-time-data.c#L141-L197>`_
    """

    __source: Source

    def __init__(self, source: Source) -> None:
        self.__source = source

    def probe(self) -> Generator[Metric, None, None]:
        startup_time = self.__source.startup_time
        if startup_time:
            yield Metric(
                name="startup_time",
                value=startup_time,
                context="startup_time",
            )


class StartupTimeContext(ScalarContext):
    def __init__(self) -> None:
        super().__init__("startup_time")
        if opts.scope_startup_time:
            self.warning = Range(opts.warning)
            self.critical = Range(opts.critical)

    def performance(self, metric: Metric, resource: Resource) -> Performance | None:
        if not opts.performance_data:
            return None
        return Performance(
            metric.name,
            metric.value,
            metric.uom,
            self.warning,
            self.critical,
            metric.min,
            metric.max,
        )


# scope: performance_data #####################################################


class PerformanceDataResource(Resource):
    units: Units

    def __init__(self, units: Units) -> None:
        self.units = units

    def probe(self) -> Generator[Metric, None, None]:
        for state_spec, count in self.units.count_by_states(
            (
                "active_state:failed",
                "active_state:active",
                "active_state:activating",
                "active_state:inactive",
            ),
            exclude=opts.exclude,
        ).items():
            yield Metric(
                name="units_{}".format(state_spec.split(":")[1]),
                value=count,
                context="performance_data",
            )

        yield Metric(
            name="count_units", value=self.units.count, context="performance_data"
        )


class PerformanceDataContext(Context):
    def __init__(self) -> None:
        super().__init__("performance_data")

    def performance(self, metric: Metric, resource: Resource) -> Performance:
        """Derives performance data from a given metric.

        :param metric: associated metric from which performance data are
            derived
        :param resource: resource that produced the associated metric
            (may optionally be consulted)

        :returns: :class:`Perfdata` object
        """
        return Performance(label=metric.name, value=metric.value)


# Presentation: *Summary ######################################################


class SystemdSummary(Summary):
    """Format the different status lines. A subclass of `nagiosplugin.Summary
    <https://github.com/mpounsett/nagiosplugin/blob/master/nagiosplugin/summary.py>`_.
    """

    def ok(self, results: Results) -> str:
        """Formats status line when overall state is ok.

        :param results: :class:`~nagiosplugin.result.Results` container
        :returns: status line
        """
        if opts.include_unit:
            for result in results.most_significant:
                if isinstance(result.context, UnitsContext):
                    return "{0}".format(result)
        return "all"

    def problem(self, results: Results) -> str:
        """Formats status line when overall state is not ok.

        :param results: :class:`~.result.Results` container

        :returns: status line
        """
        summary: list[Result] = []
        for result in results.most_significant:
            if result.context and result.context.name in [
                "startup_time",
                "units",
                "timers",
            ]:
                summary.append(result)
        return ", ".join(["{0}".format(result) for result in summary])

    def verbose(self, results: Results) -> list[str]:
        """Provides extra lines if verbose plugin execution is requested.

        :param results: :class:`~.result.Results` container

        :returns: list of strings
        """
        summary: list[str] = []
        for result in results.most_significant:
            if result.context and result.context.name in [
                "startup_time",
                "units",
                "timers",
            ]:
                summary.append("{0}: {1}".format(result.state, result))
        return summary


# Command line interface (argparse) ###########################################


def convert_to_regexp_list(
    regexp: Optional[Sequence[str]] = None,
    unit_names: Optional[Union[str, Sequence[str]]] = None,
    unit_types: Optional[Sequence[str]] = None,
) -> set[str]:
    result: set[str] = set()
    if regexp:
        for regexp in regexp:
            result.add(regexp)

    if unit_names:
        if isinstance(unit_names, str):
            unit_names = [unit_names]
        for unit_name in unit_names:
            result.add(unit_name.replace(".", "\\."))

    if unit_types:
        types = SystemdUnitTypesList(*unit_types)
        result.add(types.convert_to_regexp())

    return result


def get_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="check_systemd",  # To get the right command name in the README.
        formatter_class=lambda prog: argparse.RawDescriptionHelpFormatter(
            prog, width=80
        ),  # noqa: E501
        description="Copyright (c) 2014-18 Andrea Briganti "
        "<kbytesys@gmail.com>\n"  # noqa: E251
        "Copyright (c) 2019-24 Josef Friedrich <josef@friedrich.rocks>\n"
        "\n"
        "Nagios / Icinga monitoring plugin to check systemd.\n",  # noqa: E501
        epilog="Performance data:\n"  # noqa: E251
        "  - count_units\n"
        "  - startup_time\n"
        "  - units_activating\n"
        "  - units_active\n"
        "  - units_failed\n"
        "  - units_inactive\n",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase output verbosity (use up to 3 times).",
    )

    parser.add_argument(
        "-d",
        "--debug",
        action="count",
        default=0,
        help="Increase debug verbosity (use up to 2 times): -d: info -dd: debug.",
    )

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version="%(prog)s {}".format(__version__),
    )

    # Scope: units ############################################################

    units = parser.add_argument_group(
        "Options related to unit selection",
        "By default all systemd units are checked. "
        "Use the option '-e' to exclude units\nby a regular expression. "
        "Use the option '-u' to check only one unit.",
    )

    units.add_argument(
        "-i",
        "--ignore-inactive-state",
        action="store_true",
        help="Ignore an inactive state on a specific unit. Oneshot services "
        "for example are only active while running and not enabled. "
        "The rest of the time they are inactive. This option has only "
        "an affect if it is used with the option -u.",
    )

    units.add_argument(
        "-I",
        "--include",
        metavar="REGEXP",
        action="append",
        default=[],
        help="Include systemd units to the checks. This option can be "
        "applied multiple times, for example: -I mnt-data.mount -I "
        "task.service. Regular expressions can be used to include "
        "multiple units at once, for example: "
        "-i 'user@\\d+\\.service'. "
        "For more informations see the Python documentation about "
        "regular expressions "
        "(https://docs.python.org/3/library/re.html).",
    )

    units.add_argument(
        "-u",
        "--unit",
        "--include-unit",
        type=str,
        metavar="UNIT_NAME",
        dest="include_unit",
        help="Name of the systemd unit that is being tested.",
    )

    units.add_argument(
        "--include-type",
        metavar="UNIT_TYPE",
        nargs="+",
        help="One or more unit types (for example: 'service', 'timer')",
    )

    units.add_argument(
        "-e",
        "--exclude",
        metavar="REGEXP",
        action="append",
        default=[],
        help="Exclude a systemd unit from the checks. This option can be "
        "applied multiple times, for example: -e mnt-data.mount -e "
        "task.service. Regular expressions can be used to exclude "
        "multiple units at once, for example: "
        "-e 'user@\\d+\\.service'. "
        "For more informations see the Python documentation about "
        "regular expressions "
        "(https://docs.python.org/3/library/re.html).",
    )

    units.add_argument(
        "--exclude-unit",
        metavar="UNIT_NAME",
        nargs="+",
        help="Name of the systemd unit that is being tested.",
    )

    units.add_argument(
        "--exclude-type",
        metavar="UNIT_TYPE",
        action="append",
        help="One or more unit types (for example: 'service', 'timer')",
    )

    units.add_argument(
        "--state",
        "--required",
        "--expected-state",
        choices=get_args(ActiveState),
        dest="expected_state",
        help="Specify the active state that the systemd unit must have "
        "(for example: active, inactive)",
    )

    # Scope: timers ###########################################################

    timers = parser.add_argument_group("Timers related options")

    timers.add_argument(
        "-t",
        "--timers",
        "--dead-timers",
        dest="scope_timers",
        action="store_true",
        help="Detect dead / inactive timers. See the corresponding options "
        "'-W, --dead-timer-warning' and "
        "'-C, --dead-timers-critical'. "
        "Dead timers are detected by parsing the output of "
        "'systemctl list-timers'. "
        "Dead timer rows displaying 'n/a' in the NEXT and LEFT "
        "columns and the time span in the column PASSED exceeds the "
        "values specified with the options '-W, --dead-timer-warning' "
        "and '-C, --dead-timers-critical'.",
    )

    timers.add_argument(
        "-W",
        "--timers-warning",
        "--dead-timers-warning",
        dest="timers_warning",
        metavar="SECONDS",
        type=float,
        default=60 * 60 * 24 * 6,
        help="Time ago in seconds for dead / inactive timers to trigger a "
        "warning state (by default 6 days).",
    )

    timers.add_argument(
        "-C",
        "--timers-critical",
        "--dead-timers-critical",
        dest="timers_critical",
        metavar="SECONDS",
        type=float,
        default=60 * 60 * 24 * 7,
        help="Time ago in seconds for dead / inactive timers to trigger a "
        "critical state (by default 7 days).",
    )

    # Scope: startup_time #####################################################

    startup_time = parser.add_argument_group("Startup time related options")

    startup_time.add_argument(
        "-n",
        "--no-startup-time",
        dest="scope_startup_time",
        action="store_false",
        default=True,
        help="Don’t check the startup time. Using this option the options "
        "'-w, --warning' and '-c, --critical' have no effect. "
        "Performance data about the startup time is collected, but "
        "no critical, warning etc. states are triggered.",
    )

    startup_time.add_argument(
        "-w",
        "--warning",
        default=60,
        type=int,
        metavar="SECONDS",
        help="Startup time in seconds to result in a warning status. The"
        " default is 60 seconds.",
    )

    startup_time.add_argument(
        "-c",
        "--critical",
        default=120,
        type=int,
        metavar="SECONDS",
        help="Startup time in seconds to result in a critical status. The"
        " default is 120 seconds.",
    )

    # Backend #################################################################

    acquisition = parser.add_argument_group("Monitoring data acquisition")
    acquisition_exclusive_group = acquisition.add_mutually_exclusive_group()

    acquisition_exclusive_group.add_argument(
        "--dbus",
        dest="data_source",
        action="store_const",
        const="dbus",
        default="cli",
        help="Use the systemd’s D-Bus API instead of parsing the text output "
        "of various systemd related command line interfaces to monitor "
        "systemd. At the moment the D-Bus backend of this plugin is "
        "only partially implemented.",
    )

    acquisition_exclusive_group.add_argument(
        "--cli",
        dest="data_source",
        action="store_const",
        const="cli",
        help="Use the text output of serveral systemd command line interface "
        "(cli) binaries to gather the required data for the monitoring "
        "process.",
    )

    acquisition.add_argument(
        "--user",
        dest="user",
        action="store_true",
        default=False,
        help="Also show user (systemctl --user) units.",
    )

    # Performance data ########################################################

    perf_data = parser.add_argument_group(
        "Performance data", "By default performance data is attached."
    )
    perf_data_exclusive_group = perf_data.add_mutually_exclusive_group()

    perf_data_exclusive_group.add_argument(
        "-P",
        "--performance-data",
        dest="performance_data",
        action="store_true",
        default=True,
        help="Attach performance data to the plugin output.",
    )

    perf_data_exclusive_group.add_argument(
        "-p",
        "--no-performance-data",
        dest="performance_data",
        action="store_false",
        help="Attach no performance data to the plugin output.",
    )

    return parser


def normalize_argparser(opts: argparse.Namespace) -> OptionContainer:
    if opts.data_source == "dbus" and not is_dbus:
        opts.data_source = "cli"

    opts.include = convert_to_regexp_list(
        regexp=opts.include, unit_names=opts.include_unit, unit_types=opts.include_type
    )

    opts.exclude = convert_to_regexp_list(
        regexp=opts.exclude, unit_names=opts.exclude_unit, unit_types=opts.exclude_type
    )

    o = cast(OptionContainer, opts)

    # del opts.include_unit
    del o.include_type
    del o.exclude_type
    del o.exclude_unit

    return o


@nagiosplugin.guarded(verbose=0)  # type: ignore
def main() -> None:
    """The main entry point of the monitoring plugin. First the command line
    arguments are read into the variable ``opts``. The configuration of this
    ``opts`` object decides which instances of the `Resource
    <https://github.com/mpounsett/nagiosplugin/blob/master/nagiosplugin/resource.py>`_,
    `Context
    <https://github.com/mpounsett/nagiosplugin/blob/master/nagiosplugin/context.py>`_
    and `Summary
    <https://github.com/mpounsett/nagiosplugin/blob/master/nagiosplugin/summary.py>`_
    subclasses are assembled in a list called ``tasks``. This list is passed
    the main class of the ``nagiosplugin`` library: the `Check
    <https://nagiosplugin.readthedocs.io/en/stable/api/core.html#nagiosplugin-check>`_
    class.
    """
    global opts
    opts = normalize_argparser(get_argparser().parse_args())

    logger.set_level(opts.debug)
    logger.show_levels()
    logger.verbose("Normalized argparse options: %s", opts)
    logger.verbose("is_dbus: %s", is_dbus)

    source: Source
    if opts.data_source == "dbus":
        source = GiSource()
    else:
        source = CliSource()
    source.set_user(opts.user)
    units = source.units

    if opts.include_unit is not None:
        unit = source.get_unit(opts.include_unit)
        units.add(unit.name, unit)

    tasks: list[Union[Resource, Context, Summary]] = [
        UnitsResource(units),
        UnitsContext(),
        SystemdSummary(),
        StartupTimeResource(source),
        StartupTimeContext(),
    ]

    if opts.scope_timers:
        tasks += [
            TimersResource(source),
            TimersContext(),
        ]

    if opts.performance_data:
        tasks += [
            PerformanceDataResource(units),
            PerformanceDataContext(),
        ]

    check = Check(*tasks)
    check.name = "systemd"
    check.main(opts.verbose)


if __name__ == "__main__":
    main()  # type: ignore
