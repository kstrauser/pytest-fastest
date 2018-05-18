# -*- coding: utf-8 -*-

import contextlib
import enum
import json
import pathlib
import subprocess
import sys

import pytest
from _pytest.runner import runtestprotocol

STOREFILE = '/tmp/amino_user.test.coverage'
COVERAGE = {}

class Mode(enum.Enum):
    # Run all tests without collecting coverage data: normal pytest behavior
    ALL = 'all'
    # Skip tests that don't need to be run, but update coverage data on the ones that do
    SKIP = 'skip'
    # Don't skip tests, but gather coverage data
    GATHER = 'gather'
    # Skip tests, but don't gather coverage data
    CACHE = 'cache'


def pytest_addoption(parser):
    group = parser.getgroup('fastest')
    group.addoption(
        '--fastest-mode',
        default='all',
        choices=[mode.value for mode in Mode],
        action='store',
        dest='fastest_mode',
        help='Set the value for the fixture "bar".'

    )


def git_toplevel():
    return subprocess.check_output(['git', 'rev-parse', '--show-toplevel']).decode('UTF-8').strip()


def git_changes(commit='dev'):
    root_dir = pathlib.Path(git_toplevel())
    diff = subprocess.check_output(['git', 'diff', commit]).decode('UTF-8')

    changed_files = set()
    changed_tests = set()
    current_file = None

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
            raise ValueError(f'Pretty sure {fname!r} should start with a/ or b/')

        current_file = str(root_dir / fname[2:])
        changed_files.add(current_file)

    return changed_files, changed_tests


def pytest_configure(config):
    config.cache.fastest_mode = config.getoption('fastest_mode')

    config.cache.fastest_skip, config.cache.fastest_gather = {
        Mode.ALL.value: (False, False),
        Mode.SKIP.value: (True, True),
        Mode.GATHER.value: (False, True),
        Mode.CACHE.value: (True, False),
    }[config.cache.fastest_mode]

    COVERAGE.clear()
    if config.cache.config.cache.fastest_gather or config.cache.fastest_skip:
        COVERAGE.update(load_coverage())


def pytest_collection_modifyitems(config, items):
    if not config.cache.fastest_skip:
        return

    covered_files = set()
    for file_list in COVERAGE.values():
        covered_files.update(set(file_list))
    changed_files, changed_tests = git_changes()

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


@contextlib.contextmanager
def tracer(rootdir):
    result = set()
    base_path = str(pathlib.Path(rootdir))

    def trace_calls(frame, event, arg):
        if event != 'call':
            return
        co = frame.f_code
        func_filename = co.co_filename

        if not func_filename.endswith('.py'):
            return
        if not func_filename.startswith(base_path):
            return

        result.add(func_filename)

    sys.settrace(trace_calls)
    try:
        yield result
    finally:
        sys.settrace(None)


def pytest_terminal_summary(terminalreporter, exitstatus):
    """Report all the things."""

    if COVERAGE:
        save_coverage(COVERAGE)


def load_coverage():
    try:
        with open(STOREFILE, 'r') as infile:
            return json.load(infile)
    except FileNotFoundError:
        return {}

def save_coverage(coverage):
    with open(STOREFILE, 'w') as outfile:
        json.dump(coverage, outfile, indent=2)
