#!/usr/bin/env python
import os
import io
import re
import shutil
import sys
from setuptools import setup, find_packages


def read(*names, **kwargs):
    with io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8")
    ) as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

VERSION = find_version('gluonfr', '__init__.py')

requirements = [
    'numpy',
    'tqdm',
    'requests',
    # 'mxnet',
    'matplotlib',
    'seaborn',
    'Pillow',
    'scipy',
]

setup(
    # Metadata
    name='gluonfr',
    version=VERSION,
    author='haoxintong',
    url='https://github.com/THUFutureLab/gluon-face',
    description='Gluon FR Toolkit',
    long_description=long_description,
    license='MIT',

    # Package info
    packages=find_packages(exclude=('docs', 'tests', 'scripts')),

    zip_safe=True,
    include_package_data=True,
    install_requires=requirements,
)