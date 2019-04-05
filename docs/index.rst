.. pytest-fastest documentation master file, created by
   sphinx-quickstart on Thu Oct  1 00:43:18 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pytest-fastest
==============

pytest-fastest uses coverage data and Git to run just the tests you need.

We all want to write well-tested code, but in large projects that can mean running thousands of tests that can take a lot of time. pytest-fastest identifies tests:

* That test modules that have changed in Git,
* That we don't already have coverage data for, and
* That we've added or changed.

Installing
==========

Install with `pip`_ (package on `PyPI`_; source at `GitHub`_)::

  $ pip install pytest-fastest

Usage
=====

Most large projects usually work off a common Git branch such as ``dev`` or ``master``. When a developer wants to add a feature or bugfix, they create a new branch to do their work. After making some changes, they run tests to make sure everything still works, fix a few things, run more tests, fix things, and so on until they're happy with it. However, that "run tests" part can slow things down, as either lots of irrelevant of tests add time and screen clutter,or the developer manually figures out what really needs to be checked.

pytest-fastest automates that processes. It takes a parameter naming a Git commit, ``fastest-commit``, and compares the current state of the developer's work to that commit. It then builds a coverage map tracking which of the project's files have been accessed by each test function. In future runs with the appropriate ``fastest-mode`` set, it compares that coverage map to the ``git diff`` from fastest-commit to see which tests actually need to be executed - the rest are skipped.

Example
=======

First, we clone a large Git repo, create a new branch, and run the full unit test suite to gather coverage data::

  $ git clone myrepo
  $ git checkout dev
  $ git checkout -b feature/newstuff
  $ pytest tests/unit --fastest-mode=skip --fastest-commit=dev
  ...
  ============================ 569 passed in 19.76 seconds ============================

Now let's run the tests again::

  $ pytest tests/unit --fastest-mode=skip --fastest-commit=dev
  ...
  ============================ 569 skipped in 2.83 seconds ============================

Whoa! Magic! Now we modify a module in the package and run the tests::

  $ vi src/somefile.py
  $ pytest tests/unit --fastest-mode=skip --fastest-commit=dev
  ...
  ======================= 6 passed, 563 skipped in 3.03 seconds =======================

Only tests that refer to ``somefile.py`` were run, but everything else was skipped. Now let's add a new test::

  $ vi tests/unit/test_module.py
  $ pytest tests/unit --fastest-mode=skip --fastest-commit=dev
  ...
  ======================= 7 passed, 563 skipped in 2.98 seconds =======================

Our testing time has dropped from nearly twenty seconds to less than three, and we didn't have to do any work to figure out which tests needed to be run.

Modes
=====

pytest-fastest runs in one of several modes:

  - ``all`` (default): Run all tests without collecting coverage data. This emulates normal pytest behavior and has no effect on performance.
  - ``skip``: Skip tests that don't need to be run, but update coverage data on the ones that do run. This is the mode you will use most often in support of the workflow described above. It will usually be faster than ``all``, but because collecting coverage information takes some time, as the number of un-skippable tests grows very large it may actually become slower.
  - ``gather``: Don't skip any tests, but do gather coverage data. This is slower than ``all`` but can be used to seed the coverage cache.
  - ``cache``: This is a fast mode for fixing existing tests as it skips tests but doesn't update the coverage cache. It will never be slower than ``all`` and will always be faster than ``skip``. However, it might not pick up subtle changes you make to tests' call chains and could accidentally skip tests that the more conservative ``skip`` mode would notice.

Configuration
=============

While ``--fastest-commit`` may be given from the command line, most projects always make feature branches from the same common ``dev`` or ``master`` branch. In those cases, it's probably easier to add a setting like::

  [pytest]
  fastest_commit = dev

to your `pytest.ini`_. You can still override this with ``--fastest-commit`` if needed.

Limitations
===========

Only call graphs are examined. If ``module_a`` imports only a constant from ``module_b``, and you edit that constant, then pytest-fastest won't notice the change. This could lead to surprises. Running with ``--fastest-mode=all`` (or ``gather``) will run all tests that pytest would normally run, though.

Code changes are tracked at the module level, not the function level. If you modify ``module_a``, then any tests that access *any* functions in ``module_a`` will run. The main complication is that it's fairly difficult to accurately parse ``git diff``'s output to see exactly what's changed. Future versions may address this.

Git is the only SCM tool currently supported, although the design supports adding others.

Notes
=====

pytest-fastest stores its cached coverage data in a file named ``.fastest.coverage`` in the pytest rootdir.

History
=======

v0.0.9, 2019-04-05: Update the version of Requests. Switched to Poetry for packaging.

v0.0.8, 2018-08-27: Updated import paths for new versions of pytest.

v0.0.7: First generally usable release.

.. _`pip`: https://pypi.org/project/pip/
.. _`pytest.ini`: https://docs.pytest.org/en/latest/customize.html
.. _`PyPI`: https://pypi.org/project/pytest-fastest/
.. _`GitHub`: https://github.com/kstrauser/pytest-fastest
