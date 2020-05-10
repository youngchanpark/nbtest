import re
from typing import List

from IPython.core.getipython import get_ipython



def _remove_strings(text: str) -> str:
    """Removes strings
    
    Example
    -------
    >>> _remove_strings('print("hello")')
    'print()'
    """
    return re.sub(r'(\'.*\')|(\".*\")', '', text)

def _split_statements(text: str) -> List[str]:
    """Splits a string on `\n` and `;`.
    
    Examples
    --------
    >>> _split_statements('print()\\nassert True')
    ['print()', 'assert True']
    >>> _split_statements('print() ; assert True')
    ['print()', 'assert True']
    """
    # If you see closely in the first example in the docstring,
    # You'll notice that the newline is written as `\\n` rather than `\n`.
    # This is because `\n` is converted to a real newline when parsed as a docstring
    # and messes up doctest and reader-side of the docstring!
    split_text = re.split(r'\n|;', text) 
    return [line.strip() for line in split_text if line]

def _assert_exists(split_text: List[str]) -> bool:
    """Checks whether an `assert` statement exists in the given `split_text` 
    Examples
    --------
    >>> _assert_exists(['print()', 'assert True'])
    True
    >>> _assert_exists(['print()'])
    False
    """
    assert_found = False
    for line in split_text:
        if re.match(r'^assert', line):
            assert_found = True
            break
    return assert_found

def _search_assert(cell: str) -> bool:
    """
    >>> _search_assert('print();assert True')
    True
    >>> _search_assert('print()')
    False
    """
    stringless_cell: str = _remove_strings(cell)
    split_text: List[str] = _split_statements(stringless_cell)    
    assert_found: bool = _assert_exists(split_text)

    return assert_found

def _split_line(line: str) -> List[str]:
    """
    >>> _split_line('%%testcell test_cell1 # hello')
    ['test_cell1']
    >>> _split_line('%%testcell -n # test_cell1')
    []
    """
    positional_args = [arg for arg in re.split(r' +', line)
            if not re.match(r'^(%|-)', arg)
            and arg]
    if '#' in positional_args:
        del positional_args[positional_args.index('#'):]

    return positional_args

def testcell(line, cell):
    positional_args = _split_line(line)

    interactive_shell = get_ipython()

    if ('-n' not in line) and (not _search_assert(cell)):
        interactive_shell.run_code('print("[testmynb] Assert statement missing.")')

    if not positional_args:
        interactive_shell.run_code('print("[testmynb] Cell title missing.")')

    interactive_shell.run_cell(cell)



def load_ipython_extension(ipython):
    ipython.register_magic_function(testcell, 'cell')
