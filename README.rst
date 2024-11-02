.. image:: http://img.shields.io/pypi/v/check-systemd.svg
    :target: https://pypi.org/project/check-systemd
    :alt: This package on the Python Package Index

.. image:: https://github.com/Josef-Friedrich/check_systemd/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/Josef-Friedrich/check_systemd/actions/workflows/tests.yml
    :alt: Tests

.. image:: https://readthedocs.org/projects/check-systemd/badge/?version=latest
    :target: https://check-systemd.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

check_systemd
=============

``check_systemd`` is a `Nagios <https://www.nagios.org>`__ /
`Icinga <https://icinga.com>`__ monitoring plugin to check
`systemd <https://systemd.io>`__. This Python script will report a
degraded system to your monitoring solution. It can also be used to
monitor individual systemd services (with the ``-u, --unit`` parameter)
and timers units (with the ``-t, --dead-timers`` parameter). The only
dependency the plugin needs is the Python library
`nagiosplugin <https://nagiosplugin.readthedocs.io/en/stable>`__.

Installation
------------

::

   pip install check_systemd

Packages
--------

``check_systemd`` on `repology.org <https://repology.org/project/check-systemd/related>`__.

-  archlinux
   (`package <https://aur.archlinux.org/packages/check_systemd>`__,
   `source
   code <https://aur.archlinux.org/check_systemd.git>`__):
   ``yaourt -S check_systemd``
-  Ubuntu
   (`package <https://packages.ubuntu.com/search?keywords=monitoring-plugins-systemd&searchon=names>`__,
   `source
   code <https://git.launchpad.net/ubuntu/+source/monitoring-plugins-systemd>`__):
   ``apt install monitoring-plugins-systemd``
-  Debian
   (`package <https://packages.debian.org/search?keywords=monitoring-plugins-systemd>`__,
   `source
   code <https://salsa.debian.org/python-team/packages/monitoring-plugins-systemd/-/tree/debian/master/debian>`__):
   ``apt install monitoring-plugins-systemd``
-  NixOS
   (`package <https://search.nixos.org/packages?channel=unstable&query=check_systemd>`__,
   `source
   code <https://github.com/NixOS/nixpkgs/blob/nixos-unstable/pkgs/servers/monitoring/nagios/plugins/check_systemd.nix>`__):
   ``nix-env -iA nixos.check_systemd``
-  Fedora
   (`package <https://packages.fedoraproject.org/pkgs/nagios-plugins-systemd/nagios-plugins-systemd/>`__,
   `source code <https://src.fedoraproject.org/rpms/nagios-plugins-systemd>`__):
   ``dnf install nagios-plugins-systemd``
-  OracleLinux9 / RHEL9
   (`package <https://gitlab.com/msfgitlab/check_systemd_build_rpm/-/jobs/artifacts/main/raw/output/check_systemd-1.0-1.x86_64.rpm?job=release_rpm>`__,
   `source code <https://gitlab.com/msfgitlab/check_systemd_build_rpm>`__,
   `binary <https://gitlab.com/msfgitlab/check_systemd_build_rpm/-/jobs/artifacts/main/raw/output/check_systemd?job=release_rpm>`__):
   This package includes one single binary compiled with the Python compiler Nuitka, including all dependencies.
   The package is built via GitLab CI as a nightly release and is considered experimental.
   ``curl -L -o check_systemd-1.0-1.x86_64.rpm "https://gitlab.com/msfgitlab/check_systemd_build_rpm/-/jobs/artifacts/main/raw/output/check_systemd-1.0-1.x86_64.rpm?job=release_rpm" && sudo dnf install -y ./check_systemd-1.0-1.x86_64.rpm``

Command line interface
----------------------

