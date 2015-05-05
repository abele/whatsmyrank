

def ranks(request):
    score_list = PLAYER_REPO.scores()
    return render_to_response(
        'ranks.jinja2',
        {'score_list': score_list},
        request,
    )

