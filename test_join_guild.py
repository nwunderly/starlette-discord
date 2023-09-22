import logging

import uvicorn
from auth import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, TOKEN
from fastapi import FastAPI

from starlette_discord.client import DiscordOAuthClient

app = FastAPI()
client = DiscordOAuthClient(
    CLIENT_ID,
    CLIENT_SECRET,
    REDIRECT_URI,
    scopes=("identify", "guilds", "guilds.join"),
    # bot_token=TOKEN,
)


@app.get("/login")
async def login_with_discord():
    return client.redirect()


@app.get("/callback")
async def callback(code: str):
    async with client.session(code) as session:
        u = await session.identify()
        print("identify response", u)
        g = await session.join_guild(625544528228777984, TOKEN, u.id)
        print("guild response", g)


uvicorn.run(app, host="0.0.0.0", port=9000)
