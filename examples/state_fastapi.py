"""
A basic FastAPI app that demonstrates "login with Discord".

This example uses an additional state for added security. Read about the state option here:
https://discord.com/developers/docs/topics/oauth2#state-and-security
"""

import secrets
import uvicorn
from fastapi import FastAPI
from starlette.requests import Request
from starlette.exceptions import HTTPException
from starlette.middleware.sessions import SessionMiddleware
from starlette_discord.client import DiscordOAuthClient


CLIENT_ID = 'YOUR_CLIENT_ID'
CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
REDIRECT_URI = 'YOUR_REDIRECT_URI'


app = FastAPI()
client = DiscordOAuthClient(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)


@app.get('/login')
async def login_with_discord(request: Request):
    state = secrets.token_urlsafe(32)
    request.session['state'] = state
    return client.redirect(state=state, prompt='none')


@app.get('/callback')
async def callback(request: Request, code: str, state: str):
    # raise 401-Unauthorized if state doesn't match
    if not state == request.session.get('state'):
        raise HTTPException(401)

    user = await client.login(code)
    return user.json()


app.add_middleware(SessionMiddleware, secret_key=secrets.token_urlsafe(64))
uvicorn.run(app)
