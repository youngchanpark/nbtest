import os
import re
import sys

from . import __version__ as testmynb__version__
from ._ansi import green, red, orange, strip_ansi


class TestHandler:
    def __init__(self, *notebooks):
        self.notebooks = notebooks

    @property
    def _summary(self):
        notebook_count = len(self.notebooks)
        test_count = sum([len(nb.extract_codes()) for nb in self.notebooks])
        py_ver = re.sub(r"\s.*", "", sys.version)
        header = self._h1_message("Test My Notebook ({})".format(testmynb__version__))
        return "{}".format(header) + "\n".join(
            [
                "Platform {}".format(sys.platform),
                "Python {}".format(py_ver),
                "Working Directory: {}".format(os.getcwd()),
                "",
                "{0} test cells across {1} notebook(s) detected.".format(
                    test_count, notebook_count
                ),
                "",
            ]
        )

    @staticmethod
    def _h1_message(message):

        col = int(os.popen('stty size', 'r').read().split()[1])

        no_formats = strip_ansi(message)
        # Remove the ANSI escape codes to check the message length
        num_equals = (col - len(no_formats) - 3) // 2
        equals_sign = num_equals * "="

        return "{1} {0} {1}\n".format(message, equals_sign)

    @property
    def _notebook_summary_section(self):
        section = ["Notebooks:\n"]
        for nb in self.notebooks:
            trust = green("Trusted") if nb.trusted else red("Untrusted")
            string = "{} {}: {}\n".format(trust, nb.name, nb.result)
            section.append(string)
        section.append("\n")
        return "".join(section)

    def __call__(self):
        failed_or_error = False
        output_message = list()

        for nb in self.notebooks:
            nb()

        output_message.append(self._summary)
        output_message.append(self._notebook_summary_section)

        errors = self.collect_errors()
        fails = self.collect_fails()

        if fails:
            failed_or_error = True
            head_message = red(self._h1_message("Failed Test(s)"))
            output_message.append(head_message)
            for cell, err in fails.items():
                string = "---- {}: {} ----\n".format(cell.notebook, cell.name)
                output_message.append(string)
                output_message.append(str(cell))
                output_message.append(
                    red("\n-----------------------------------------\n")
                )
                output_message.append(err)
                output_message.append("\n\n")

        if errors:
            failed_or_error = True
            head_message = orange(self._h1_message("Errored Test(s)"))
            output_message.append(head_message)
            for cell, err in errors.items():
                string = "---- {}: {} ----\n".format(cell.notebook, cell.name)
                output_message.append(string)
                output_message.append(str(cell))
                output_message.append(
                    red("\n-----------------------------------------\n")
                )
                output_message.append(err)
                output_message.append("\n\n")

        output_message.append(self._final_remarks)

        output_message = "".join(output_message)
        print(output_message)
        if failed_or_error:
            sys.exit(1)

    @property
    def _final_remarks(self):
        all_tests = "".join([nb.result for nb in self.notebooks])

        passed_test_count = all_tests.count(".")
        failed_test_count = all_tests.count("F")
        errored_test_count = all_tests.count("E")

        passed_text = green("{} test(s) passed".format(passed_test_count))
        failed_text = red("{} failed".format(failed_test_count))
        error_text = orange(" and {} raised an error".format(errored_test_count))
        return self._h1_message(
            "{}, {},{}".format(passed_text, failed_text, error_text)
        )

    def collect_errors(self):
        errors = dict()
        for nb in self.notebooks:
            errors.update(nb.get_error_stack())

        return errors

    def collect_fails(self):
        fails = dict()
        for nb in self.notebooks:
            fails.update(nb.get_fail_stack())

        return fails


def find_notebooks(*args):
    notebooks = list()
    if len(args):
        for path in args:
            if os.path.isfile(path):
                notebooks.append(path)
            elif os.path.isdir(path):
                notebooks.extend(_recursive_find_notebooks(path))
    else:
        notebooks = _recursive_find_notebooks(os.getcwd())
    return notebooks


def _recursive_find_notebooks(path):
    notebooks = list()
    for root, dirs, files in os.walk(path):
        for file in files:
            if ".ipynb_checkpoints" in root:
                continue
            if re.match(r"^test_.+\.ipynb", file):
                notebooks.append(os.path.join(root, file))

    return notebooks
