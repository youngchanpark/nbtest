import io
import re
from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

with io.open("src/testmynb/__init__.py", "rt", encoding="utf8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

setup(
    name="testmynb",
    version=version,
    install_requires=["nbformat>=5.0.0", "ipython", "click", "pytest"],
    include_package_data=False,
    entry_points={"console_scripts": ["testmynb = testmynb.main:cli",],},
    # Metadata
    author="Young-Chan Park",
    author_email="young.chan.park93@gmail.com",
    description="A Jupyter Notebook Testing Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Testing",
        "Topic :: Utilities",
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.5.3",
)
