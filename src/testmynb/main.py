import click

from testmynb.handler import TestHandler, find_notebooks
from testmynb.notebook import Notebook

@click.command()
@click.argument('path', type=click.Path(exists=True), nargs=-1) # 'Path to notebooks or directories to search for test notebooks.'
def cli(path):
    test_notebooks = find_notebooks(*path)
    handler = TestHandler(*[Notebook(nb) for nb in test_notebooks])
    handler.notebooks
    handler()



if __name__ == '__main__':
    cli()