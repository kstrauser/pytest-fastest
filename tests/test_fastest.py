# -*- coding: utf-8 -*-


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