:: 

    usage: check_systemd [-h] [-v] [-d] [-V] [-i] [-I REGEXP] [-u UNIT_NAME]
                         [--include-type UNIT_TYPE [UNIT_TYPE ...]] [-e REGEXP]
                         [--exclude-unit UNIT_NAME [UNIT_NAME ...]]
                         [--exclude-type UNIT_TYPE]
                         [--state {active,reloading,inactive,failed,activating,deactivating}]
                         [-t] [-W SECONDS] [-C SECONDS] [-n] [-w SECONDS]
                         [-c SECONDS] [--dbus | --cli] [--user] [-P | -p]

    Copyright (c) 2014-18 Andrea Briganti <kbytesys@gmail.com>
    Copyright (c) 2019-24 Josef Friedrich <josef@friedrich.rocks>

    Nagios / Icinga monitoring plugin to check systemd.

    options:
      -h, --help            show this help message and exit
      -v, --verbose         Increase output verbosity (use up to 3 times).
      -d, --debug           Increase debug verbosity (use up to 2 times): -d: info
                            -dd: debug.
      -V, --version         show program's version number and exit

    Options related to unit selection:
      By default all systemd units are checked. Use the option '-e' to exclude units
      by a regular expression. Use the option '-u' to check only one unit.

      -i, --ignore-inactive-state
                            Ignore an inactive state on a specific unit. Oneshot
                            services for example are only active while running and
                            not enabled. The rest of the time they are inactive.
                            This option has only an affect if it is used with the
                            option -u.
      -I REGEXP, --include REGEXP
                            Include systemd units to the checks. This option can be
                            applied multiple times, for example: -I mnt-data.mount
                            -I task.service. Regular expressions can be used to
                            include multiple units at once, for example: -i
                            'user@\d+\.service'. For more informations see the
                            Python documentation about regular expressions
                            (https://docs.python.org/3/library/re.html).
      -u UNIT_NAME, --unit UNIT_NAME, --include-unit UNIT_NAME
                            Name of the systemd unit that is being tested.
      --include-type UNIT_TYPE [UNIT_TYPE ...]
                            One or more unit types (for example: 'service', 'timer')
      -e REGEXP, --exclude REGEXP
                            Exclude a systemd unit from the checks. This option can
                            be applied multiple times, for example: -e mnt-
                            data.mount -e task.service. Regular expressions can be
                            used to exclude multiple units at once, for example: -e
                            'user@\d+\.service'. For more informations see the
                            Python documentation about regular expressions
                            (https://docs.python.org/3/library/re.html).
      --exclude-unit UNIT_NAME [UNIT_NAME ...]
                            Name of the systemd unit that is being tested.
      --exclude-type UNIT_TYPE
                            One or more unit types (for example: 'service', 'timer')
      --state {active,reloading,inactive,failed,activating,deactivating}, --required {active,reloading,inactive,failed,activating,deactivating}, --expected-state {active,reloading,inactive,failed,activating,deactivating}
                            Specify the active state that the systemd unit must have
                            (for example: active, inactive)

    Timers related options:
      -t, --timers, --dead-timers
                            Detect dead / inactive timers. See the corresponding
                            options '-W, --dead-timer-warning' and '-C, --dead-
                            timers-critical'. Dead timers are detected by parsing
                            the output of 'systemctl list-timers'. Dead timer rows
                            displaying 'n/a' in the NEXT and LEFT columns and the
                            time span in the column PASSED exceeds the values
                            specified with the options '-W, --dead-timer-warning'
                            and '-C, --dead-timers-critical'.
      -W SECONDS, --timers-warning SECONDS, --dead-timers-warning SECONDS
                            Time ago in seconds for dead / inactive timers to
                            trigger a warning state (by default 6 days).
      -C SECONDS, --timers-critical SECONDS, --dead-timers-critical SECONDS
                            Time ago in seconds for dead / inactive timers to
                            trigger a critical state (by default 7 days).

    Startup time related options:
      -n, --no-startup-time
                            Don’t check the startup time. Using this option the
                            options '-w, --warning' and '-c, --critical' have no
                            effect. Performance data about the startup time is
                            collected, but no critical, warning etc. states are
                            triggered.
      -w SECONDS, --warning SECONDS
                            Startup time in seconds to result in a warning status.
                            The default is 60 seconds.
      -c SECONDS, --critical SECONDS
                            Startup time in seconds to result in a critical status.
                            The default is 120 seconds.

    Monitoring data acquisition:
      --dbus                Use the systemd’s D-Bus API instead of parsing the text
                            output of various systemd related command line
                            interfaces to monitor systemd. At the moment the D-Bus
                            backend of this plugin is only partially implemented.
      --cli                 Use the text output of serveral systemd command line
                            interface (cli) binaries to gather the required data for
                            the monitoring process.
      --user                Also show user (systemctl --user) units.

    Performance data:
      By default performance data is attached.

      -P, --performance-data
                            Attach performance data to the plugin output.
      -p, --no-performance-data
                            Attach no performance data to the plugin output.

    Performance data:
      - count_units
      - startup_time
      - units_activating
      - units_active
      - units_failed
      - units_inactive

Project pages
-------------

-  on `github.com <https://github.com/Josef-Friedrich/check_systemd>`__
-  on
   `icinga.com <https://exchange.icinga.com/joseffriedrich/check_systemd>`__
-  on
   `nagios.org <https://exchange.nagios.org/directory/Plugins/System-Metrics/Processes/check_systemd/details>`__

Behind the scenes
-----------------

dbus
^^^^

- ``gi``: Python 3 bindings for gobject-introspection libraries
   GObject is an abstraction layer that allows programming with an object
   paradigm that is compatible with many languages. It is a part of Glib,
   the core library used to build GTK+ and GNOME.
   `Website <https://gnome.pages.gitlab.gnome.org/pygobject/index.html>`__
   `Repo <https://gitlab.gnome.org/GNOME/pygobject>`__
   `PyPI (PyGObject) <https://pypi.org/project/PyGObject/>`__
   `Stubs <https://pypi.org/project/PyGObject-stubs/>`__
   `Ubuntu (python3-gi) <https://packages.ubuntu.com/search?keywords=python3-gi>`__
   `Debian (python3-gi) <https://packages.debian.org/search?keywords=python3-gi>`__

- ``dbus``: simple interprocess messaging system (Python 3 interface)
   D-Bus is a message bus, used for sending messages between applications.
   Conceptually, it fits somewhere in between raw sockets and CORBA in
   terms of complexity.
   `Website <https://www.freedesktop.org/wiki/Software/dbus/>`__
   `Repo <https://gitlab.freedesktop.org/dbus/dbus-python>`__
   `PyPI (dbus-python) <https://pypi.org/project/dbus-python/>`__
   `Ubuntu (python3-dbus) <https://packages.ubuntu.com/search?keywords=python3-dbus>`__
   `Debian (python3-dbus) <https://packages.debian.org/search?keywords=python3-dbus>`__

Command line interface (cli) parsing:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To detect failed units this monitoring script runs:

.. code:: sh

   systemctl list-units --all

To get the startup time it executes:

.. code:: sh

   systemd-analyze

To find dead timers this plugin launches:

.. code:: sh

   systemctl list-timers --all

To learn how ``systemd`` produces the text output on the command line,
it is worthwhile to take a look at ``systemd``\ ’s source code. Files
relevant for text output are:
`basic/time-util.c <https://github.com/systemd/systemd/blob/main/src/basic/time-util.c>`__,
`analyze/analyze.c <https://github.com/systemd/systemd/blob/main/src/analyze/analyze.c>`__.

Testing
-------

::

   pyenv install 3.6.12
   pyenv install 3.7.9
   pyenv local 3.6.12 3.7.9
   pip3 install tox
   tox

Test a single test case:

::

   tox -e py38 -- test/test_scope_timers.py:TestScopeTimers.test_all_n_a

Deploying
---------

Edit the version number in check_systemd.py (without ``v``). Use the
``-s`` option to sign the tag (required for the Debian package).

::

   git tag -s v2.0.11
   git push --tags
