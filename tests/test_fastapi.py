import uvicorn
from auth import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
from fastapi import FastAPI

from starlette_discord import DiscordOAuth2Client

app = FastAPI()
client = DiscordOAuth2Client(
    CLIENT_ID,
    CLIENT_SECRET,
    REDIRECT_URI,
    scopes=("identify", "guilds", "email", "connections"),
)


@app.get("/login")
async def login_with_discord():
    return client.redirect()


@app.get("/callback")
async def callback(code: str):
    async with client.session(code) as session:
        u = await session.identify()
        g = await session.guilds()
        c = await session.connections()
    return {"user": str(u), "guilds": str(g), "connections": str(c)}


uvicorn.run(app, host="0.0.0.0", port=9000)
