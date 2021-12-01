# Getting Started


## Installing

starlette-discord can be installed with the command

```sh
# Linux
python3 -m pip install -U starlette-discord

# Windows
python -m pip install -U starlette-discord
```

To install the development version of the library directly from source:

```sh
$ git clone https://github.com/nwunderly/starlette-discord
$ cd starlette-discord
$ python3 -m pip install -U .
```

## Basic FastAPI App

Below is an example FastAPI app implementing Discord's OAuth flow to identify the user.

```py
import uvicorn
from fastapi import FastAPI
from starlette_discord import DiscordOAuthClient

client_id = "YOUR APP'S CLIENT ID HERE"
client_secret = "YOUR APP'S CLIENT SECRET HERE"
redirect_uri = "http://localhost:8000/callback"

app = FastAPI()
discord_client = DiscordOAuthClient(client_id, client_secret, redirect_uri)

@app.get('/login')
async def start_login():
    return discord_client.redirect()

@app.get('/callback')
async def finish_login(code: str):
    user = await discord_client.login(code)
    print(user)
    return user

uvicorn.run(app)
```

To begin the OAuth authorization flow with this app, visit `http://localhost:8000/login`.
