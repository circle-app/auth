import asyncpg
import passlib

from aiolambda.functools import bind
from aiolambda.typing import Maybe

from auth.db import get_user
from auth.errors import InvalidCredentials, IdCheckError
from auth.user import User


@bind
async def check_password(db_pool: asyncpg.pool, username: str, password: str) -> Maybe[User]:
    user_data = await get_user(db_pool, username)
    if isinstance(user_data, Exception):
        return user_data

    user_request = User(username, password)
    is_verified = passlib.hash.pbkdf2_sha256.verify(user_request.password, user_data.password)
    if not is_verified:
        return InvalidCredentials()

    return user_data


@bind
async def verify_username(user_request: User, username: str) -> Maybe[User]:
    if user_request.username != username:
        return IdCheckError()
    return user_request
