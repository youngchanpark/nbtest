import io
import re
from setuptools import setup, find_packages


with io.open("src/testmynb/__init__.py", "rt", encoding="utf8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

setup(
    name = "testmynb",
    version = version,
    install_requires = ['nbformat>=5.0.0'],
    include_package_data = False,
    
# Metadata
    author = "Young-Chan Park",
    author_email = "young.chan.park93@gmail.com",
    description = "",
    packages = find_packages(where = 'src'),
    package_dir={"": "src"},
    classifiers = [
        "Programming Language :: Python :: 3"
    ],
    python_requires='>=3.5',
)
