"""Test My Notebook

.. ipython::

   In [1]: %load_ext testmynb

   In [2]: %%testcell
      ...: assert False
"""

__version__ = "0.0.1"

__author__ = "Young-Chan Park <young.chan.park93@gmail.com>"

from .magic import load_ipython_extension
from .handler import TestHandler
from .notebook import Notebook, TestCell
