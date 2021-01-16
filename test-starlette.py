import uvicorn
from starlette.applications import Starlette

from starlette_discord.client import DiscordOAuthClient
from auth import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI


app = Starlette()
client = DiscordOAuthClient(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)


@app.route('/login')
async def login_with_discord():
    return client.redirect()


@app.route('/callback')
async def callback(code: str):
    return await client.login(code)



uvicorn.run(app, host='localhost', port=9000)
