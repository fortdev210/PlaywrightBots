import datetime
import os
import re
import sys
import subprocess
from decimal import Decimal

from fabric.operations import local


MODIFIED_FILE_RE = re.compile(r'^(?:M|A)(\s+)(?P<name>.*)')
RED = '\033[31m'
GREEN = '\033[32m'
RESET = '\033[33m'
_PROTECTED_TYPES = (
    type(None), int, float, Decimal, datetime.datetime, datetime.date,
    datetime.time,
)


def run_process_asynchronous(command):
    return local(command)


def run_process(command):
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, shell=True)
    out, err = process.communicate()
    return out, err


def matches_file(file_name, files):
    return any(re.compile(item).match(file_name) for item in files)


def get_list_commit_files():
    files = []
    out, err = run_process("git status --porcelain")
    for line in out.splitlines():
        line = force_str(line)
        match = MODIFIED_FILE_RE.match(line)
        if not match:
            continue
        files.append(match.group('name'))

    return files


def get_stage_files():
    out, _ = run_process("git diff --name-only")
    return [force_str(file) for file in out.splitlines()]


def get_changed_files():
    out, _ = run_process("git status --short")
    lines = out.splitlines()
    files = [item.strip().split()[-1] for item in lines]
    files = [force_str(file) for file in files]
    return files


def ask_user_to_add_all_files_to_commit(files):
    files = [force_str(file) for file in files]
    sys.stdin = open('/dev/tty', 'r')

    print("List changed file but not to commit")
    print("%s%s%s" % (
        RED, '\n'.join(files), RESET))

    var = input("Do you want to add them to commit? [[no]/yes/quit] ")  # NOQA
    if var == "yes":
        run_process("git add .")
        return True
    if var == "quit":
        sys.exit(1)
    return


def check_virtual_env():
    if 'VIRTUAL_ENV' not in os.environ:
        print("You must run source venv/bin/active first !!!")
        sys.exit(1)


def force_str(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Similar to smart_str(), except that lazy instances are resolved to
    strings, rather than kept as lazy objects.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    # Handle the common case first for performance reasons.
    if issubclass(type(s), str):
        return s
    if strings_only and isinstance(s, _PROTECTED_TYPES):
        return s
    if isinstance(s, bytes):
        s = str(s, encoding, errors)
    else:
        s = str(s)
    return s
