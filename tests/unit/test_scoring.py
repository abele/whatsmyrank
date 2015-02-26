from whatsmyrank.players import START_RANK
from whatsmyrank.players import PlayerRepository


def test_default_starting_rank_is_1000():
    assert START_RANK == 1000


# XXX: we shouldn't have DB in unittests
def test_all_players_start_with_starting_rank(database_url):
    player_name = 'some-player'
    player_repo = PlayerRepository(database_url, START_RANK)
    player_repo.create(player_name)
    assert player_repo.score(player_name) == 'SOME-PLAYER 1000' 
