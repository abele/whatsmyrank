import logging
import os
import shelve
import sys
from wsgiref.simple_server import make_server

import pyramid.httpexceptions as exc
from pyramid.config import Configurator
from pyramid.renderers import render_to_response
from pyramid.response import Response

from whatsmyrank.players import START_RANK
from whatsmyrank.players import PlayerRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.environ['RANK_DATABASE_URL']

player_repo = PlayerRepository(DATABASE_URL, START_RANK)


def ranks(request):
    score_list = player_repo.scores()
    return render_to_response(
        'ranks.jinja2', 
        {'score_list': score_list}, 
        request,
    )


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


def games(request):
    content = """
    <form action="" method="POST">
        <div>
        <label for="player1">Player 1</label>
        <input id="player1" type="text" name="player1">
        </div>
        <div>
        <label for="player2">Player 2</label>
        <input id="player2" type="text" name="player2">
        </div>
        <div>
        <label for="games">Games</label>
        <textarea id="games" name="games" rows="3"></textarea>
        </div>
        <div>
        <input id="submit" type="submit" value="Submit">
        </div>
    </form>
    """

    return Response(content)


def add_games(request):
    player1 = request.POST['player1']
    player2 = request.POST['player2']
    games = request.POST['games']
    for game in games.split():
        p1, p2 = map(int, game.split('/'))
        player = player1 if p1 > p2 else player2
        player_repo.add_win(player, 1)
        print(player, p1, p2)

    raise exc.HTTPFound(request.route_url('ranks'))


config = Configurator()
config.add_route('ranks', 'ranks')
config.add_view(ranks, route_name='ranks')

config.add_route('players', '/players')
config.add_view(players, route_name='players', request_method='GET')
config.add_view(create_player, route_name='players', request_method='POST')

config.add_route('player', '/players/{player}')
config.add_view(view_player, route_name='player')

config.add_route('games', '/')
config.add_view(games, route_name='games', request_method='GET')
config.add_view(add_games, route_name='games', request_method='POST')

config.include('pyramid_jinja2')
config.add_jinja2_search_path('whatsmyrank:templates')

app = config.make_wsgi_app()


if __name__ == '__main__':
    logger.info('ENVIRONMENT=%s',
                {key: os.environ[key] for key in os.environ
                 if key.startswith('RANK_')})
    port = int(os.environ.get('PORT', 8080))
    sys.stderr.write("started\n")
    sys.stderr.flush()

    server = make_server('127.0.0.1', port, app)
    server.serve_forever()
