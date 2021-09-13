import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse, RedirectResponse
from starlette.requests import Request

from starlette_discord.client import DiscordOAuthClient
from starlette_discord.models import User
from starlette_discord.middleware import setup_login_session_middleware
from auth import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI


app = Starlette()
client = DiscordOAuthClient(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, scopes=('identify', 'guilds', 'email', 'connections'))


@app.route('/dash')
async def callback(request: Request):
    user = User.from_cookie(request)
    token = request.session.get('discord-token')

    # back to login if not authenticated
    if not user:
        return RedirectResponse('/login')

    # request guilds
    async with client.session_from_token(token) as session:
        g = await session.guilds()

    # return cached user from login as well as guilds from this request
    return JSONResponse({'user': user.json(), 'guilds': str(g)})


setup_login_session_middleware(app, client)
uvicorn.run(app, host='0.0.0.0', port=9000)
