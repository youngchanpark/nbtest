import doctest
from testmynb.magic import (remove_strings, split_statements
                            , assert_exists, search_assert)


def test_remove_strings1():
    text = 'print("hello")'
    assert 'print()' == remove_strings(text)

    
def test_remove_strings2():
    text = 'print(\'hello;\', "random")'
    assert 'print(, )' == remove_strings(text)


def test_split_statements():
    result = split_statements('print()\nprint()')
    expected = ['print()', 'print()']
    
    assert result == expected, result

doctest.testmod()
