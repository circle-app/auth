import asyncpg
import passlib.hash

from aiohttp.web import Request
from aiolambda import logger
from aiolambda.db import _check_table_exists
from aiolambda.errors import ObjectAlreadyExists, ObjectNotFound
from aiolambda.functools import Maybe
from toolz import curry
from typing import Callable

from auth.config import ADMIN_USER, ADMIN_PASSWORD
from auth.user import User

USERS_TABLE_NAME = 'users'


async def _create_user(conn: asyncpg.connect, user: User) -> Maybe[User]:
    try:
        await conn.execute(f'''
            INSERT INTO {USERS_TABLE_NAME}(username, password, scope) VALUES($1, $2, $3)
        ''', user.username, passlib.hash.pbkdf2_sha256.hash(user.password), user.scope)
    except asyncpg.exceptions.UniqueViolationError:
        return ObjectAlreadyExists()
    return user


async def init_db(conn: asyncpg.connect) -> None:
    if await _check_table_exists(conn, USERS_TABLE_NAME):
        logger.info('Already initializated.')
        return

    logger.info(f'Create table: {USERS_TABLE_NAME}')
    await conn.execute(f'''
        CREATE TABLE {USERS_TABLE_NAME}(
            username text PRIMARY KEY,
            password text,
            scope text
        )
    ''')

    logger.info(f'Create admin user')
    await _create_user(conn, User(ADMIN_USER, ADMIN_PASSWORD, 'admin'))


@curry
async def _operate_user(operation: Callable, request: Request) -> Maybe[User]:
    pool = request.app['pool']
    user_request = User(**(await request.json()))

    async with pool.acquire() as connection:
        maybe_user = await operation(connection, user_request)
    return maybe_user


@_operate_user
async def create_user(conn: asyncpg.connect, user: User) -> Maybe[User]:
    return await _create_user(conn, user)


@_operate_user
async def update_user(conn: asyncpg.connect, user: User) -> Maybe[User]:
    await conn.execute(f'''
        UPDATE {USERS_TABLE_NAME} SET password = $2, scope = $3 WHERE username = $1
    ''', user.username, passlib.hash.pbkdf2_sha256.hash(user.password), user.scope)
    return user


@_operate_user
async def get_user(conn: asyncpg.connection, user: User) -> Maybe[User]:
    row = await conn.fetchrow(
        f'SELECT * FROM {USERS_TABLE_NAME} WHERE username = $1', user.username)

    if not row:
        return ObjectNotFound()
    return User(**dict(row))
