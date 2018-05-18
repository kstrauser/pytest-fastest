#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='pytest-fastest',
    version='0.0.5',
    author='Kirk Strauser',
    author_email='kirk@strauser.com',
    maintainer='Kirk Strauser',
    maintainer_email='kirk@strauser.com',
    license='MIT',
    url='https://github.com/kstrauser/pytest-fastest',
    description='Use SCM and coverage data to run only needed tests',
    long_description=read('README.rst'),
    py_modules=['pytest_fastest'],
    python_requires='>3, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
    install_requires=['pytest>=3.4.0'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'pytest11': [
            'fastest = pytest_fastest',
        ],
    },
)
