import sys

import utils


class StepChecker(object):
    def __init__(self, options):
        self.options = options

    def _get_selected_file(self, files):
        if "match_files" in self.options:
            match_files = filter(
                lambda x: utils.matches_file(x, self.options['match_files']),
                files)
        else:
            match_files = files

        if "ignore_files" in self.options:
            ignore_files = filter(
                lambda x: utils.matches_file(x, self.options['ignore_files']),
                files)
        else:
            ignore_files = []

        return set(match_files) - set(ignore_files)

    def _run_command(self, files):
        command = self.options['command']
        result = 0

        for file_name in files:
            out, err = utils.run_process(command % file_name)
            if out or err:
                if self.options['print_filename']:
                    prefix = '\t%s:' % file_name
                else:
                    prefix = '\t'
                output_lines = [
                    '%s%s' % (prefix, line) for line in out.splitlines()]

                print('\n'.join(output_lines))
                if err:
                    print(err)
                result = 1
        return result

    def _run_function(self, files):
        function = self.options['function']
        return function(self.options, files)

    def check(self, files):
        selected_files = self._get_selected_file(files)
        print(self.options['output'])

        if 'command' in self.options:
            result = self._run_command(selected_files)
        elif 'function' in self.options:
            result = self._run_function(selected_files)

        if result and self.options['is_mandatory']:
            sys.exit(1)
