# -*- coding: utf-8 -*-

import json
import subprocess
import sys
from collections import defaultdict
from contextlib import contextmanager
from functools import singledispatch
from pathlib import Path
from types import ModuleType
from typing import Callable

import pytest
from _pytest.runner import runtestprotocol

STOREFILE = '/tmp/amino_user.test.coverage'
COVERAGE = {}


def pytest_addoption(parser):
    group = parser.getgroup('fastest')
    group.addoption(
        '--fastest-package',
        action='store',
        dest='fastest_package',
        help='Set the value for the fixture "bar".'
    )

    parser.addini('HELLO', 'Dummy pytest.ini setting')


def git_toplevel():
    return subprocess.check_output(['git', 'rev-parse', '--show-toplevel']).decode('UTF-8').strip()

def git_changes(commit='dev'):
    root_dir = Path(git_toplevel())
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

        if not line.startswith('--- ') or line.startswith('+++ '):
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
    fastest_package = config.getoption('fastest_package')
    if fastest_package:
        config.cache.fastest_package = path_of_module(fastest_package)
    else:
        config.cache.fastest_package = None

def pytest_collection_modifyitems(config, items):
    if not config.cache.fastest_package:
        return

    COVERAGE.clear()
    COVERAGE.update(load_coverage())

    changed_files, changed_tests = git_changes()

    affected_nodes = set()
    for nodeid, files in COVERAGE.items():
        for fname in files: 
            if fname in changed_files:
                affected_nodes.add(nodeid)

    index = 0
    while index < len(items):
        item = items[index]
        if (
                item.nodeid in affected_nodes or
                (str(item.fspath), item.name) in changed_tests
        ):
            index += 1
        else:
            del items[index]

    return

def pytest_runtest_protocol(item, nextitem):
    if not item.config.cache.fastest_package:
        return

    with tracer(item.config.cache.fastest_package) as coverage:
        reports = runtestprotocol(item, nextitem=nextitem)

    result = next(report.outcome for report in reports if report.when == 'call')
    if result == 'passed':
        COVERAGE[item.nodeid] = sorted(coverage)
    else:
        try:
            del COVERAGE[item.nodeid]
        except KeyError:
            pass

    return True

@pytest.fixture
def bar(request):
    return request.config.option.dest_foo

@singledispatch
def path_of(obj: str) -> Path:
    return path_of_path(Path(obj))

@path_of.register(Path)
def path_of_path(obj: Path) -> Path:
    if obj.is_dir():
        return obj
    return obj.parent

@path_of.register(Callable)
def path_of_func(obj: Callable) -> Path:
    return path_of_module(obj.__module__)

@path_of.register(ModuleType)
def path_of_module(obj: ModuleType) -> Path:
    return Path(sys.modules[obj].__file__).absolute().parent


@contextmanager
def tracer(startswith):
    result = set()
    base_path = str(path_of(startswith))

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
