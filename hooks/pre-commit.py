#!/usr/bin/env python

import sys

import utils
# import hook_test
# import coverage
from checker import StepChecker


CHECKS = [
    {
        'output': 'Checking for pdbs...',
        'command': 'grep -n "import pdb" %s',
        'ignore_files': ['.*pre-commit'],
        'print_filename': True,
        'is_mandatory': True,
    },
    {
        'output': 'Running flake8...',
        'command': 'flake8 %s',
        'match_files': ['.*\.py$'],
        'ignore_files': [
            '.*settings/.*', '.*manage.py', '.*migrations.*', '.*wsgi\.py*'
        ],
        'print_filename': False,
        'is_mandatory': True,
    },
    # {
    #     'output': 'Running unit tests...',
    #     'function': hook_test.run_test,
    #     'ignore_files': [
    #         '.*settings/.*', '.*manage.py', '.*migrations.*', '^mws/*',
    #         '^templates/*'
    #     ],
    #     'print_filename': False,
    #     'is_mandatory': True,
    # },
    # {
    #     'output': 'Check coverage...',
    #     'function': coverage.check_coverage,
    #     'ignore_files': [
    #         '.*settings/.*', '.*manage.py', '.*migrations.*', '^mws/*',
    #         '^tests/*', '^templates/*', '^hooks/*'
    #     ],
    #     'print_filename': False,
    #     'is_mandatory': True,
    # }
]


def main():
    utils.check_virtual_env()
    commit_files = utils.get_list_commit_files()
    changed_files = utils.get_changed_files()
    uncommit_files = set(changed_files) - set(commit_files)
    stage_files = utils.get_stage_files()
    if uncommit_files or stage_files:
        utils.ask_user_to_add_all_files_to_commit(uncommit_files)

    commit_files = utils.get_list_commit_files()
    if not commit_files:
        print("There is no file to commit. What do you want me to check?!!")
        sys.exit(0)
    else:
        for check_options in CHECKS:
            step = StepChecker(check_options)
            step.check(commit_files)
            print("========================================================================")  # NOQA


if __name__ == '__main__':
    main()
