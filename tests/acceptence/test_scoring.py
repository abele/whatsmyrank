import sys
import os
import signal

import py
import pytest
from splinter.browser import Browser


@pytest.fixture(scope='session')
def test_server(xprocess, request):
    def preparefunc(cwd):
        server_mod = py.path.local('src/whatsmyrank/web.py')
        return ('started', [sys.executable, server_mod])

    pid, log = xprocess.ensure('server', preparefunc)
    print(pid)

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


class ScoringApp(object):
    def __init__(self, browser, get_url):
        self._browser = browser
        self._get_url = get_url

    def visit(self, url):
        self._browser.visit(self._get_url(url))

    def shows(self, text):
        assert self._browser.is_text_present(text)

    def add_player(self, name):
        self._browser.fill('player-name', name)
        self._browser.find_by_id('submit').click()


def test_shows_player_rating(browser, test_server):
    app = ScoringApp(browser, test_server)
    app.visit('/')
    app.shows('P1 1000')


def test_user_adding(browser, test_server):
    app = ScoringApp(browser, test_server)
    app.visit('/players')
    app.add_player('test')
    app.is_in_page('/players/test')
    app.shows('test')
