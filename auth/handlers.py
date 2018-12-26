from aiohttp.web import Response
from aiolambda import logger
from aiolambda.functools import compose

from auth.db import create_user, delete_user, get_user, update_user, update_password
from auth.mq import send_create_user_message
from auth.response import return_200, return_201, return_204
from auth.token import generate_token
from auth.user import to_dict
from auth.verify import check_password, verify_username


async def auth_handler(*_null, **extra_args) -> Response:
    return await compose(
        check_password,
        logger.debug,
        generate_token,
        logger.debug,
        return_201
    )(extra_args['request'])


async def create_user_handler(*_null, **extra_args) -> Response:
    return await compose(
        create_user,
        send_create_user_message(extra_args['request']),
        to_dict,
        return_201
    )(extra_args['request'])


async def get_user_handler(username, **extra_args) -> Response:
    return await compose(
        get_user,
        to_dict,
        return_200
    )(extra_args['request'], username)


async def update_user_handler(username, **extra_args) -> Response:
    return await compose(
        verify_username,
        update_user,
        to_dict,
        return_204
    )(extra_args['request'], username)


async def delete_user_handler(username, **extra_args) -> Response:
    return await compose(
        delete_user,
        to_dict,
        return_204
    )(extra_args['request'], username)


async def update_password_handler(*_null, **extra_args) -> Response:
    return await compose(
        update_password,
        return_204
    )(extra_args['request'])


async def ping_handler() -> Response:
    return compose(
        logger.debug,
        return_200)('pong')
