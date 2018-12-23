from aiolambda import logger
from aiolambda.app import get_app

from auth.db import init_db
from auth.mq import init_mq


def main():
    app = get_app(init_db=init_db, init_mq=init_mq)
    app.run(port=8080, access_log=logger.access_logger)
