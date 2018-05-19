"""Git backend for pytest-fastest."""

import pathlib
import subprocess
from typing import List, Set, Tuple


def cmd_output(args: List[str]) -> str:
    """Run a git command and return its output as a string."""

    return subprocess.check_output(['git', *args]).decode('UTF-8')


def find_toplevel() -> pathlib.Path:
    """Get the toplevel git directory."""

    return pathlib.Path(cmd_output(['rev-parse', '--show-toplevel']).strip())


def changes_since(commit: str) -> Tuple[Set[str], Set[Tuple[str, str]]]:
    """Get the set of changes between the given commit."""

    toplevel = find_toplevel()
    diff = cmd_output(['diff', commit])

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

        current_file = str(toplevel / fname[2:])
        changed_files.add(current_file)

    return changed_files, changed_tests
