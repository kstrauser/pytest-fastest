# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pytest_fastest']

package_data = \
{'': ['*']}

install_requires = \
['pytest>=4.4,<5.0']

entry_points = \
{'pytest11': ['fastest = pytest_fastest']}

setup_kwargs = {
    'name': 'pytest-fastest',
    'version': '0.0.9',
    'description': 'Use SCM and coverage to run only needed tests',
    'long_description': '==============\npytest-fastest\n==============\n\n.. image:: https://img.shields.io/pypi/v/pytest-fastest.svg\n    :target: https://pypi.org/project/pytest-fastest\n    :alt: PyPI version\n\n.. image:: https://img.shields.io/pypi/pyversions/pytest-fastest.svg\n    :target: https://pypi.org/project/pytest-fastest\n    :alt: Python versions\n\n.. image:: https://travis-ci.com/kstrauser/pytest-fastest.svg?branch=dev\n    :target: https://travis-ci.com/kstrauser/pytest-fastest\n    :alt: See Build Status on Travis CI\n\n.. image:: https://ci.appveyor.com/api/projects/status/github/kstrauser/pytest-fastest?branch=dev\n    :target: https://ci.appveyor.com/project/kstrauser/pytest-fastest/branch/dev\n    :alt: See Build Status on AppVeyor\n\nUse SCM and coverage to run only needed tests\n\n----\n\nThis `pytest`_ plugin was generated with `Cookiecutter`_ along with `@hackebrot`_\'s `cookiecutter-pytest-plugin`_ template.\n\n\nFeatures\n--------\n\n* Gathers coverage data from tests to track which tests call functions from which modules.\n* Uses Git to track changes from a given commit to find the minimum set of tests that need to run to test new changes, then skips everything else.\n\n\nRequirements\n------------\n\n* Python 3.5+\n* pytest 3.4.0+\n\n\nInstallation\n------------\n\nYou can install "pytest-fastest" via `pip`_ from `PyPI`_::\n\n    $ pip install pytest-fastest\n\n\nUsage\n-----\n\npytest-fastest can be set to run only tests:\n\n* That test modules that have changed in Git,\n* Tests that we don\'t already have coverage data for, and\n* Tests that we\'ve added or changed.\n\nIn most common development workflows where you make short-lived branches\noff a main "master" or "dev" branch, the amount of code that actually\nchanges while fixing a bug or writing a feature is usually just a small\nportion of the whole codebase. Instead of running thousands of tests\nafter each change, pytest-fastest can identify the relevant ones that\nthoroughly test your work but skip all the things you *haven\'t* changed.\n\nTo use it:\n\n* In ``pytest.ini``, set ``fastest_commit`` to the name of a Git commit to\n  compare your current work against. (You can also set or override it on the\n  command line with ``--fastest-commit``). This is required if you want to\n  skip tests, which is the main reason for using this plugin.\n\n* Use the command line argument ``--fastest-mode`` to choice the appropriate\n  running mode:\n\n  - ``all`` (default): Run all tests without collecting coverage data. This\n    emulates normal pytest behavior and has no effect on performance.\n  - ``skip``: Skip tests that don\'t need to be run, but update coverage data\n    on the ones that do run. This will usually be faster than ``all``, but\n    because collecting coverage information takes some time, as the number\n    of un-skippable tests grows very large it may actually become slower.\n  - ``gather``: Don\'t skip any tests, but do gather coverage data. This is\n    slower than ``all`` but can be used to seed the coverage cache.\n  - ``cache``: This is a fast mode for fixing existing tests. It skips tests\n    but doesn\'t update the coverage cache. It will never be slower than\n    ``all`` and will always be faster than ``skip``.\n\nContributing\n------------\nContributions are very welcome. Tests can be run with `tox`_, please ensure\nthe coverage at least stays the same before you submit a pull request.\n\nLicense\n-------\n\nDistributed under the terms of the `MIT`_ license, "pytest-fastest" is free and open source software\n\n\nIssues\n------\n\nIf you encounter any problems, please `file an issue`_ along with a detailed description.\n\n.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter\n.. _`@hackebrot`: https://github.com/hackebrot\n.. _`MIT`: http://opensource.org/licenses/MIT\n.. _`BSD-3`: http://opensource.org/licenses/BSD-3-Clause\n.. _`GNU GPL v3.0`: http://www.gnu.org/licenses/gpl-3.0.txt\n.. _`Apache Software License 2.0`: http://www.apache.org/licenses/LICENSE-2.0\n.. _`cookiecutter-pytest-plugin`: https://github.com/pytest-dev/cookiecutter-pytest-plugin\n.. _`file an issue`: https://github.com/kstrauser/pytest-fastest/issues\n.. _`pytest`: https://github.com/pytest-dev/pytest\n.. _`tox`: https://tox.readthedocs.io/en/latest/\n.. _`pip`: https://pypi.org/project/pip/\n.. _`PyPI`: https://pypi.org/project\n',
    'author': 'Kirk Strauser',
    'author_email': 'kirk@amino.com',
    'url': 'https://github.com/kstrauser/pytest-fastest',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
