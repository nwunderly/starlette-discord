"""
A more advanced FastAPI app that demonstrates Starlette-Discord's versatile DiscordOAuthSession.

While client.login(code) is a useful shortcut for identifying a user, DiscordOAuthSession within
an async context manager is much more powerful. It can be used for getting other information like
a user's guilds or account connections.
"""

import uvicorn
from fastapi import FastAPI
from starlette_discord.client import DiscordOAuthClient


CLIENT_ID = 'YOUR_CLIENT_ID'
CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
REDIRECT_URI = 'YOUR_REDIRECT_URI'


app = FastAPI()
client = DiscordOAuthClient(
    CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, scopes=('identify', 'guilds', 'connections')
)


@app.get('/login')
async def login_with_discord():
    return client.redirect()


# NOTE: REDIRECT_URI should be this path.
@app.get('/callback')
async def callback(code: str):
    # it's recommended to use DiscordOAuthSession within an async context manager
    async with client.session(code) as session:
        user = await session.identify()
        guilds = await session.guilds()
        connections = await session.connections()

    return {
        'user': str(user),
        'guilds': [str(g) for g in guilds],
        'connections': [str(c) for c in connections]
    }


uvicorn.run(app)
