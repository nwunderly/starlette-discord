"""
A basic FastAPI app that demonstrates "login with Discord", returning the user who was logged in.
"""

import uvicorn
from fastapi import FastAPI
from starlette_discord.client import DiscordOAuthClient


CLIENT_ID = 'YOUR_CLIENT_ID'
CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
REDIRECT_URI = 'YOUR_REDIRECT_URI'


app = FastAPI()
client = DiscordOAuthClient(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)


@app.get('/login')
async def login_with_discord():
    return client.redirect()


# NOTE: REDIRECT_URI should be this path.
@app.get('/callback')
async def callback(code: str):
    user = await client.login(code)
    return user.json()


uvicorn.run(app)
