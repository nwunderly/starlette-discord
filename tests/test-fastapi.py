import uvicorn
from fastapi import FastAPI

from starlette_discord.client import DiscordOAuthClient
from auth import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI


app = FastAPI()
client = DiscordOAuthClient(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, scopes=('identify', 'guilds', 'email', 'connections'))


@app.get('/login')
async def login_with_discord():
    return client.redirect()


@app.get('/callback')
async def callback(code: str):
    async with client.session(code) as session:
        u = await session.identify()
        g = await session.guilds()
        c = await session.connections()
    return {'user': u, 'guilds': g, 'connections': c}

uvicorn.run(app, host='0.0.0.0', port=9000)
