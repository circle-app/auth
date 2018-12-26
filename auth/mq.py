from aio_pika import DeliveryMode, Message
from aiohttp.web import Request
from aiolambda import logger
from aiolambda.functools import Maybe
from toolz import curry
from typing import Callable, Dict, Optional

from auth.user import User


@curry
async def send_create_user_message(request: Request, user: Maybe[User]) -> Maybe[User]:
    if isinstance(user, Exception):
        return user
    logger.debug(f'Publish {user.username} in create_user route')
    await request.app['mq']['channel'].default_exchange.publish(
        Message(user.username.encode(), delivery_mode=DeliveryMode.PERSISTENT),
        'create_user')
    return user


init_mq: Optional[Dict[str, Callable]] = {}
