import asyncpg
import passlib.hash

from aiolambda import logger
from aiolambda.db import _check_table_exists
from aiolambda.errors import ObjectAlreadyExists, ObjectNotFound
from aiolambda.functools import bind
from aiolambda.typing import Maybe

from auth.config import ADMIN_USER, ADMIN_PASSWORD
from auth.user import User

USERS_TABLE_NAME = 'users'


@bind
async def create_user(pool: asyncpg.pool, user: User) -> Maybe[User]:
    async with pool.acquire() as conn:
        try:
            await conn.execute(f'''
                INSERT INTO {USERS_TABLE_NAME}(username, password, scope) VALUES($1, $2, $3)
            ''', user.username, passlib.hash.pbkdf2_sha256.hash(user.password), user.scope)
        except asyncpg.exceptions.UniqueViolationError:
            return ObjectAlreadyExists()
    return user


async def init_db(pool: asyncpg.pool) -> None:
    if await _check_table_exists(pool, USERS_TABLE_NAME):
        logger.info('Already initializated.')
        return

    logger.info(f'Create table: {USERS_TABLE_NAME}')
    async with pool.acquire() as conn:
        await conn.execute(f'''
            CREATE TABLE {USERS_TABLE_NAME}(
                username text PRIMARY KEY,
                password text,
                scope text
            )
        ''')

    logger.info(f'Create admin user')
    await create_user(pool, User(ADMIN_USER, ADMIN_PASSWORD, 'admin'))


@bind
async def update_user(pool: asyncpg.pool, user: User) -> Maybe[User]:
    async with pool.acquire() as conn:
        await conn.execute(f'''
            UPDATE {USERS_TABLE_NAME} SET password = $2, scope = $3 WHERE username = $1
        ''', user.username, passlib.hash.pbkdf2_sha256.hash(user.password), user.scope)
    return user


@bind
async def delete_user(pool: asyncpg.pool, username: str) -> Maybe[str]:
    async with pool.acquire() as conn:
        res = await conn.execute(f'''
            DELETE FROM {USERS_TABLE_NAME} WHERE username = $1
        ''', username)
    if res == 'DELETE 0':
        return ObjectNotFound()
    return username


@bind
async def get_user(pool: asyncpg.pool, username: str) -> Maybe[User]:
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            f'SELECT * FROM {USERS_TABLE_NAME} WHERE username = $1', username)

    if not row:
        return ObjectNotFound()
    return User(**dict(row))


@bind
async def update_password(pool: asyncpg.pool,
                          username: str, password: str) -> Maybe[str]:
    async with pool.acquire() as connection:
        res = await connection.execute(f'''
            UPDATE {USERS_TABLE_NAME} SET password = $2 WHERE username = $1
        ''', username, passlib.hash.pbkdf2_sha256.hash(password))
    if res != 'UPDATE 1':
        return Exception()
    return password
