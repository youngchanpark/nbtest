from testmynb.magic import (
    _remove_strings,
    _split_statements,
    _assert_exists,
    _search_assert,
)


def test_remove_strings1():
    text = 'print("hello")'
    assert "print()" == _remove_strings(text)


def test_remove_strings2():
    text = "print('hello;', \"random\")"
    assert "print(, )" == _remove_strings(text)


def test_split_statements():
    result = _split_statements("print()\nprint()")
    expected = ["print()", "print()"]

    assert result == expected, result
