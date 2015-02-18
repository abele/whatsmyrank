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

