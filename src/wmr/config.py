import os

import inject


def config(binder):
    from wmr.players import START_RANK
    binder.bind('database_url', os.environ['RANK_DATABASE_URL'])
    binder.bind('start_rank', START_RANK)


inject.configure(config)
