import os
import shelve
from operator import itemgetter

START_RANK = 1000


class PlayerRepository(object):
    def __init__(self, database_url, start_rank):
        self._url = database_url
        self._start_rank = start_rank

    def scores(self):
        with shelve.open(self._url) as db:
            _scores = [(key, db[key]) for key in db]

        return sorted(_scores, key=itemgetter(1), reverse=True)

    def create(self, name):
        with shelve.open(self._url) as db:
            if name not in db:
                db[name] = self._start_rank
            else:
                pass

    def score(self, name):
        with shelve.open(self._url) as db:
            player_score = name.upper() + ' ' + str(db[name])

        return player_score

    def add_win(self, name, count):
        with shelve.open(self._url) as db:
            if name not in db:
                db[name] = self._start_rank + count
            else:
                db[name] += count
