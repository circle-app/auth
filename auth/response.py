from aiohttp.web import Response, json_response

from aiolambda.errors import ObjectAlreadyExists, ObjectNotFound
from aiolambda.typing import Maybe

from auth.errors import InvalidCredentials, IdCheckError


def return_error(error: Exception) -> Response:
    if isinstance(error, InvalidCredentials):
        return json_response('Invalid credentials', status=422)
    if isinstance(error, IdCheckError):
        return json_response('Id in body and url params does not match', status=422)
    if isinstance(error, ObjectAlreadyExists):
        return json_response('User already exists', status=409)
    if isinstance(error, ObjectNotFound):
        return json_response('Object not found', status=404)
    return json_response('Unknow error', status=500)


def return_200(maybe_json: Maybe[dict]) -> Response:
    if isinstance(maybe_json, Exception):
        return return_error(maybe_json)
    return json_response(maybe_json, status=200)


def return_201(maybe_json: Maybe[dict]) -> Response:
    if isinstance(maybe_json, Exception):
        return return_error(maybe_json)
    return json_response(maybe_json, status=201)


def return_204(maybe_json: Maybe[dict]) -> Response:
    if isinstance(maybe_json, Exception):
        return return_error(maybe_json)
    return json_response('successful operation', status=204)
