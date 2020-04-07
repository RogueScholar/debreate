"""Debreate command line interface

SPDX-License-Identifier: MIT

Copyright (c) 2016-2019 Jordan Irwin <antumdeluge@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Usage: debreate <options> [args] [cmds]

    -h or --help
    Display usage information in the command line.
    -v or --version
    Display Debreate version in the command line & exit
    -l or --log-level
    Sets logging output level. Values can be 'quiet', 'info', 'warn', 'error',
        'debug', or equivalent numeric values of 0-4. Default is 'error' (3).
    -i or --log-interval
    Set the refresh interval, in seconds, for updating the log window.
"""

import argparse
import logging
import os
import sys

from dbr.log import Logger
from startup.tests import available_tests
from startup.tests import test_list

_LOG_LEVEL_STRINGS = ['quiet', 'info', 'warn', 'error', 'debug']
_LOG_LEVEL_INTS = range(0, 5)

_PARSED_ARGS_S = []
_PARSED_ARGS_V = {}

_SOLO_ARGS = (
    ('h', 'help'),
    ('v', 'version'),
)

_VALUE_ARGS = (
    ('l', 'log-level'),
    ('i', 'log-interval'),
)

def _log_level_string_to_int(log_level_string):
    if not log_level_string in _LOG_LEVEL_STRINGS:
        message = 'invalid choice: {0} (choose from {1})'.format(
            log_level_string, _LOG_LEVEL_STRINGS
        )
        raise argparse.ArgumentTypeError(message)

    log_level_int = getattr(logging, log_level_string, logging.ERROR)
    assert isinstance(log_level_int, int)

    return log_level_int

parser = argparse.ArgumentParser(
    prog='debreate',
    description='Create a Debian software package.',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    add_help=False,
    allow_abbrev=False
)

parser.add_argument(
    '-h', '--help',
    action='help',
    help='Print this message and exit.',
    dest='help'
)
parser.add_argument(
    '--version',
    action='version',
    version='%(prog)s 0.7.18',
    dest='version'
)
parser.add_argument(
    '-l', '--log-level',
    nargs=1,
    default=3,
    type=_log_level_string_to_int,
    choices=[(_LOG_LEVEL_STRINGS, _LOG_LEVEL_INTS)],
    help='Set the logging output level. {0}'.format(_LOG_LEVEL_STRINGS),
    dest='log_level'
)
parser.add_argument(
    '-i', '--log-interval',
    nargs=1,
    default=1,
    type=int,
    help='Set the refresh interval, in seconds, for updating the log window.',
    dest='log_interval'
)
parser.add_argument(
    'command',
    default=argparse.SUPPRESS,
    type=str,
    choices=['clean', 'compile', 'legacy', 'test'],
    help='Manually execute a single packaging stage.',
    dest='command'
)
parser.add_argument(
    'path',
    default=os.getcwd(),
    type=str,
    help='Path to package source tree root or .dsc file.',
    dest='path'
)

parsed_args = parser.parse_args()

if parsed_args.log_level != 3:
    Logger.SetLogLevel(parsed_args.log_level)


def arg_is_defined(arg):
    for group in (_SOLO_ARGS, _VALUE_ARGS):
        for SET in group:
            for A in SET:
                if arg == A:
                    return True
            return False


def get_arg_type(arg):
    dashes = 0
    for C in arg:
        if C != '-':
            break

        dashes += 1

    if dashes:
        if dashes == 2 and len(arg.split('=')[0]) > 2:
            if not arg.count('='):
                return 'long'

            if arg.count('=') == 1:
                return 'long-value'

        elif dashes == 1 and len(arg.split('=')[0]) == 2:
            if not arg.count('='):
                return 'short'

            if arg.count('=') == 1:
                return 'short-value'

        return None

    if parsed_args.command:
        return parsed_args.command

    # Any other arguments should be a filename path
    return parsed_args.path


def parse_arguments(arg_list):
    if 'test' in parsed_args.command:
        tests = parsed_args.command('test')

        if not tests:
            print('ERROR: Must supply at least one test')
            sys.exit(64)

        for TEST in tests:
            if TEST not in available_tests:
                print(('ERROR: Unrecognized test: {}'.format(TEST)))
                sys.exit(64)

            test_list.append(TEST)

    argc = len(arg_list)

    for AINDEX in range(argc):
        if AINDEX >= argc:
            break

        A = arg_list[AINDEX]
        arg_type = get_arg_type(A)

        if arg_type is None:
            sys.exit(64)

        clip = 0
        for C in A:
            if C != '-':
                break

            clip += 1

        if arg_type in ('long', 'short'):
            _PARSED_ARGS_S.append(A[clip:])
            continue

        # Anything else should be a value type
        key, value = A.split('=')

        if not value.strip():
            print(('ERROR: Value argument with empty value: {}'.format(key)))
            sys.exit(64)

        key = key[clip:]

        # Use long form
        for S, L in _VALUE_ARGS:
            if key == S:
                key = L
                break

        _PARSED_ARGS_V[key] = value

        # Use long form
        arg_index = _PARSED_ARGS_S.index(A)
        for S, L in _SOLO_ARGS:
            if A == S:
                _PARSED_ARGS_S[arg_index] = L

    for S, L in _SOLO_ARGS:
        s_count = _PARSED_ARGS_S.count(S)
        l_count = _PARSED_ARGS_S.count(L)

        if s_count + l_count > 1:
            print(('ERROR: Duplicate arguments: -{}|--{}'.format(S, L)))
            sys.exit(64)


def found_arg(arg):
    """Checks if an argument was used"""
    for param in parsed_args:
        if param == arg:
            return True
    return False


def found_cmd(cmd):
    """Checks if a command was used"""
    return cmd in parsed_args.command


def getparsed_path():
    return parsed_args.path
