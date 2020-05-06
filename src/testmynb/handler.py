import os
import re
import sys

from . import __version__ as testmynb__version__

class TestHandler:
    def __init__(self, *notebooks):
        self.notebooks = notebooks
            
    def __call__(self):
        
        for nb in self.notebooks:
            nb()
        
        notebook_count = len(self.notebooks)
        test_count = sum([len(nb.extract_codes()) for nb in self.notebooks])
        py_ver = re.sub(r'\s.*', '', sys.version)
        
        head_message = f' Test My Notebook ({testmynb__version__}) '
        col, _ = os.get_terminal_size()
        num_equals = (col - len(head_message)) // 2
        equals_sign = num_equals * '='

        print(
            f'{equals_sign}{head_message}{equals_sign}\n'
            f'Platform {sys.platform}\n'
            f'Python {py_ver}\n'
            f'Working Directory: {os.getcwd()}\n'
            '\n'
            f'{test_count} test cells across {notebook_count} notebook(s) detected.\n'
            '\n'
            'Notebooks:'
            ''
        )
        for nb in self.notebooks:
            trust = 'Trusted' if nb.trusted else 'Untrusted'
            print(f'{trust} {nb.name}: {nb.result}')
        print('\n')
        errors = self.collect_errors()
        fails = self.collect_fails()
        
        if errors:
            head_message = ' Errored Test(s) '
            num_equals = (col - len(head_message)) // 2
            equals_sign = num_equals * '='
            print(f'{equals_sign}{head_message}{equals_sign}\n')
            for cell, err in errors.items():
                print(f'---- {cell.notebook}: {cell.name} ----\n')
                print(cell)
                print('-----------------------------------------')
                print(err)
                #print(f'---- {cell.notebook}: {cell.name} ----\n')
                print('\n\n\n\n\n')
                
        if fails:
            head_message = ' Failed Test(s) '
            num_equals = (col - len(head_message)) // 2
            equals_sign = num_equals * '='
            print(f'{equals_sign}{head_message}{equals_sign}\n')
            for cell, err in fails.items():
                print(f'---- {cell.notebook}: {cell.name} ----\n')
                print(cell)
                print('-----------------------------------------')
                print(err)
                #print(f'---- {cell.notebook}: {cell.name} ----\n') 
                print('\n\n\n\n\n')

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