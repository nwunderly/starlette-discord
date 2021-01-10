import aiohttp
import oauthlib

from starlette.responses import RedirectResponse


BASE_URL = 'https://discord.com'


class DiscordOauthClient:
    """Client for Discord Oauth2."""
    def __init__(self, client_id, client_secret, redirect_uri):
        self.session = aiohttp.ClientSession()
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    async def __aenter__(self):
        await self.session.__aenter__()

    async def __aexit__(self, *args, **kwargs):
        await self.session.__aexit__(*args, **kwargs)

    def redirect(self):
        return RedirectResponse(BASE_URL + f'/api/oauth2/authorize'
                                           f'?client_id={self.client_id}'
                                           f'&redirect_uri={self.redirect_uri}'
                                           f'&response_type=code'
                                           f'&scope=identify')

    async def _get_token(self, code):
        url = BASE_URL + '/api/v8/oauth2/token'
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
            'scope': 'identify',
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        async with self.session.post(url, data=data, headers=headers) as resp:
            return await resp.json()

    async def _identify(self, auth):
        token = auth['access_token']
        url = BASE_URL + '/api/v6/users/@me'
        headers = {
            'Authorization': 'Authorization: Bearer ' + token
        }
        async with self.session.get(url, headers=headers) as resp:
            return resp.json()

    async def login(self, code):
        auth = await self._get_token(code)
        user = await self._identify(auth)
        return user
