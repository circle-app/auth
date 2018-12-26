import passlib

from aiohttp.web import Request
from aiolambda.typing import Maybe

from auth.db import get_user
from auth.errors import InvalidCredentials, IdCheckError
from auth.user import User


async def check_password(request: Request) -> Maybe[User]:
    user_data = await get_user(request)
    if isinstance(user_data, Exception):
        return user_data

    user_request = User(**(await request.json()))
    is_verified = passlib.hash.pbkdf2_sha256.verify(user_request.password, user_data.password)
    if not is_verified:
        return InvalidCredentials()

    return user_data


async def verify_username(request: Request, username: str) -> Maybe[Request]:
    user_request = User(**(await request.json()))
    if user_request.username != username:
        return IdCheckError()
    return request
