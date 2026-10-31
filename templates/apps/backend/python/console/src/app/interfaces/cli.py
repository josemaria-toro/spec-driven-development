"""The command line interface of the application."""

import argparse
import sys
from collections.abc import Sequence
from typing import NoReturn, TextIO

from app.application.greet import greet

SUCCESS = 0
USAGE_ERROR = 2


class _UsageError(Exception):
    """Raised by the parser instead of exiting the process."""


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise _UsageError(message)


def run(arguments: Sequence[str], output: TextIO, errors: TextIO) -> int:
    """Run the application with the given arguments and return the exit code."""
    parser = _Parser(prog="backend", add_help=False)
    parser.add_argument("name", nargs="?", default="")
    try:
        parsed = parser.parse_args(arguments)
    except _UsageError:
        errors.write(parser.format_usage())
        return USAGE_ERROR
    output.write(f"{greet(parsed.name)}\n")
    return SUCCESS


def main() -> None:
    """Entry point of the installed command."""
    raise SystemExit(run(sys.argv[1:], sys.stdout, sys.stderr))
