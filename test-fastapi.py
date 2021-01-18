import uvicorn
from fastapi import FastAPI
from starlette.responses import PlainTextResponse

from starlette_discord.client import DiscordOAuthClient
from auth import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI


app = FastAPI()
client = DiscordOAuthClient(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, scopes=('identify', 'guilds'))


@app.get('/login')
async def login_with_discord():
    return client.redirect()


@app.get('/callback')
async def callback(code: str):
    u = await client.login(code)
    return u

uvicorn.run(app, host='0.0.0.0', port=5000)
