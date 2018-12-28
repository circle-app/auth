from aio_pika import Channel, DeliveryMode, Message
from aiolambda import logger
from aiolambda.functools import bind
from aiolambda.typing import Maybe
from typing import Callable, Dict, Optional

from auth.user import User


@bind
async def send_create_user_message(channel: Channel, user: Maybe[User]) -> Maybe[User]:
    if isinstance(user, Exception):
        return user
    logger.debug(f'Publish {user.username} in create_user route')
    await channel.default_exchange.publish(
        Message(user.username.encode(), delivery_mode=DeliveryMode.PERSISTENT),
        'create_user')
    return user


init_mq: Optional[Dict[str, Callable]] = {}
