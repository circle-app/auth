from aiohttp.web import Response
from aiolambda import logger
from aiolambda.functools import compose

from auth.db import create_user, delete_user, get_user, update_user, update_password
from auth.mq import send_create_user_message
from auth.response import return_200, return_201, return_204
from auth.token import generate_token
from auth.user import to_dict, User
from auth.verify import check_password, verify_username


async def auth_handler(*_null, **extra_args) -> Response:
    return await compose(
        check_password(extra_args['request'].app['pool']),
        logger.debug,
        generate_token,
        logger.debug,
        return_201
    )(extra_args['token_info']['username'], extra_args['token_info']['password'])


async def create_user_handler(*_null, **extra_args) -> Response:
    return await compose(
        create_user(extra_args['request'].app['pool']),
        send_create_user_message(extra_args['request'].app['mq']['channel']),
        to_dict,
        return_201
    )(User(**(await extra_args['request'].json())))


async def get_user_handler(username, **extra_args) -> Response:
    return await compose(
        get_user(extra_args['request'].app['pool']),
        to_dict,
        return_200
    )(username)


async def update_user_handler(username, **extra_args) -> Response:
    return await compose(
        verify_username(User(**(await extra_args['request'].json()))),
        update_user(extra_args['request'].app['pool']),
        logger.error,
        to_dict,
        return_204
    )(username)


async def delete_user_handler(username, **extra_args) -> Response:
    return await compose(
        delete_user(extra_args['request'].app['pool']),
        return_204
    )(username)


async def update_password_handler(*_null, **extra_args) -> Response:
    return await compose(
        update_password(extra_args['request'].app['pool']),
        return_204
    )(extra_args['request']['user'], await extra_args['request'].json())


async def ping_handler() -> Response:
    return compose(
        logger.debug,
        return_200)('pong')
