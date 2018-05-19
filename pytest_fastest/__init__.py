# -*- coding: utf-8 -*-

"""Use coverage data and Git to determine which tests may be skipped."""

import contextlib
import enum
import json
import pathlib
import sys
from typing import Dict, List, Set, Tuple  # noqa: F401, pylint: disable=unused-import

import pytest
from _pytest.config import ArgumentError
from _pytest.runner import runtestprotocol

from . import git

STOREFILE = '.fastest.coverage'
COVERAGE = {}  # type: Dict[str, List[str]]
STOREVERSION = 1


# Configuration

class Mode(enum.Enum):
    """Enumerated running modes."""

    # Run all tests without collecting coverage data: normal pytest behavior
    ALL = 'all'
    # Skip tests that don't need to be run, but update coverage data on the ones that do
    SKIP = 'skip'
    # Don't skip tests, but gather coverage data
    GATHER = 'gather'
    # Skip tests, but don't gather coverage data
    CACHE = 'cache'


def pytest_addoption(parser):
    """Add command line options."""

    group = parser.getgroup('fastest')
    group.addoption(
        '--fastest-mode',
        default='all',
        choices=[mode.value for mode in Mode],
        action='store',
        dest='fastest_mode',
        help=(
            'Set the running mode.'
            ' `all` runs all tests but does not collect coverage data.'
            ' `skip` skips tests that can be skipped, and updates coverage data on the rest.'
            ' `gather` runs all tests and gathers coverage data on them.'
            ' `cache` skips tests and does not collect coverage data.'
        )
    )
    group.addoption(
        '--fastest-commit',
        action='store',
        dest='fastest_commit',
        help='Git commit to compare current work against.'
    )

    parser.addini('fastest_commit', 'Git commit to compare current work against')


# Helpers

@contextlib.contextmanager
def tracer(rootdir: str, own_file: str):
    """Collect call graphs for modules within the rootdir."""

    result = set()
    base_path = str(pathlib.Path(rootdir))

    def trace_calls(frame, event, arg):  # pylint: disable=unused-argument
        """settrace calls this every time something interesting happens."""

        if event != 'call':
            return

        func_filename = frame.f_code.co_filename
        if func_filename == own_file:
            return
        if not func_filename.endswith('.py'):
            return
        if not func_filename.startswith(base_path):
            return

        result.add(func_filename)

    sys.settrace(trace_calls)
    try:
        yield result
    finally:
        sys.settrace(None)  # type: ignore


def load_coverage():
    """Load the coverage data from disk."""

    try:
        with open(STOREFILE, 'r') as infile:
            data = json.load(infile)
    except FileNotFoundError:
        return {}

    try:
        if data['version'] != STOREVERSION:
            return {}
    except KeyError:
        return {}

    return data['coverage']


def save_coverage(coverage):
    """Save the coverage data to disk."""

    with open(STOREFILE, 'w') as outfile:
        json.dump({
            'coverage': coverage,
            'version': STOREVERSION,
        }, outfile, indent=2)


# Hooks

def pytest_configure(config):
    """Process the configuration."""

    config.cache.fastest_commit = (
        config.getoption('fastest_commit') or config.getini('fastest_commit')
    )
    config.cache.fastest_mode = config.getoption('fastest_mode')

    config.cache.fastest_skip, config.cache.fastest_gather = {
        Mode.ALL.value: (False, False),
        Mode.SKIP.value: (True, True),
        Mode.GATHER.value: (False, True),
        Mode.CACHE.value: (True, False),
    }[config.cache.fastest_mode]

    if config.cache.fastest_skip and not config.cache.fastest_commit:
        raise ArgumentError(
            'fastest_mode',
            'Mode {} requires fastest_commit to be set.'.format(
                config.cache.fastest_mode
            )
        )

    COVERAGE.clear()
    if config.cache.config.cache.fastest_gather or config.cache.fastest_skip:
        COVERAGE.update(load_coverage())


def pytest_collection_modifyitems(config, items):
    """Mark unaffected tests as skippable."""

    if not config.cache.fastest_skip:
        return None

    covered_test_files = {covdata['fspath'] for covdata in COVERAGE.values()}
    changed_files, changed_tests = git.changes_since(config.cache.fastest_commit)

    affected_nodes = set()
    for nodeid, covdata in COVERAGE.items():
        if any(fname in changed_files for fname in covdata['files']):
            affected_nodes.add(nodeid)

    skip = pytest.mark.skip(reason='skipper')

    for item in items:
        if not any((
                # Tests refer to modules that have changed
                item.nodeid in affected_nodes,
                # Tests that we don't already have coverage data for
                str(item.fspath) not in covered_test_files,
                # Tests that have themselves been changed
                (str(item.fspath), item.name) in changed_tests,
        )):
            item.add_marker(skip)

    return True


def pytest_runtest_protocol(item, nextitem):
    """Gather coverage data for the item."""

    if not item.config.cache.fastest_gather:
        return None

    with tracer(item.config.rootdir, str(item.fspath)) as coverage:
        reports = runtestprotocol(item, nextitem=nextitem)

    item.ihook.pytest_runtest_logfinish(
        nodeid=item.nodeid, location=item.location,
    )

    outcomes = {report.when: report.outcome for report in reports}
    if outcomes['setup'] in {'failed', 'skipped'}:
        return True

    if outcomes['call'] == 'passed':
        COVERAGE[item.nodeid] = {
            'files': sorted(coverage),
            'fspath': str(item.fspath),
        }
    else:
        try:
            del COVERAGE[item.nodeid]
        except KeyError:
            pass

    return True


def pytest_terminal_summary(terminalreporter, exitstatus):  # pylint: disable=unused-argument
    """Save the coverage data we've collected."""

    if COVERAGE:
        save_coverage(COVERAGE)
