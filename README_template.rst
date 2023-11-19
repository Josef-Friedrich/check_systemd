{{ badge.pypi }}

{{ badge.github_workflow() }}

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

-  Debian
   (`package <https://packages.debian.org/search?keywords=monitoring%2Dplugins%2Dsystemd>`__,
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
