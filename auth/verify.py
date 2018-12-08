import aiohttp
import passlib

from auth.db import get_user
from auth.user import User
from auth.typing import Maybe, Error


async def check_password(request: aiohttp.web.Request) -> Maybe[User]:
    user_data = await get_user(request)
    if isinstance(user_data, Error):
        return user_data

    user_request = User(**(await request.json()))
    is_verified = passlib.hash.pbkdf2_sha256.verify(user_request.password, user_data.password)
    if not is_verified:
        return Error("'password does not match'", 422)

    return user_request