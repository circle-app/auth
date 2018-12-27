from jose import jwt

from aiolambda.config import JWT_ALGORITHM, JWT_ISSUER, JWT_LIFETIME_SECONDS, JWT_PRIVATE_KEY
from aiolambda.functools import bind
from aiolambda.typing import Maybe

from auth.user import User
from auth.utils import current_timestamp
from auth.errors import JWTEncodeError


@bind
def generate_token(user: User) -> Maybe[dict]:
    timestamp = current_timestamp()
    payload = {
        "iss": JWT_ISSUER,
        "iat": int(timestamp),
        "exp": int(timestamp + JWT_LIFETIME_SECONDS),
        "sub": str(user.username),
        "scope": str(user.scope),
    }
    try:
        token = jwt.encode(payload, JWT_PRIVATE_KEY, algorithm=JWT_ALGORITHM)
    except Exception:
        return JWTEncodeError()
    return {"access_token": token,
            "token_type": "bearer",
            "expires_in": int(timestamp + JWT_LIFETIME_SECONDS),
            "scope": str(user.scope)}
