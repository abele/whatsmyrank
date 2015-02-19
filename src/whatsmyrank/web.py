import shelve
import sys
from wsgiref.simple_server import make_server

import pyramid.httpexceptions as exc
from pyramid.config import Configurator
from pyramid.response import Response

DB_NAME = 'score_set'


with shelve.open(DB_NAME) as db:
    db['p1'] = 1000
    db['p2'] = 2000


def home(request):
    with shelve.open(DB_NAME) as db:
        for key in db:
            p1_score = key.upper() + " " + str(db[key])

    return Response(str(p1_score))


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

    with shelve.open(DB_NAME) as db:
        db[name] = 1000

    raise exc.HTTPFound('/players/test')


def view_player(request):
    name = request.matchdict['player']

    with shelve.open(DB_NAME) as db:
        player_score = name.upper() + ' ' + str(db[name])

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
    sys.stderr.write("started\n")
    sys.stderr.flush()

    server = make_server('127.0.0.1', 8080, app)
    server.serve_forever()
