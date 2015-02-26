import logging
import os
import shelve
import sys
from wsgiref.simple_server import make_server

import pyramid.httpexceptions as exc
from pyramid.config import Configurator
from pyramid.response import Response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.environ['QUEST_DATABASE_URL']

class PlayerRepository(object):
    def __init__(self, database_url):
        self._url = database_url

    def scores(self):
        with shelve.open(self._url) as db:
            _scores = [key.upper() + ' ' + str(db[key]) + '\n'
                       for key in db]

        return _scores

    def create(self, name):
        with shelve.open(self._url) as db:
            db[name] = 1000

    def score(self, name):
        with shelve.open(DATABASE_URL) as db:
            player_score = name.upper() + ' ' + str(db[name])

        return player_score



player_repo = PlayerRepository(DATABASE_URL)


def home(request):
    score_list = player_repo.scores()
    return Response(str(score_list))


def players(request):
    content = """
    <form action="" method="POST">
        <input id="player-name" type="text" name="player-name">
        <input id="submit" type="submit" value="Create">
    </form>
    """

    return Response(content) 


def create_player(request):
    name = request.POST['player-name']
    player_repo.create(name)
    raise exc.HTTPFound(request.route_url('player', player=name))


def view_player(request):
    name = request.matchdict['player']
    player_score = player_repo.score(name)
    return Response(player_score)


config = Configurator()
config.add_route('home', '/')
config.add_view(home, route_name='home')

config.add_route('players', '/players')
config.add_view(players, route_name='players', request_method='GET')
config.add_view(create_player, route_name='players', request_method='POST')

config.add_route('player', '/players/{player}')
config.add_view(view_player, route_name='player')

app = config.make_wsgi_app()


if __name__ == '__main__':
    logger.info('ENVIRONMENT=%s',
                {key: os.environ[key] for key in os.environ
                 if key.startswith('QUEST_')})
    sys.stderr.write("started\n")
    sys.stderr.flush()

    server = make_server('127.0.0.1', 8080, app)
    server.serve_forever()
