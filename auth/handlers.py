from aiohttp.web import Response
from aiolambda import logger
from aiolambda.functools import compose

from auth.db import create_user
from auth.response import return_200, return_201
from auth.token import create_token
from auth.user import to_dict
from auth.verify import check_password


async def auth_handler(*_null, **request) -> Response:
    return await compose(
        check_password,
        logger.debug,
        create_token,
        logger.debug,
        return_201
    )(request)


async def create_user_handler(*_null, **request) -> Response:
    return await compose(
        create_user,
        logger.debug,
        to_dict,
        return_201
    )(request)


async def ping_handler() -> Response:
    return compose(
        logger.debug,
        return_200)('pong')
