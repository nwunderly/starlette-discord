import aiohttp
import oauthlib

from starlette.responses import RedirectResponse

from .oauth2session import OAuth2Session


BASE_URL = 'https://discord.com'


class DiscordOauthClient:
    """Client for Discord Oauth2."""
    def __init__(self, client_id, client_secret, redirect_uri, scope='identify'):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope

    def redirect(self):
        return RedirectResponse(BASE_URL + f'/api/oauth2/authorize'
                                           f'?client_id={self.client_id}'
                                           f'&redirect_uri={self.redirect_uri}'
                                           f'&response_type=code'
                                           f'&scope=identify')

    def _session(self):
        return OAuth2Session(
            client_id=self.client_id,
            # client=None,
            # auto_refresh_url=None,
            # auto_refresh_kwargs=None,
            scope=self.scope,
            redirect_uri=self.redirect_uri,
            # token=None,
            # state=None,
            # token_updater=None,
        )

    async def _identify(self, session, auth):
        token = auth['access_token']
        url = BASE_URL + '/api/v6/users/@me'
        headers = {
            'Authorization': 'Authorization: Bearer ' + token
        }
        async with session.get(url, headers=headers) as resp:
            return resp.json()

    async def login(self, code):
        async with self._session() as session:
            url = BASE_URL + '/api/v8/oauth2/token'
            token = await session.fetch_token(url, code=code)
            print("TOKEN", token)
            user = await self._identify(session, token)
            return user
