import os
import shelve


class PlayerRepository(object):
    def __init__(self, database_url):
        self._url = database_url

    def scores(self):
        with shelve.open(self._url) as db:
            _scores = [key.upper() + ' ' + str(db[key]) + '\n' for key in db]

        return _scores

    def create(self, name):
        with shelve.open(self._url) as db:
            db[name] = 1000

    def score(self, name):
        with shelve.open(self._url) as db:
            player_score = name.upper() + ' ' + str(db[name])

        return player_score
