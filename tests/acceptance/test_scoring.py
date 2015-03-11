import shelve

import pytest

from whatsmyrank.players import START_RANK
from whatsmyrank.players import PlayerRepository


@pytest.fixture
def app(browser, test_server):
    return ScoringApp(browser, test_server)


def test_shows_player_rating(app, database_url):
    player_repo = PlayerRepository(database_url, START_RANK)
    player_repo.create('p1')

    app.visit('/ranks')
    app.shows('P1 1000')


def test_user_adding(app):
    app.visit('/players')
    app.add_player('test')
    app.is_in_page('/players/test')
    app.shows('TEST 1000')


def test_can_add_game_scores(app):
    app.visit('/players')
    app.add_player('p1')

    app.visit('/')
    app.enter_games('p1', 'p2', '11/2 11/3 11/8')
    app.is_in_page('/ranks')
    app.visit('/players/p1')
    app.shows('P1 1003')


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

    def is_in_page(self, url):
        assert self._browser.url == self._get_url(url)

    def enter_games(self, p1, p2, game_seq_str):
        self._browser.fill('player1', p1)
        self._browser.fill('player2', p2)
        self._browser.fill('games', game_seq_str)
        self._browser.find_by_id('submit').click()
