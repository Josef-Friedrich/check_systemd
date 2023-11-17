import subprocess
import typing

import utils


def execute_cli(args: typing.Union[str, typing.Iterator[str]]) -> str:
    """Execute a command on the command line (cli = command line interface))
    and capture the stdout. This is a wrapper around ``subprocess.Popen``.

    :param args: A list of programm arguments.

    :return: The stdout of the command.
    """
    try:
        p = subprocess.Popen(
            args, stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=subprocess.PIPE
        )
        stdout, stderr = p.communicate()
    except OSError as e:
        raise Exception(e)

    if p.returncode != 0:
        return
        # raise Exception('The command exits with a none-zero'
        #                 'return code ({})'.format(p.returncode))

    if stderr:
        raise Exception(stderr)

    if stdout:
        stdout = stdout.decode("utf-8")
        return stdout


def collect_all_units():
    stdout = execute_cli(["systemctl", "list-units", "--all", "--no-legend"])

    rows = stdout.splitlines()

    units = []
    for row in rows:
        row = row.strip()
        units.append(row[: row.index(" ")])

    return units


def collect_properties(unit_name: str) -> dict:
    stdout = execute_cli(["systemctl", "show", unit_name])
    if stdout is None:
        return
    rows = stdout.splitlines()

    properties = {}
    for row in rows:
        index_equal_sign = row.index("=")
        properties[row[:index_equal_sign]] = row[index_equal_sign + 1 :]

    return properties


def list_units(unit_type=None, properties=None):
    units = collect_all_units()
    for unit_name in units:
        if unit_type and not utils.is_unit_type(unit_name, unit_type):
            continue
        print(unit_name)

        result = collect_properties(unit_name)
        if result is not None:
            utils.print_properties(result, properties)
