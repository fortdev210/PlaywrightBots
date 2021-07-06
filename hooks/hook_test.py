import os

import utils


def remove_all_pyc_files():
    command = "find . -name '*.pyc' | xargs rm -rf"
    utils.run_process_asynchronous(command)


def run_test(options, files):
    if files:
        remove_all_pyc_files()
        command = "COVERAGE_PROCESS_START=./.coveragerc \
            $VIRTUAL_ENV/bin/coverage run --parallel-mode \
            --concurrency=multiprocessing --rcfile=./.coveragerc \
            manage.py test tests.unit --failfast --noinput \
            --settings=myproject.tests_settings"
        out = utils.run_process_asynchronous(command)

        run_post_processing()
        return 0 if out.return_code == 0 else 1


def run_post_processing():
    run_coverage_combine()
    run_coverage_html()
    remove_coverage_tmp_files()


def run_coverage_combine():
    command = "$VIRTUAL_ENV/bin/coverage combine --rcfile=./.coveragerc"
    utils.run_process_asynchronous(command)


def run_coverage_html():
    command = "$VIRTUAL_ENV/bin/coverage html -i"
    utils.run_process_asynchronous(command)


def remove_coverage_tmp_files():
    host_name = os.uname()[1]
    command = "find . -name '.coverage.%s.*' | xargs rm -f" % host_name
    utils.run_process_asynchronous(command)
