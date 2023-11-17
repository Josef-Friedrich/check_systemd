#! /usr/bin/python3

"""
A little script to explore the D-Bus API of systemd.
"""

import utils

# https://raw.githubusercontent.com/pengutronix/monitoring-check-systemd-service/master/check-systemd-service

try:
    from gi.repository.Gio import BusType, DBusProxy
except ImportError as e:
    print("Please install python3-gi")
    raise e

# https://lazka.github.io/pgi-docs/#Gio-2.0/classes/DBusProxy.html#Gio.DBusProxy

# https://www.freedesktop.org/software/systemd/man/org.freedesktop.systemd1.html

dbus = DBusProxy.new_for_bus_sync(
    BusType.SYSTEM,
    0,
    None,
    "org.freedesktop.systemd1",
    "/org/freedesktop/systemd1",
    "org.freedesktop.systemd1.Manager",
    None,
)


def collect_properties_of_object(
    result: dict, object_path: str, interface_name="org.freedesktop.systemd1.Unit"
):
    """
    :param object_path: for example
      /org/freedesktop/systemd1/unit/apt_2ddaily_2eservice
    :param interface_name: for example org.freedesktop.systemd1.Service
    """

    unit = DBusProxy.new_for_bus_sync(
        BusType.SYSTEM,
        0,
        None,
        "org.freedesktop.systemd1",
        object_path,
        interface_name,
        None,
    )

    for property_name in unit.get_cached_property_names():
        result[property_name] = unit.get_cached_property(property_name).unpack()


def list_units(unit_type=None, properties=None):
    for name, _, _, _, _, _, object_path, _, _, _ in dbus.ListUnits():
        if unit_type and not utils.is_unit_type(name, unit_type):
            continue
        print(name)

        result = {}

        collect_properties_of_object(result, object_path)
        collect_properties_of_object(
            result, object_path, utils.get_interface_name_from_object_path(object_path)
        )

        utils.print_properties(result, properties)
