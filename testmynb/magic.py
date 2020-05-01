from IPython.core.getipython import get_ipython


def testcell(line, cell):
    interactive_shell = get_ipython()
    interactive_shell.run_cell(cell)


def load_ipython_extension(ipython):
    ipython.register_magic_function(testcell, 'cell')
