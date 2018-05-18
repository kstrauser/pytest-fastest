==============
pytest-fastest
==============

.. image:: https://img.shields.io/pypi/v/pytest-fastest.svg
    :target: https://pypi.org/project/pytest-fastest
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/pytest-fastest.svg
    :target: https://pypi.org/project/pytest-fastest
    :alt: Python versions

.. image:: https://travis-ci.com/kstrauser/pytest-fastest.svg?branch=dev
    :target: https://travis-ci.com/kstrauser/pytest-fastest
    :alt: See Build Status on Travis CI

.. image:: https://ci.appveyor.com/api/projects/status/github/kstrauser/pytest-fastest?branch=dev
    :target: https://ci.appveyor.com/project/kstrauser/pytest-fastest/branch/dev
    :alt: See Build Status on AppVeyor

Use SCM and coverage to run only needed tests

----

This `pytest`_ plugin was generated with `Cookiecutter`_ along with `@hackebrot`_'s `cookiecutter-pytest-plugin`_ template.


Features
--------

* Gathers coverage data from tests to track which tests call functions from which modules.
* Uses Git to track changes from a given commit to find the minimum set of tests that need to run to test new changes, then skips everything else.


Requirements
------------

* Python 3.4+
* pytest 3.4.0+


Installation
------------

You can install "pytest-fastest" via `pip`_ from `PyPI`_::

    $ pip install pytest-fastest


Usage
-----

pytest-fastest can be set to run only tests:

* That test modules that have changed in Git,
* Tests that we don't already have coverage data for, and
* Tests that we've added or changed.

In most common development workflows where you make short-lived branches
off a main "master" or "dev" branch, the amount of code that actually
changes while fixing a bug or writing a feature is usually just a small
portion of the whole codebase. Instead of running thousands of tests
after each change, pytest-fastest can identify the relevant ones that
thoroughly test your work but skip all the things you *haven't* changed.

To use it:

* In ``pytest.ini``, set ``fastest_commit`` to the name of a Git commit to
  compare your current work against. (You can also set or override it on the
  comment line with ``--fastest-commit``). This is required if you want to
  skip tests, which is the main reason for using this plugin.

* Use the command line argument ``--fastest-mode`` to choice the appropriate
  running mode:

  - ``all`` (default): Run all tests without collecting coverage data. This
    emulates normal pytest behavior and has no effect on performance.
  - ``skip``: Skip tests that don't need to be run, but update coverage data
    on the ones that do run. This will usually be faster than ``all``, but
    because collecting coverage information takes some time, as the number
    of un-skippable tests grows very large it may actually become slower.
  - ``gather``: Don't skip any tests, but do gather coverage data. This is
    slower than ``all`` but can be used to seed the coverage cache.
  - ``cache``: This is a fast mode for fixing existing tests. It skips tests
    but doesn't update the coverage cache. It will never be slower than
    ``all`` and will always be faster than ``skip``.

Contributing
------------
Contributions are very welcome. Tests can be run with `tox`_, please ensure
the coverage at least stays the same before you submit a pull request.

License
-------

Distributed under the terms of the `MIT`_ license, "pytest-fastest" is free and open source software


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter
.. _`@hackebrot`: https://github.com/hackebrot
.. _`MIT`: http://opensource.org/licenses/MIT
.. _`BSD-3`: http://opensource.org/licenses/BSD-3-Clause
.. _`GNU GPL v3.0`: http://www.gnu.org/licenses/gpl-3.0.txt
.. _`Apache Software License 2.0`: http://www.apache.org/licenses/LICENSE-2.0
.. _`cookiecutter-pytest-plugin`: https://github.com/pytest-dev/cookiecutter-pytest-plugin
.. _`file an issue`: https://github.com/kstrauser/pytest-fastest/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`pip`: https://pypi.org/project/pip/
.. _`PyPI`: https://pypi.org/project
