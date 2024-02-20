from __future__ import annotations

import io
import os
import typing
from contextlib import redirect_stderr, redirect_stdout
from os import path
from unittest import TestCase, mock
from unittest.mock import Mock

import check_systemd

test: TestCase = TestCase()
test.maxDiff = None


class AddBin(object):
    """
    :param string bin_path: Path relative to the test folder.
    """

    bin_path: str

    old_path: str

    def __init__(self, bin_path: str) -> None:
        self.bin_path = bin_path
        self.old_path = os.environ["PATH"]

    def __enter__(self) -> None:
        BIN = os.path.abspath(os.path.join(os.path.dirname(__file__), self.bin_path))
        os.environ["PATH"] = BIN + ":" + os.environ["PATH"]

    def __exit__(self) -> None:
        os.environ["PATH"] = self.old_path


def get_cli_output_path(file_name: str) -> str:
    return path.join(path.dirname(path.abspath(__file__)), "cli_output", file_name)


def convert_to_bytes(file_name_or_str: str) -> bytes:
    """Read a text file as bytes or convert a string into bytes.

    :param file_name_or_str: The name of a text file which is placed in the
      folder ``cli_output`` or a string that is converted to bytes.

    :return: The text in byte format.
    """
    output_path = get_cli_output_path(file_name_or_str)
    if os.path.exists(output_path):
        in_file = open(output_path, "rb")
        data = in_file.read()
        in_file.close()
        return data
    else:
        return file_name_or_str.encode()


def MPopen(
    returncode: int = 0, stdout: str | None = None, stderr: str | None = None
) -> Mock:
    """A mocked version of ``subprocess.POpen``."""
    mock = Mock()
    mock.returncode = returncode
    stdout_bytes = None
    if stdout:
        stdout_bytes = convert_to_bytes(stdout)

    stderr_bytes = None
    if stderr:
        stderr_bytes = convert_to_bytes(stderr)
    mock.communicate.return_value = (stdout_bytes, stderr_bytes)
    return mock


def get_mocks_for_popen(*stdout: str) -> list[Mock]:
    """
    Create multiple mock objects which are suitable to mimic multiple calls of
    ``subprocess.Popen()``.

    Assign the result of this function to the attribute ``side_effect``:
    ``Popen.side_effect = result_of_is_function``

    :param stdout: Multiple strings or multiple file names of text files inside
      the folder ``cli_ouput``.

    :return: A list of mock objects for the class ``subprocess.Popen()``.
    """
    mocks: list[Mock] = []
    for out in stdout:
        mocks.append(MPopen(stdout=out))
    return mocks


class MockResult:
    """A class to collect all results of a mocked execution of the main
    function."""

    __sys_exit: Mock
    __stdout: str | None
    __stderr: str | None

    def __init__(self, sys_exit_mock: Mock, stdout: str, stderr: str) -> None:
        self.__sys_exit = sys_exit_mock
        self.__stdout = stdout
        self.__stderr = stderr

    @property
    def stdout(self) -> str | None:
        """The function ``redirect_stdout()`` is used to capture the ``stdout``
        output."""
        if self.__stdout:
            return self.__stdout
        return None

    @property
    def stderr(self) -> str | None:
        """The function ``redirect_stderr()`` is used to capture the ``stderr``
        output."""
        if self.__stderr:
            return self.__stderr
        return None

    @property
    def output(self) -> str:
        """A combined string of the captured stdout, stderr and the print
        calls. Somehow the whole stdout couldn’t be read. The help text could
        be read, but not the plugin output using the function
        ``redirect_stdout()``."""
        out: str = ""

        if self.__stdout:
            out += self.__stdout

        if self.__stderr:
            out += self.__stderr

        return out

    @property
    def exitcode(self) -> int:
        """The captured exit code"""
        return int(self.__sys_exit.call_args[0][0])

    def assert_exitcode(self, exitcode: int) -> None:
        assert self.exitcode == exitcode

    def assert_ok(self) -> None:
        self.assert_exitcode(0)

    def assert_warn(self) -> None:
        self.assert_exitcode(1)

    def assert_critical(self) -> None:
        self.assert_exitcode(2)

    def assert_unknown(self) -> None:
        self.assert_exitcode(3)

    @property
    def first_line(self) -> str | None:
        """The first line of the stdout output without a newline break at the
        end as a string.
        """
        if self.output:
            return self.output.split("\n", 1)[0]
        return None

    def assert_first_line(self, first_line: str) -> None:
        assert self.first_line == first_line


def execute_main(
    argv: list[str] = ["check_systemd.py"],
    stdout: list[str] = [
        "systemctl-list-units_ok.txt",
        "systemd-analyze_12.345.txt",
    ],
    popen: typing.Iterable[Mock] | None = None,
) -> MockResult:
    """Execute the main function with a lot of patched functions and classes.

    :param argv: A list of command line arguments, e. g.
        ``argv=['-u', 'nginx.service']``

    :param stdout: A list of file names of files in the directory
        ``test/cli_output``. You have to specify as many text files as there
        are calls of the function ``subprocess.Popen``:

        * Line 334
          ``p = subprocess.Popen(['systemctl', 'list-units', '--all']``,
          ``SystemctlListUnitsResource``
        * Line 460
          ``p = subprocess.Popen(['systemd-analyze']``,
          ``SystemdAnalyseResource``
        * Line 576
          ``p = subprocess.Popen(['systemctl', 'list-timers', '--all']``,
          ``SystemctlListTimersResource``
        * Line 656
          ``p = subprocess.Popen(['systemctl', 'is-active', self.unit]``,
          ``SystemctlIsActiveResource``

    :param popen: Some mocked Popen classes.

    :param int analyze_returncode: The first call `systemctl analyze` to check
        if the startup process is finished

    :return: The results are assembled in the class ``MockResult``
    """
    if not argv or argv[0] != "check_systemd.py":
        argv.insert(0, "check_systemd.py")
    with mock.patch("sys.exit") as sys_exit, mock.patch(
        "check_systemd.subprocess.Popen"
    ) as Popen, mock.patch("sys.argv", argv):
        if popen:
            Popen.side_effect = popen
        else:
            Popen.side_effect = get_mocks_for_popen(*stdout)

        file_stdout: io.StringIO = io.StringIO()
        file_stderr: io.StringIO = io.StringIO()
        with redirect_stdout(file_stdout), redirect_stderr(file_stderr):
            check_systemd.main()

    return MockResult(
        sys_exit_mock=sys_exit,
        stdout=file_stdout.getvalue(),
        stderr=file_stderr.getvalue(),
    )


class Expected:
    startup_time = "startup_time=12.345;60;120"
    """``startup_time=12.345;60;120``"""


def debug(msg):
    file_object = open("debug.txt", "a")
    file_object.write("\n---\n")

    file_object.write(msg)
    file_object.close()
