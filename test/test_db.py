import asyncpg
import pytest

from aiolambda.config import (POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER,
                              POSTGRES_PASSWORD)

from auth.db import init_db


@pytest.fixture
async def pool(loop):
    pool = await asyncpg.create_pool(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD)
    async with pool.acquire() as connection:
        await init_db(connection)
    return pool


async def count_rows(conn: asyncpg.connect, table: str):
    r = await conn.fetchrow(f'SELECT COUNT(*) FROM {table}')
    return r['count']
