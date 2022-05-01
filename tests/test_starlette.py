import uvicorn
from auth import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse

from starlette_discord.client import DiscordOAuthClient

app = Starlette()
client = DiscordOAuthClient(
    CLIENT_ID,
    CLIENT_SECRET,
    REDIRECT_URI,
    scopes=("identify", "guilds", "email", "connections"),
)


@app.route("/login")
async def login_with_discord(_):
    return client.redirect()


@app.route("/callback")
async def callback(request: Request):
    code = request.query_params["code"]
    async with client.session(code) as session:
        u = await session.identify()
        g = await session.guilds()
        c = await session.connections()
    return JSONResponse({"user": str(u), "guilds": str(g), "connections": str(c)})


uvicorn.run(app, host="0.0.0.0", port=9000)
