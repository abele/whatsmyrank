import inject
from pyramid.renderers import render_to_response

from .players import PlayerRepository


def list_ranks(request):
    player_repo = inject.instance(PlayerRepository)
    score_list = player_repo.scores()
    return render_to_response(
        'ranks.jinja2',
        {'score_list': score_list},
        request,
    )
