import logging

import uvicorn
from starlette.requests import Request

from auth import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SECRET_KEY
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from starlette_discord.client import DiscordOAuthClient

logging.basicConfig(level=logging.DEBUG)

app = FastAPI()
client = DiscordOAuthClient(
    CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, scopes=("identify", "guilds")
)

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)


@app.get("/login")
async def login_with_discord(request: Request):
    print(request.session, 'before')
    request.session.clear()
    return client.redirect(prompt="none")


@app.get("/callback")
async def callback(code: str, request: Request):
    async with client.session(code) as session:
        user = await session.identify()
        print(session.token)  # at this point you can get the user's access token
        # save the token
        request.session["token"] = session.token
    return {"user": str(user)}


@app.get("/guilds")
async def get_guilds(request: Request):
    # get the token from the session
    token = request.session["token"]
    
    async with client.session_from_token(token) as session:
        # TOKEN is the 'access_token' string or the whole dict obtained in previous login
        guilds = await session.guilds()
        
        if request.session['token'] != session.token:  # if the session refreshed you want to change the stored token,
            request.session['token'] = session.token   # otherwise you'll get an error if you try to use the old token.
    return {"guilds": [str(g) for g in guilds]}


uvicorn.run(app, host="0.0.0.0", port=9000)
