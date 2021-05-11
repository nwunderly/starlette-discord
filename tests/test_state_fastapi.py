import secrets
import uvicorn
from fastapi import FastAPI
from starlette.requests import Request
from starlette.exceptions import HTTPException
from starlette.middleware.sessions import SessionMiddleware

from starlette_discord.client import DiscordOAuthClient
from auth import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI


app = FastAPI()
client = DiscordOAuthClient(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, scopes=('identify', 'guilds', 'email', 'connections'))


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

    async with client.session(code) as session:
        u = await session.identify()

    return {'user': u}


app.add_middleware(SessionMiddleware, secret_key=secrets.token_urlsafe(64))
uvicorn.run(app, host='0.0.0.0', port=9000)
