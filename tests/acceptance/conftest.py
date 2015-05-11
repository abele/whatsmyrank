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


@pytest.fixture(scope='session', autouse=True)
def setup_test_environment(database_url, server_port):
    """Pass test environment to application configuration."""
    os.environ['RANK_DATABASE_URL'] = database_url
    os.environ['PORT'] = str(server_port)


@pytest.fixture(scope='session')
def database_url():
    return str(py.path.local('test.shelve'))


@pytest.fixture(scope='session')
def server_port():
    return 8081


@pytest.fixture(scope='session')
def server(xprocess, request, database_url, server_port):
    pid, log = xprocess.ensure('server', lambda cwd: ('started', ['wmr']))
    request.addfinalizer(lambda: os.kill(pid, signal.SIGKILL))
    return lambda url: 'http://localhost:{}{}'.format(server_port, url)


@pytest.fixture(scope='module')
def browser(request):
    b = Browser('chrome')
    request.addfinalizer(b.quit)
    return b
