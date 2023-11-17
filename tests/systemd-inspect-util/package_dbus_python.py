#! /usr/bin/python3

"""
A little script to explore the D-Bus API of systemd using dbus-python.
"""

import dbus
import utils

# https://dbus.freedesktop.org/doc/dbus-python/


unit_name = "apt-daily.timer"

bus = dbus.SystemBus()
systemd = bus.get_object("org.freedesktop.systemd1", "/org/freedesktop/systemd1")

manager = dbus.Interface(systemd, "org.freedesktop.systemd1.Manager")


def collect_properties_of_object(
    result: dict, object_path: str, interface_name="org.freedesktop.systemd1.Unit"
):
    """
    :param object_path: for example
      /org/freedesktop/systemd1/unit/apt_2ddaily_2eservice
    :param interface_name: for example org.freedesktop.systemd1.Service
    """

    proxy = bus.get_object(
        "org.freedesktop.systemd1",
        object_path,
    )

    interface = dbus.Interface(proxy, dbus_interface="org.freedesktop.DBus.Properties")

    # https://dbus.freedesktop.org/doc/dbus-specification.html#standard-interfaces-properties
    properties = interface.GetAll(interface_name)
    for key, value in properties.items():
        result[key] = value


def list_units(unit_type=None, properties=None):
    for name, _, _, _, _, _, object_path, _, _, _ in manager.ListUnits():
        if unit_type and not utils.is_unit_type(name, unit_type):
            continue
        print(name)

        result = {}

        collect_properties_of_object(result, object_path)
        collect_properties_of_object(
            result, object_path, utils.get_interface_name_from_object_path(object_path)
        )

        utils.print_properties(result, properties)
