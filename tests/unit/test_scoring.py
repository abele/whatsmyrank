from wmr.players import START_RANK
from wmr.players import PlayerRepository


def test_default_starting_rank_is_1000():
    assert START_RANK == 1000


# XXX: we shouldn't have DB in unittests
def test_all_players_start_with_starting_rank(database_url):
    player_name = 'some-player'
    player_repo = PlayerRepository(database_url, START_RANK)
    player_repo.create(player_name)
    assert player_repo.score(player_name) == 'SOME-PLAYER 1000'


def test_returns_ranks_sorted_descending(database_url):
    player_1 = 'player 1'
    player_2 = 'player 2'
    player_repo = PlayerRepository(database_url, START_RANK)
    player_repo.create(player_2)
    player_repo.create(player_1)
    player_repo.add_win(player_1, 1)

    assert player_repo.scores() == [
        (player_1, START_RANK + 1),
        (player_2, START_RANK)
    ]
