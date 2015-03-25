import shelve
import uuid


class TournamentRepository(object):
    def __init__(self, database_url):
        self._url = database_url

    def add(self, name):
        with shelve.open(self._url) as db:
            pk = uuid.uuid4().hex
            db[pk] = {
                'name': name,
                'player_list': [],
            }

        return pk

    def get(self, pk):
        with shelve.open(self._url) as db:
            tour = db[pk]

        return tour

    def add_player(self, pk, player_list):
        with shelve.open(self._url) as db:
            tour = db[pk]
            tour['player_list'] = list(set(tour['player_list']) | set(player_list))
            db[pk] = tour

        return tour
