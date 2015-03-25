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
from whatsmyrank.tournament import TournamentRepository

DATABASE_URL = os.environ['RANK_DATABASE_URL']

player_repo = PlayerRepository(DATABASE_URL, START_RANK)
tournament_repo = TournamentRepository(DATABASE_URL)

GAME_FORM_HTML = """
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
    content = GAME_FORM_HTML
    return Response(content)


def add_games(request):
    player1 = request.POST['player1']
    player2 = request.POST['player2']
    games = request.POST['games']
    for game in games.split():
        p1, p2 = map(int, game.split('/'))
        winner = player1 if p1 > p2 else player2
        player_repo.create(player1)
        player_repo.create(player2)
        player_repo.add_win(winner, 1)

    raise exc.HTTPFound(request.route_url('ranks'))


def tournaments(request):
    content = """
    <form action="" method="POST">
        <div>
        <label for="name">Tournament Name</label>
        <input id="name" type="text" name="name">
        </div>
        <div>
        <input id="submit" type="submit" value="Submit">
        </div>
    </form>
    """

    return Response(content)


def add_tournament(request):
    name = request.POST['name']
    pk = tournament_repo.add(name)
    raise exc.HTTPFound(request.route_url('tournament', pk=pk))


def view_tournament(request):
    pk = request.matchdict['pk']
    tour = tournament_repo.get(pk)
    print(tour)
    content = ('<div>' + tour['name'] + '</div><div>' + GAME_FORM_HTML +
    '</div><ol>')
    for player_pk in tour['player_list']:
        player_score = player_repo.score(player_pk)
        content += '<li>' + player_score + '</li>'

    content += '</ol>'
    return Response(content)

def add_tournament_score(request):
    pk = request.matchdict['pk']

    player1 = request.POST['player1']
    player2 = request.POST['player2']
    games = request.POST['games']
    for game in games.split():
        p1, p2 = map(int, game.split('/'))
        winner = player1 if p1 > p2 else player2
        player_repo.create(player1)
        player_repo.create(player2)
        player_repo.add_win(winner, 1)

    tournament_repo.add_player(pk, [player1, player2])
    raise exc.HTTPFound(request.route_url('tournament', pk=pk))




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

config.add_route('tournaments', '/tournaments')
config.add_view(tournaments, route_name='tournaments', request_method='GET')
config.add_view(add_tournament, route_name='tournaments', request_method='POST')
config.add_route('tournament', '/tournaments/{pk}')
config.add_view(view_tournament, route_name='tournament', request_method='GET')

config.add_view(add_tournament_score, route_name='tournament',
        request_method='POST')

config.include('pyramid_jinja2')
config.add_jinja2_search_path('whatsmyrank:templates')

app = config.make_wsgi_app()
