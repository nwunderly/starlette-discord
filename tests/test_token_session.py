import logging

import uvicorn
from auth import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, TOKEN
from fastapi import FastAPI

from starlette_discord.client import DiscordOAuthClient

logging.basicConfig(level=logging.DEBUG)

app = FastAPI()
client = DiscordOAuthClient(
    CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, scopes=("identify", "guilds")
)


@app.get("/login")
async def login_with_discord():
    return client.redirect(prompt="none")


@app.get("/callback")
async def callback(code: str):
    async with client.session(code) as session:
        user = await session.identify()
        print(session.token)  # at this point you can get the user's access token
    return {"user": str(user)}


@app.get("/guilds")
async def get_guilds():
    async with client.session_from_token(TOKEN) as session:
        # TOKEN is the 'access_token' string or the whole dict obtained in previous login
        guilds = await session.guilds()
    return {"guilds": [str(g) for g in guilds]}


uvicorn.run(app, host="0.0.0.0", port=9000)
