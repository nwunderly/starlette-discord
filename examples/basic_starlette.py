"""
A basic Starlette app that demonstrates "login with Discord", returning the user who was logged in.
"""

import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette_discord.client import DiscordOAuthClient


CLIENT_ID = 'YOUR_CLIENT_ID'
CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
REDIRECT_URI = 'YOUR_REDIRECT_URI'


app = Starlette()
client = DiscordOAuthClient(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)


@app.route('/login')
async def login_with_discord(_):
    return client.redirect()


# NOTE: REDIRECT_URI should be this path.
@app.route('/callback')
async def callback(request):
    code = request.query_params['code']
    u = await client.login(code)
    return JSONResponse(u)


uvicorn.run(app)
