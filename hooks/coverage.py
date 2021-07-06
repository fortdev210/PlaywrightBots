import sys
import utils


class CoverageChecker(object):
    COVERAGE_FILE = '.stlpro.coverage'

    def __init__(self, options, files):
        self.options = options
        self.files = files
        self.files_coverage = {}
        self.has_files_not_coverage = False

    def _run_coverage_report_html(self):
        command = "$VIRTUAL_ENV/bin/coverage html"
        utils.run_process(command)

    def _run_coverage_report(self):
        command = "$VIRTUAL_ENV/bin/coverage report"
        out, _ = utils.run_process(command)
        return out

    def _parse_coverage_report(self, content):
        lines = content.splitlines()

        for line in lines[1:-1]:
            file_name = line.split()[0]
            self.files_coverage[file_name] = line

        try:
            self.coverage_number = int(
                lines[-1].split()[-1][:-1].decode('utf-8')
            )
        except:
            self.coverage_number = 0

    def _get_last_coverage_number(self):
        try:
            with open(self.COVERAGE_FILE) as f:
                self.last_coverage_number = int(f.readlines()[0])
        except:
            self.last_coverage_number = 0

    def _save_coverage_number(self):
        with open(self.COVERAGE_FILE, 'w') as f:
            f.write(str(self.coverage_number))

    def _print_coverage_for_files(self):
        for file_path in self.files:
            file_without_extension = file_path[:file_path.rindex('.')]

            if file_without_extension in self.files_coverage:
                line = self.files_coverage[file_without_extension]
                coverage_number = int(line.split()[-1][:-1])
                if coverage_number < 100:
                    self.has_files_not_coverage = True
                    print("%s\t%s%s" % (utils.RED, line, utils.RESET))
                else:
                    print("%s\t%s%s" % (utils.GREEN, line, utils.RESET))

    def _print_increase_coverage(self):
        print("---------------------------------------------------------------")  # NOQA
        if self.coverage_number > self.last_coverage_number:
            print("%sIncrease coverage from %s to %s%s" % (
                utils.GREEN, self.last_coverage_number,
                self.coverage_number, utils.RESET))
        elif self.coverage_number < self.last_coverage_number:
            print("%sDecrease coverage from %s to %s%s" % (
                utils.RED, self.last_coverage_number,
                self.coverage_number, utils.RESET))
        else:
            print("%sCoverage stay at %s%s" % (
                utils.GREEN, self.coverage_number, utils.RESET))

    def _prompt_user(self):
        if self.has_files_not_coverage:
            sys.stdin = open('/dev/tty', 'r')
            var = input("You have some files were not coverage. Do you still want to commit? [yes] ")  # NOQA
            if var != "yes":
                sys.exit(1)

    def _remove_coverage_dot_file(self):
        command = "rm -f .coverage"
        utils.run_process_asynchronous(command)

    def execute(self):
        self._get_last_coverage_number()

        out = self._run_coverage_report()
        self._run_coverage_report_html()
        self._parse_coverage_report(out)
        self._print_coverage_for_files()
        self._print_increase_coverage()
        self._save_coverage_number()
        self._prompt_user()
        self._remove_coverage_dot_file()


def check_coverage(options, files):
    CoverageChecker(options, files).execute()
