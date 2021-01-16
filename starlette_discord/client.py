import discord
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

    async def _identify(self, session, auth):
        token = auth['access_token']
        url = API_URL + '/users/@me'
        headers = {
            'Authorization': 'Authorization: Bearer ' + token
        }
        async with session.get(url, headers=headers) as resp:
            return await resp.json()

    async def login(self, code):
        """Identify the user who has granted an authorization token.

        Parameters
        ----------
        code:
            Authorization code included with user request after redirect from Discord.

        Returns
        -------
        :class:`discord.User`
            The user who authorized the application.
        """
        async with self._session() as session:
            url = API_URL + '/oauth2/token'
            token = await session.fetch_token(url, code=code, client_secret=self.client_secret)
            user = await self._identify(session, token)

        return discord.User(state=None, data=user)
