import discord
from .user import StarletteDiscordUser
from starlette.responses import RedirectResponse

from .session import OAuth2Session


DISCORD_URL = 'https://discord.com'
API_URL = DISCORD_URL + '/api/v8'


class DiscordOAuthClient:
    """Client for Discord Oauth2.

    Parameters
    ----------
    client_id:
        Discord application client ID.
    client_secret:
        Discord application client secret.
    redirect_uri:
        Discord application redirect URI.
    """
    def __init__(self, client_id, client_secret, redirect_uri, scope='identify'):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope

    def redirect(self):
        """Returns a RedirectResponse that directs to Discord login."""
        return RedirectResponse(DISCORD_URL + f'/api/oauth2/authorize'
                                              f'?client_id={self.client_id}'
                                              f'&redirect_uri={self.redirect_uri}'
                                              f'&response_type=code'
                                              f'&scope={self.scope}')

    def _session(self):
        return OAuth2Session(
            client_id=self.client_id,
            scope=self.scope,
            redirect_uri=self.redirect_uri,
        )

    async def _request(self, url_fragment, session, auth):
        token = auth['access_token']
        url = API_URL + url_fragment
        headers = {
            'Authorization': 'Authorization: Bearer ' + token
        }
        async with session.get(url, headers=headers) as resp:
            return await resp.json()

    async def fetch_token(self, session, code):
        """Fetch a token from a user authorization code."""
        url = API_URL + '/oauth2/token'
        token = await session.fetch_token(url, code=code, client_secret=self.client_secret)
        return token

    async def identify(self, code):
        """Authorize and identify a user.

        Parameters
        ----------
        code:
            Authorization code included with user request after redirect from Discord.

        Returns
        -------
        :class:`dict`
            The user who authorized the application.
        """
        async with self._session() as session:
            token = await self.fetch_token(session, code)
            user = await self._request('/users/@me', session, token)

        return user

    async def login(self, code):
        """Alias for ``identify``."""
        return await self.identify(code)

    async def guilds(self, code):
        """Authorize a user and fetch their guild list.

        Parameters
        ----------
        code:
            Authorization code included with user request after redirect from Discord.

        Returns
        -------
        :class:`list`
            The user's guild list.
        """
        async with self._session() as session:
            token = await self.fetch_token(session, code)
            guilds = await self._request('/users/@me/guilds', session, token)

        return guilds
