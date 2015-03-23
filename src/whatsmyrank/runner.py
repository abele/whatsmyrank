import logging
import os
import sys
from wsgiref.simple_server import make_server

from .web import app

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def main():
    LOGGER.info('ENVIRONMENT=%s',
                {key: os.environ[key] for key in os.environ
                 if key.startswith('RANK_')})

    port = int(os.environ.get('PORT', 8080))

    sys.stderr.write("started\n")
    sys.stderr.flush()

    server = make_server('127.0.0.1', port, app)
    server.serve_forever()


if __name__ == '__main__':
    sys.exit(main())
