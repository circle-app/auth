import pytest

from aiolambda.app import get_app

from auth.db import init_db

BASE_URL = "/v1"


@pytest.fixture
def cli(loop, aiohttp_client):
    app = get_app(init_db)
    return loop.run_until_complete(aiohttp_client(app.app))


async def get_token(cli) -> str:
    auth_resp = await cli.post(f'{BASE_URL}/auth', json={'username': 'admin', 'password': 'admin'})
    token = str(await auth_resp.json())
    return token


async def test_auth(cli):
    resp = await cli.post(f'{BASE_URL}/auth', json={'username': 'admin', 'password': 'admin'})
    assert resp.status == 201
    token_start = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJhaW9sYW1iZGEiLC'
    token = str(await resp.json())
    assert token.startswith(f'{token_start}')


async def test_auth_incorret_user(cli):
    resp = await cli.post(f'{BASE_URL}/auth', json={'username': 'foo', 'password': 'foo'})
    assert resp.status == 422
    assert await resp.json() == 'Invalid credentials'


async def test_auth_incorret_password(cli):
    resp = await cli.post(f'{BASE_URL}/auth', json={'username': 'admin', 'password': 'foo'})
    assert resp.status == 422
    assert await resp.json() == 'Invalid credentials'


async def test_user_add(cli):
    token = await get_token(cli)
    auth_header = {'Authorization': f'Bearer {token}'}
    user = {'username': 'test2', 'password': 'test1234', 'scope': 'user'}
    resp = await cli.post(f'{BASE_URL}/user', json=user, headers=auth_header)
    assert resp.status == 201
    assert await resp.json() == user


async def test_user_add_exist_user(cli):
    token = await get_token(cli)
    auth_header = {'Authorization': f'Bearer {token}'}
    user = {'username': 'admin', 'password': 'test1234'}
    resp = await cli.post(f'{BASE_URL}/user', json=user, headers=auth_header)
    assert resp.status == 409
    assert await resp.json() == 'User already exists'


async def test_user_add_permission_deny(cli):
    auth_resp = await cli.post(f'{BASE_URL}/auth',
                               json={'username': 'test2', 'password': 'test1234'})
    token = str(await auth_resp.json())
    auth_header = {'Authorization': f'Bearer {token}'}
    resp = await cli.post(f'{BASE_URL}/user',
                          headers=auth_header)
    assert resp.status == 403


async def test_user_add_body_validation(cli):
    token = await get_token(cli)
    auth_header = {'Authorization': f'Bearer {token}'}
    user = {'username': 'boo'}
    resp = await cli.post(f'{BASE_URL}/user', json=user, headers=auth_header)
    assert resp.status == 400


async def test_ping(cli):
    resp = await cli.get(f'{BASE_URL}/ping')
    assert resp.status == 200
    assert await resp.json() == 'pong'
