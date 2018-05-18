# -*- coding: utf-8 -*-

import os
import pathlib
import subprocess

import pytest_fastest


def test_help_message(testdir):
    result = testdir.runpytest(
        '--help',
    )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*--fastest-mode={all,skip,gather,cache}',
        '*--fastest-commit=FASTEST_COMMIT',
    ])


def test_fastest_commit_setting(testdir):
    testdir.makeini("""
        [pytest]
        fastest_commit = abc1234
    """)

    testdir.makepyfile("""
        import pytest

        @pytest.fixture
        def commit(request):
            return request.config.getini('fastest_commit')

        def test_commit(commit):
            assert commit == 'abc1234'
    """)

    result = testdir.runpytest('-v')

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_commit PASSED*',
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_git_toplevel(tmpdir):
    git_dir = tmpdir.mkdir('git_toplevel')
    os.chdir(str(git_dir))
    subprocess.check_call(['git', 'init'])

    subdir = git_dir / 'foo' / 'bar' / 'baz'
    os.makedirs(str(subdir))
    os.chdir(str(subdir))

    assert pathlib.Path(pytest_fastest.git_toplevel()) == git_dir


def test_git_changes_empty(mocker):
    mocker.patch('pytest_fastest.git_output', return_value="""\
""")

    assert pytest_fastest.git_changes('foo') == (set(), set())


def test_git_changes_example(mocker):
    mocker.patch('pytest_fastest.git_toplevel', return_value='here')
    mocker.patch('pytest_fastest.git_output', return_value='''\
diff --git a/pytest_fastest.py b/pytest_fastest.py
index a9584f8..0eec9e2 100644
--- a/pytest_fastest.py
+++ b/pytest_fastest.py
@@ -64,17 +64,24 @@ def pytest_addoption(parser):

 # Helpers

+
+def git_output(args: List[str]) -> str:
+    """Run a git command and return its output as a string."""
+
+    return subprocess.check_output(['git', *args]).decode('UTF-8')
+
+
 def git_toplevel() -> str:
     """Get the toplevel git directory."""

-    return subprocess.check_output(['git', 'rev-parse', '--show-toplevel']).strip()
+    return git_output(['rev-parse', '--show-toplevel']).strip()


 def git_changes(commit: str) -> Tuple[Set[str], Set[Tuple[str, str]]]:
     """Get the set of changes between the given commit."""

     root_dir = pathlib.Path(git_toplevel())
-    diff = subprocess.check_output(['git', 'diff', commit]).decode('UTF-8')
+    diff = git_output(['diff', commit])

     changed_files = set()
     changed_tests = set()
diff --git a/tests/test_fastest.py b/tests/test_fastest.py
index ddc9bcb..03d9e26 100644
--- a/tests/test_fastest.py
+++ b/tests/test_fastest.py
@@ -1,5 +1,7 @@
 # -*- coding: utf-8 -*-

+import pytest_fastest
+

 def test_help_message(testdir):
     result = testdir.runpytest(
@@ -38,3 +40,25 @@ def test_fastest_commit_setting(testdir):

     # make sure that that we get a '0' exit code for the testsuite
     assert result.ret == 0
+
+
+def test_git_toplevel(tmpdir):
+    import subprocess
+    import os
+
+    git_dir = tmpdir.mkdir('git_toplevel')
+    os.chdir(git_dir)
+    subprocess.check_call(['git', 'init'])
+
+    subdir = git_dir / 'foo' / 'bar' / 'baz'
+    os.makedirs(subdir)
+    os.chdir(subdir)
+
+    assert pytest_fastest.git_toplevel() == str(git_dir)
+
+
+def test_git_changes_empty(mocker):
+    mocker.patch('pytest_fastest.git_output', return_value="""\
+""")
+
+    assert pytest_fastest.git_changes('foo') == (set(), set())
\ No newline at end of file
''')

    assert pytest_fastest.git_changes('foo') == (
        {'here/tests/test_fastest.py', 'here/pytest_fastest.py'},
        {
            ('here/tests/test_fastest.py', 'test_fastest_commit_setting'),
            ('here/tests/test_fastest.py', 'test_git_changes_empty'),
            ('here/tests/test_fastest.py', 'test_git_toplevel'),
            ('here/tests/test_fastest.py', 'test_help_message'),
        }
    )
