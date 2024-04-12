"""Run this test in an unmocked environment."""

from __future__ import annotations

from time import sleep

from gi.repository.Gio import BusType, DBusProxy, DBusProxyFlags

# print(proxy.GetAll("(ss)", "org.freedesktop.systemd1.Timer", "NextElapseUSecMonotonic"))  # type: ignore


while True:
    proxy = DBusProxy.new_for_bus_sync(
        BusType.SESSION,
        DBusProxyFlags.DO_NOT_LOAD_PROPERTIES,
        None,
        "org.freedesktop.systemd1",
        "/org/freedesktop/systemd1/unit/example_2dtimer_2etimer",
        "org.freedesktop.DBus.Properties",
        None,
    )
    print(proxy.Get("(ss)", "org.freedesktop.systemd1.Timer", "NextElapseUSecRealtime"))  # type: ignore
    sleep(10)
