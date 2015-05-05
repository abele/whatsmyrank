import os
import shelve
import sys
from wsgiref.simple_server import make_server

import pyramid.httpexceptions as exc
from pyramid.config import Configurator
from pyramid.renderers import render_to_response
from pyramid.response import Response

from wmr.config import inject
from wmr.players import PlayerRepository
from wmr.tournament import TournamentRepository

PLAYER_REPO = inject.instance(PlayerRepository)
TOURNAMENT_REPO = inject.instance(TournamentRepository)


def ranks(request):
    score_list = PLAYER_REPO.scores()
    return render_to_response(
        'ranks.jinja2',
        {'score_list': score_list},
        request,
    )


def players(request):
    return render_to_response('players.jinja2', {}, request)


def create_player(request):
    name = request.POST['player-name']
    PLAYER_REPO.create(name)
    raise exc.HTTPFound(request.route_url('player', player=name))


def view_player(request):
    name = request.matchdict['player']
    player_score = PLAYER_REPO.score(name)
    return Response(player_score)


def games(request):
    return render_to_response('game_form.jinja2', {}, request)


def add_games(request):
    player1 = request.POST['player1']
    player2 = request.POST['player2']
    games = request.POST['games']
    for game in games.split():
        p1, p2 = map(int, game.split('/'))
        winner = player1 if p1 > p2 else player2
        PLAYER_REPO.create(player1)
        PLAYER_REPO.create(player2)
        PLAYER_REPO.add_win(winner, 1)

    raise exc.HTTPFound(request.route_url('ranks'))


def tournaments(request):
    return render_to_response('tournament_form.jinja2', {}, request)


def add_tournament(request):
    name = request.POST['name']
    pk = TOURNAMENT_REPO.add(name)
    raise exc.HTTPFound(request.route_url('tournament', pk=pk))


def view_tournament(request):
    pk = request.matchdict['pk']
    tour = TOURNAMENT_REPO.get(pk)
    context = {
        'name': tour['name'],
        'player_score_seq': (PLAYER_REPO.score(pk)
                             for pk in tour['player_list'])
    }
    return render_to_response(
        'tournament.jinja2',
        context,
        request
    )

def add_tournament_score(request):
    pk = request.matchdict['pk']

    player1 = request.POST['player1']
    player2 = request.POST['player2']
    games = request.POST['games']
    for game in games.split():
        p1, p2 = map(int, game.split('/'))
        winner = player1 if p1 > p2 else player2
        PLAYER_REPO.create(player1)
        PLAYER_REPO.create(player2)
        PLAYER_REPO.add_win(winner, 1)

    TOURNAMENT_REPO.add_player(pk, [player1, player2])
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
config.add_jinja2_search_path('wmr:templates')

app = config.make_wsgi_app()
