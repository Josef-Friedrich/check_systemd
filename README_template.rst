{{ badge.pypi }}

{{ badge.github_workflow() }}

{{ badge.readthedocs }}

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

Command line interface
----------------------

{{ cli('check_systemd --help') | literal }}

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
   `Website <https://gnome.pages.gitlab.gnome.org/pygobject/index.html>`_
   `Repo <https://gitlab.gnome.org/GNOME/pygobject>`_
   `PyPI (PyGObject) <https://pypi.org/project/PyGObject/>`_
   `Stubs <https://pypi.org/project/PyGObject-stubs/>`_
   `Ubuntu (python3-gi) <https://packages.ubuntu.com/search?keywords=python3-gi>`_
   `Debian (python3-gi) <https://packages.debian.org/search?keywords=python3-gi>`_

- ``dbus``: simple interprocess messaging system (Python 3 interface)
   D-Bus is a message bus, used for sending messages between applications.
   Conceptually, it fits somewhere in between raw sockets and CORBA in
   terms of complexity.
   `Website <https://www.freedesktop.org/wiki/Software/dbus/>`_
   `Repo <https://gitlab.freedesktop.org/dbus/dbus-python>`_
   `PyPI (dbus-python) <https://pypi.org/project/dbus-python/>`_
   `Ubuntu (python3-dbus) <https://packages.ubuntu.com/search?keywords=python3-dbus>`_
   `Debian (python3-dbus) <https://packages.debian.org/search?keywords=python3-dbus>`_

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
