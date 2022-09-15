from contextlib import asynccontextmanager, contextmanager
from contextvars import ContextVar
from inspect import signature

import aiohttp
from funcy import compact, compose, decorator, merge, project

from response import Response


SETTINGS = ContextVar('settings', default={})


SESSION_PARAMS = [
    p.name for p in signature(aiohttp.ClientSession).parameters.values()
    if p.kind == p.KEYWORD_ONLY
]


@contextmanager
def settings(**values):
    try:
        with_settings.cache = {}
        token = SETTINGS.set(values)
        yield
    finally:
        SETTINGS.reset(token)


settings.get = lambda param, default=None: SETTINGS.get().get(param, default)


@decorator
def with_settings(call):
    middleware = settings.get('middleware', [])
    try:
        composed = with_settings.cache['middleware']
    except KeyError:
        composed = with_settings.cache['middleware'] = compose(*middleware)(call._func)
    try:
        default_session_params = with_settings.cache['default_session_params']
    except KeyError:
        default_session_params = project(SETTINGS.get(), SESSION_PARAMS)
        with_settings.cache['default_session_params'] = default_session_params

    call._kwargs['session_params'] = compact(merge(
        default_session_params, 
        call._kwargs.get('session_params', {})
    ))
    return composed(*call._args, **call._kwargs)


with_settings.cache = {}


@with_settings
async def fetch(url, *, method='get', headers=None, session_params=None, **request_params):
    session_params = session_params or {}
    headers = compact(merge(settings.get('headers') or {}, headers or {}))
    
    async with aiohttp.ClientSession(**session_params) as session:
        async with session.request(method=method, url=url, headers=headers, **request_params) as response:
            body = await response.text()
            return Response(
                method=response.method, url=str(response.url), body=body,
                status=response.status, reason=response.reason,
                headers=dict(response.headers)
            )
