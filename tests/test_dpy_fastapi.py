import asyncio

import discord
import uvicorn
from auth import BOT_TOKEN, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
from fastapi import FastAPI

from starlette_discord.client import DiscordOAuthClient

app = FastAPI()
client = DiscordOAuthClient(
    CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, scopes=("identify", "guilds")
)

# dpy bot initialization
bot = discord.Client()


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}.")


@app.on_event("startup")
async def startup():
    asyncio.create_task(bot.start(BOT_TOKEN))


@app.get("/login")
async def login_with_discord():
    return client.redirect()


@app.get("/callback")
async def callback(code: str):
    async with client.session(code) as session:
        u = await session.identify()
        g = await session.guilds()

    u = await u.to_dpy(bot)
    g = [await g.to_dpy(bot) for g in g]

    return {"user": str(u), "guilds": str(g)}


uvicorn.run(app, host="0.0.0.0", port=9000)
