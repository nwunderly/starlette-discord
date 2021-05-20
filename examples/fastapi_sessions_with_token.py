import logging
import secrets
from typing import Dict

import uvicorn
from fastapi import FastAPI
from starlette.exceptions import HTTPException
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse

from starlette_discord.client import DiscordOAuthClient

from auth import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI

logging.basicConfig(level=logging.DEBUG)

app = FastAPI()
client = DiscordOAuthClient(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, scopes=('identify', 'guilds'))

token_cache: Dict[int, dict] = dict()


@app.get('/login')
async def start_login(request: Request):
    state = secrets.token_urlsafe(32)
    request.session['state'] = state
    return client.redirect(state=state, prompt='none')


@app.get('/callback')
async def callback(request: Request, code: str, state: str):
    if not state == request.session.get('state'):
        raise HTTPException(401)

    user, token = await client.login(code, return_token=True)
    request.session['user'] = user
    token_cache[int(user['id'])] = token

    if url_redirect := request.session.pop('url_redirect', None):
        return RedirectResponse(url_redirect)
    else:
        return user


@app.get('/guilds')
async def get_guilds(request: Request):
    if (user := request.session.get('user')) and (user_id := int(user['id'])) in token_cache:
        token = token_cache[user_id]
        async with client.session_from_token(token) as session:
            guilds = await session.guilds()
        return guilds
    else:
        request.session['url_redirect'] = '/guilds'
        return RedirectResponse('/login')


app.add_middleware(SessionMiddleware, secret_key=secrets.token_urlsafe(64))

uvicorn.run(app)
