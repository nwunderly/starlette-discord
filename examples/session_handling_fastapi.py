"""
A basic FastAPI app that demonstrates "login with Discord".

It also saves the user's login session, so any subsequent visits to /dash
will return the same data without requiring re-authorization.
"""

import secrets

import uvicorn
from fastapi import FastAPI
from starlette.exceptions import HTTPException
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse

from starlette_discord.client import DiscordOAuthClient

CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
REDIRECT_URI = "YOUR_REDIRECT_URI"


app = FastAPI()
client = DiscordOAuthClient(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)


@app.get("/login")
async def login_with_discord():
    return client.redirect()


# NOTE: REDIRECT_URI should be this path.
@app.get("/callback")
async def callback(request: Request, code: str):
    user = await client.login(code)
    request.session["discord_user"] = user
    return RedirectResponse("/dash")


@app.get("/dash")
async def dash(request: Request):
    # raise 401-Unauthorized if user isn't logged in
    user = request.session.get("discord_user")
    if not user:
        raise HTTPException(401)

    return user.json()


app.add_middleware(SessionMiddleware, secret_key=secrets.token_urlsafe(64))
uvicorn.run(app)
