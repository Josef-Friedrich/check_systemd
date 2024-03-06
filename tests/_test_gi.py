"""Run this test in an unmocked environment."""

from __future__ import annotations


from gi.repository.Gio import BusType, DBusProxy, DBusProxyFlags

proxy = DBusProxy.new_for_bus_sync(
    BusType.SESSION,
    DBusProxyFlags.DO_NOT_LOAD_PROPERTIES,
    None,
    "org.freedesktop.systemd1",
    "/org/freedesktop/systemd1/unit/update_2dmotd_2etimer",
    "org.freedesktop.DBus.Properties",
    None,
)


print(proxy.GetAll("(ss)", "org.freedesktop.systemd1.Timer", "NextElapseUSecMonotonic"))  # type: ignore

print(proxy.Get("(ss)", "org.freedesktop.systemd1.Timer", "NextElapseUSecMonotonic"))  # type: ignore
