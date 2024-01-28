# -*- coding: utf-8 -*-
"""The GMDM CLI tool for managing dependencies of GameMaker projects and files.
"""
__version__ = "0.2.6"

import argparse
import logging
import sys

from gmdm.app import get_app
# Variables
from gmdm.utils.logging import get_logger


def windows_enable_ansi(std_id):  # pylint: disable=R0914
    """Enable Windows 10 cmd.exe ANSI VT Virtual Terminal Processing."""
    from ctypes import (POINTER, WINFUNCTYPE, byref,  # pylint: disable=C0415
                        windll)
    from ctypes.wintypes import BOOL, DWORD, HANDLE  # pylint: disable=C0415

    GetStdHandle = WINFUNCTYPE(  # pylint: disable=C0103
        HANDLE,
        DWORD)(('GetStdHandle', windll.kernel32))

    GetFileType = WINFUNCTYPE(  # pylint: disable=C0103
        DWORD,
        HANDLE)(('GetFileType', windll.kernel32))

    GetConsoleMode = WINFUNCTYPE(  # pylint: disable=C0103
        BOOL,
        HANDLE,
        POINTER(DWORD))(('GetConsoleMode', windll.kernel32))

    SetConsoleMode = WINFUNCTYPE(  # pylint: disable=C0103
        BOOL,
        HANDLE,
        DWORD)(('SetConsoleMode', windll.kernel32))

    if std_id == 1:       # stdout
        h = GetStdHandle(-11)
    elif std_id == 2:     # stderr
        h = GetStdHandle(-12)
    else:
        return False

    if h is None or h == HANDLE(-1):
        return False

    FILE_TYPE_CHAR = 0x0002  # pylint: disable=C0103
    if (GetFileType(h) & 3) != FILE_TYPE_CHAR:
        return False

    mode = DWORD()
    if not GetConsoleMode(h, byref(mode)):
        return False

    ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004  # pylint: disable=C0103
    if (mode.value & ENABLE_VIRTUAL_TERMINAL_PROCESSING) == 0:
        SetConsoleMode(h, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING)
    return True


if sys.platform == "win32":
    windows_enable_ansi(0)  # Windows 10 VirtualTerminal Ansi on Stdout
    windows_enable_ansi(1)  # Windows 10 VirtualTerminal Ansi on Stderr

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


def cli(command="help", **kwargs):
    """The main entry call for the package.

    Args:
        command (str, optional): Command to execute. Defaults to "help".

    Returns:
        int: Exit code
    """
    parser = kwargs["parser"]
    args = kwargs["args"]
    logger = kwargs["logger"]

    # Check for special positional argument values in place of "file"
    if command == "help":
        sys.exit(parser.print_help(None))
    else:
        gmdm = get_app(logger)
        sys.exit(gmdm.run(args))


def main():
    "Main program"
    parser = argparse.ArgumentParser(prog='gmdm',
                                          usage='%(prog)s [options] command',
                                          description=__doc__,
                                          formatter_class=argparse.RawTextHelpFormatter
                                     )

    parser.add_argument('--version', action="version",
                        version="GMDM v" + __version__)

    parser.add_argument('command',
                        help='Command to do with GMDM',
                        choices=["help", "sync", "test",],
                        default="help",
                        )

    parser.add_argument('-Q',
                        '--quiet',
                        action='store_true',
                        dest='quiet',
                        default=False,
                        help='run quietly without any output')

    parser.add_argument('-nc',
                        '--no-colors',
                        action='store_true',
                        dest="nocolors",
                        default=False,
                        help='set output to be without ANSI colors')

    parser.add_argument('--fake',
                        action='store_true',
                        dest="fake",
                        default=False,
                        help='run without actually doing the command.')

    parser.add_argument('-V',
                        '--verbosity',
                        action='store',
                        metavar='NOTSET|ERROR|INFO|DEBUG|VERBOSE',
                        dest='verbosity',
                        type=str,
                        choices=["NOTSET", "WARNING",
                                 "INFO", "DEBUG", "ERROR", "CRITICAL"],
                        default="INFO",
                        help='Verbosity of output messages (default is INFO)')

    args = parser.parse_args()

    quiet = args.quiet

    verbosity = args.verbosity.upper()
    if quiet:
        verbosity = "NONE"

    verbosity = logging.WARNING if verbosity == "WARNING" else \
        logging.INFO if verbosity == "INFO" else \
        logging.DEBUG if verbosity == "DEBUG" else \
        logging.ERROR if verbosity == "ERROR" else \
        logging.CRITICAL if verbosity == "CRITICAL" else \
        logging.NOTSET if verbosity in ("NOTSET", "NONE",) else \
        logging.INFO

    command = args.command
    nocolors = args.nocolors

    logger = get_logger(verbosity, False if nocolors else None)

    kwargs = {
        "parser": parser,
        "args": args,
        "logger": logger,
    }

    cli(command, **kwargs)


if __name__ == "__main__":
    main()
