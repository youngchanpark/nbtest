import os
import re
import traceback
from collections import UserString
from typing import List, TextIO

import nbformat
from nbformat.sign import NotebookNotary
from nbformat.notebooknode import NotebookNode, from_dict

notebook_notary = NotebookNotary()


class TestCell(UserString):
    """
    A class for Jupyter Notebook code cell.
    
    Attributes
    ----------
    ignore : bool    
        Whether the cell magic line contained the `-t` option.
    name : str    
        The user defined name of the test cell block.
    """

    def __init__(self, data, notebook):
        super().__init__(data["source"])
        magic_args = self.parse_cell_magic(self)
        if "-n" in magic_args:
            self.ignore = True
            magic_args.remove("-n")
        else:
            self.ignore = False

        try:
            self.name = magic_args[0]
        except IndexError:
            self.name = "unnamed"

        self.data = re.sub(r"\%\%testcell.*\n", "", self.data, count=1)

        self.notebook = notebook

        self.result = None

    @staticmethod
    def parse_cell_magic(source: str) -> List[str]:
        line = source.split("\n")[0]
        args = re.split(r" +", line)
        del args[0]  # delete '%%testcell'
        return args

    def __str__(self):
        return self.data

    def __repr__(self):
        return self.name

    def __call__(self):

        try:
            exec(str(self), self.notebook.env)
            status = "."
            err = ""
        except AssertionError:
            status = "F"
            err = self._modify_err(traceback.format_exc())
            # This traceback function only works within the exception block.
        except:
            status = "E"
            err = self._modify_err(traceback.format_exc())

        self.result = status, err

        return status, err

    def _modify_err(self, err):
        split_err = err.split("\n")
        exec_run_string = split_err[3]

        mod_exec_run_string = exec_run_string.replace(
            '"<string>"', '"{}"'.format(self.notebook.ipynb)
        ).replace("<module>", self.name)
        split_err[3] = mod_exec_run_string

        error_line_num = self._extract_test_cell_error_line(exec_run_string)
        error_line = self.data.split("\n")[error_line_num - 1]
        split_err.insert(4, "    " + error_line)
        del split_err[1]
        del split_err[1]
        return "\n".join(split_err)

    @staticmethod
    def _extract_test_cell_error_line(string: str) -> int:
        """
        >>> TestCell._extract_test_cell_error_line('  File "<string>", line 2, in <module>')
        2
        """
        matched = re.search(r"(?!line )[0-9]+(?=, )", string)
        start, end = matched.span()
        return int(string[start:end])


class Notebook(NotebookNode):
    """
    A class used to read the Jupyter Notebook
    
    Parameters
    ----------
    ipynb : TextIO
        Path to the `.ipynb` file.
    
    Attributes
    ----------
    ipynb : TextIO
        Absolute path to the `.ipynb` file that was given to instantiate the instance.
    
    name : str
        Name of the `.ipynb` file.
    
    trusted : bool
        Whether the Notebook is `Trusted` or not for the user.
    
    nbformat : str
        The Jupyter Notebook format number.
    
    Methods
    -------
    extract_codes()
        Returns a list of code cells with the `%%testcell` cell magic. 
    
    """

    def __init__(self, ipynb: TextIO):
        _notebook = nbformat.read(ipynb, as_version=4)
        value = from_dict(_notebook)

        # self is a dict. If you look at the MRO, NotebookNode is a dict.
        # Think of the below as two dicts (`self` and `value`) merging
        # (where `self` happens to be an empty dict).
        dict.__init__(self, value)

        self.__dict__["ipynb"] = os.path.abspath(ipynb)
        self.__dict__["name"] = os.path.basename(ipynb)
        self.__dict__["env"] = dict()

        self.__dict__["tests"] = self.extract_codes()

        self.__dict__["result"] = None
        self.__dict__["stack"] = None

    @property
    def trusted(self):
        return notebook_notary.check_signature(self)

    def extract_codes(self) -> List[TestCell]:
        test_list = list()
        for cell in self.cells:
            if cell.cell_type == "code" and re.match(r"^%%testcell", cell.source):
                test_list.append(TestCell(cell, self))
        return test_list

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        return self.name == other.name

    def __repr__(self):
        return self.name

    def __call__(self):
        result = list()
        stack = dict()
        for cell in self.tests:

            status, err = cell()
            result.append(status)
            if status != ".":
                stack[cell] = {"status": status, "traceback": err}

        self.__dict__["result"] = "".join(result)
        self.__dict__["stack"] = stack

    def get_error_stack(self):
        error_stack = dict()
        for cell, err in self.stack.items():
            if err["status"] == "E":
                error_stack[cell] = err["traceback"]
        return error_stack

    def get_fail_stack(self):
        fail_stack = dict()
        for cell, err in self.stack.items():
            if err["status"] == "F":
                fail_stack[cell] = err["traceback"]
        return fail_stack
