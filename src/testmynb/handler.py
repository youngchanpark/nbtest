import os
import re
import sys

from . import __version__ as testmynb__version__


def green(text):
    return f"\033[38;5;82m{text}\033[0m"

def red(text):
    return f"\033[38;5;197m{text}\033[0m"

def orange(text):
    return f"\033[38;5;214m{text}\033[0m"

class TestHandler:
    def __init__(self, *notebooks):
        self.notebooks = notebooks


    @property
    def _summary(self):
        notebook_count = len(self.notebooks)
        test_count = sum([len(nb.extract_codes()) for nb in self.notebooks])
        py_ver = re.sub(r'\s.*', '', sys.version)
        header = self._h1_message(f'Test My Notebook ({testmynb__version__})')
        return (
            f'{header}'
            f'Platform {sys.platform}\n'
            f'Python {py_ver}\n'
            f'Working Directory: {os.getcwd()}\n'
            '\n'
            f'{test_count} test cells across {notebook_count} notebook(s) detected.\n'
        )


    @staticmethod
    def _h1_message(message):
        try:
            col, _ = os.get_terminal_size(0)
        except OSError:
            col, _ = os.get_terminal_size(1)

        no_formats = re.sub(r'\x1b\[(\d|;)+m', '', message)
        # Remove the ANSI escape codes to check the message length
        num_equals = (col - len(no_formats) - 3) // 2
        equals_sign = num_equals * '='
        
        return f'{equals_sign} {message} {equals_sign}\n'
    

    @property
    def _notebook_summary_section(self):
        section = ['Notebooks:\n']
        for nb in self.notebooks:
            trust = green("Trusted") if nb.trusted else red('Untrusted')
            section.append(f'{trust} {nb.name}: {nb.result}\n')
        section.append('\n')
        return ''.join(section)


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
            head_message = red(self._h1_message('Failed Test(s)'))
            output_message.append(head_message)
            for cell, err in fails.items():
                output_message.append(f'---- {cell.notebook}: {cell.name} ----\n')
                output_message.append(str(cell))
                output_message.append(red('\n-----------------------------------------\n'))
                output_message.append(err)
                output_message.append('\n\n')


        if errors:
            failed_or_error = True
            head_message = orange(self._h1_message('Errored Test(s)'))
            output_message.append(head_message)
            for cell, err in errors.items():
                output_message.append(f'---- {cell.notebook}: {cell.name} ----\n')
                output_message.append(str(cell))
                output_message.append(red('\n-----------------------------------------\n'))
                output_message.append(err)
                output_message.append('\n\n')

        output_message.append(self._final_remarks)

        output_message = ''.join(output_message)
        if failed_or_error:
            print(output_message, file = sys.stderr)
        else:
            print(output_message, file = sys.stdout)
                



    @property
    def _final_remarks(self):
        all_tests = ''.join([nb.result for nb in self.notebooks])

        passed_test_count = all_tests.count('.')
        failed_test_count = all_tests.count('F')
        errored_test_count = all_tests.count('E')
        

        return self._h1_message(f'{green(f"{passed_test_count} test(s) passed")}, {red(f"{failed_test_count} failed")},{orange(f" and {errored_test_count} raised an error")}')
    

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
            if '.ipynb_checkpoints' in root:
                continue
            if re.match(r'^test_.+\.ipynb', file):
                notebooks.append(os.path.join(root, file))
                
    return notebooks
