import sys
import os
import signal

import py
import pytest
from splinter.browser import Browser

@pytest.fixture(scope='session')
def database_url():
    return str(py.path.local('test.shelve'))


@pytest.fixture(scope='session')
def test_server(xprocess, request, database_url):
    def preparefunc(cwd):
        server_mod = py.path.local('src/whatsmyrank/web.py')
        os.environ['QUEST_DATABASE_URL'] = database_url
        return ('started', [sys.executable, server_mod, ])

    pid, log = xprocess.ensure('server', preparefunc)

    def fin():
        os.kill(pid, signal.SIGKILL)

    request.addfinalizer(fin)

    def get_url(url):
        return 'http://localhost:8080{}'.format(url)

    return get_url


@pytest.fixture(scope='module')
def browser(request):
    b = Browser('chrome')
    request.addfinalizer(b.quit)
    return b

