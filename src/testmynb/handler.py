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
        col, _ = os.get_terminal_size()
        num_equals = (col - len(message) - 3) // 2
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
        
        for nb in self.notebooks:
            nb()
        
        print(self._summary)
        print(self._notebook_summary_section)


        errors = self.collect_errors()
        fails = self.collect_fails()

        if fails:
            head_message = red(self._h1_message('Failed Test(s)'))
            print(head_message)
            for cell, err in fails.items():
                print(f'---- {cell.notebook}: {cell.name} ----')
                print(cell)
                print(red('-----------------------------------------'))
                print(err)
                print('\n\n')


        if errors:
            head_message = orange(self._h1_message('Errored Test(s)'))
            print(head_message)
            for cell, err in errors.items():
                print(f'---- {cell.notebook}: {cell.name} ----')
                print(cell)
                print(red('-----------------------------------------'))
                print(err)
                print('\n\n')

        print(self._final_remarks)
                



    @property
    def _final_remarks(self):
        all_tests = ''.join([nb.result for nb in self.notebooks])

        passed_test_count = all_tests.count('.')
        failed_test_count = all_tests.count('F')
        errored_test_count = all_tests.count('E')
        
        f'{green(f"{passed_test_count} test(s) passed")}, {red(f"{failed_test_count} failed")},{orange(f" and {errored_test_count} raised an error")}'

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