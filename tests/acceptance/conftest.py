import os
import shelve
import signal
import sys

import py
import pytest
from splinter.browser import Browser


@pytest.fixture(scope='function', autouse=True)
def clear_database(database_url):
    with shelve.open(database_url) as db:
        db.clear()


@pytest.fixture(scope='session')
def database_url():
    return str(py.path.local('test.shelve'))


@pytest.fixture(scope='session')
def test_server(xprocess, request, database_url):
    port = 8081

    def preparefunc(cwd):
        os.environ['RANK_DATABASE_URL'] = database_url
        os.environ['PORT'] = str(port)

        return ('started', ['whatsmyrank'])

    pid, log = xprocess.ensure('server', preparefunc)

    def fin():
        os.kill(pid, signal.SIGKILL)

    request.addfinalizer(fin)

    def get_url(url):
        return 'http://localhost:{}{}'.format(port, url)

    return get_url


@pytest.fixture(scope='module')
def browser(request):
    b = Browser('chrome')
    request.addfinalizer(b.quit)
    return b
