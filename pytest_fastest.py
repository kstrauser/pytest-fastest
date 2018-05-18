# -*- coding: utf-8 -*-

"""Use coverage data and Git to determine which tests may be skipped."""

import contextlib
import enum
import json
import pathlib
import subprocess
import sys
from typing import Dict, List, Set, Tuple  # noqa: F401, pylint: disable=unused-import

import pytest
from _pytest.config import ArgumentError
from _pytest.runner import runtestprotocol

STOREFILE = '.fastest.coverage'
COVERAGE = {}  # type: Dict[str, List[str]]


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

def git_toplevel() -> str:
    """Get the toplevel git directory."""

    return subprocess.check_output(['git', 'rev-parse', '--show-toplevel']).decode('UTF-8').strip()


def git_changes(commit: str) -> Tuple[Set[str], Set[Tuple[str, str]]]:
    """Get the set of changes between the given commit."""

    root_dir = pathlib.Path(git_toplevel())
    diff = subprocess.check_output(['git', 'diff', commit]).decode('UTF-8')

    changed_files = set()
    changed_tests = set()
    current_file = ''

    for line in diff.splitlines():
        try:
            test_index = line.index('def test_')
        except ValueError:
            pass
        else:
            test_name = line[test_index + 4:].partition('(')[0]
            changed_tests.add((current_file, test_name))

        if not (line.startswith('--- ') or line.startswith('+++ ')):
            continue
        if not line.endswith('.py'):
            continue
        fname = line[4:]
        if fname == '/dev/null':
            continue
        if not (fname.startswith('a/') or fname.startswith('b/')):
            raise ValueError(
                'Pretty sure {!r} should start with a/ or b/'.format(fname)
            )

        current_file = str(root_dir / fname[2:])
        changed_files.add(current_file)

    return changed_files, changed_tests


@contextlib.contextmanager
def tracer(rootdir: str):
    """Collect call graphs for modules within the rootdir."""

    result = set()
    base_path = str(pathlib.Path(rootdir))

    def trace_calls(frame, event, arg):  # pylint: disable=unused-argument
        """settrace calls this every time something interesting happens."""

        if event != 'call':
            return

        func_filename = frame.f_code.co_filename

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
            return json.load(infile)
    except FileNotFoundError:
        return {}


def save_coverage(coverage):
    """Save the coverage data to disk."""

    with open(STOREFILE, 'w') as outfile:
        json.dump(coverage, outfile, indent=2)


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
        return

    covered_files = set()
    for file_list in COVERAGE.values():
        covered_files.update(set(file_list))
    changed_files, changed_tests = git_changes(config.cache.fastest_commit)

    affected_nodes = set()
    for nodeid, files in COVERAGE.items():
        for fname in files:
            if fname in changed_files:
                affected_nodes.add(nodeid)

    skip = pytest.mark.skip(reason='skipper')

    for item in items:
        if not any((
                # Tests refer to modules that have changed
                item.nodeid in affected_nodes,
                # Tests that we don't already have coverage data for
                str(item.fspath) not in covered_files,
                # Tests that have themselves been changed
                (str(item.fspath), item.name) in changed_tests,
        )):
            item.add_marker(skip)

    return True


def pytest_runtest_protocol(item, nextitem):
    """Gather coverage data for the item."""

    if not item.config.cache.fastest_gather:
        return

    with tracer(item.config.rootdir) as coverage:
        reports = runtestprotocol(item, nextitem=nextitem)

    item.ihook.pytest_runtest_logfinish(
        nodeid=item.nodeid, location=item.location,
    )

    outcomes = {report.when: report.outcome for report in reports}
    if outcomes['setup'] == 'skipped':
        return True

    if outcomes['call'] == 'passed':
        COVERAGE[item.nodeid] = sorted(coverage)
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
