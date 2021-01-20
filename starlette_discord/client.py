from starlette.responses import RedirectResponse
from .oauth import OAuth2Session


DISCORD_URL = 'https://discord.com'
API_URL = DISCORD_URL + '/api/v8'


class DiscordOAuthSession(OAuth2Session):
    """Session containing data for a single authorized user. Handles authorization internally.

    Parameters
    ----------
    code:
        Authorization code included with user request after redirect from Discord.
    """
    def __init__(self, code, client_id, client_secret, scope, redirect_uri):
        self._discord_auth_code = code
        self._discord_client_secret = client_secret
        self._discord_token = None
        super().__init__(
            client_id=client_id,
            scope=scope,
            redirect_uri=redirect_uri,
        )

    async def __aenter__(self):
        await super().__aenter__()

        url = API_URL + '/oauth2/token'

        self._discord_token = await self.fetch_token(
            url,
            code=self._discord_auth_code,
            client_secret=self._discord_client_secret
        )

        return self

    async def _discord_request(self, url_fragment, auth):
        token = auth['access_token']
        url = API_URL + url_fragment
        headers = {
            'Authorization': 'Authorization: Bearer ' + token
        }
        async with self.get(url, headers=headers) as resp:
            return await resp.json()

    async def identify(self):
        """Authorize and identify a user.

        Returns
        -------
        :class:`dict`
            The user who authorized the application.
        """
        return await self._discord_request('/users/@me', self._discord_token)

    async def guilds(self):
        """Authorize a user and fetch their guild list.

        Returns
        -------
        :class:`list`
            The user's guild list.
        """
        return await self._discord_request('/users/@me/guilds', self._discord_token)


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
    def __init__(self, client_id, client_secret, redirect_uri, scopes=('identify',)):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scopes = ' '.join(scope for scope in scopes)

    def redirect(self):
        """Returns a RedirectResponse that directs to Discord login."""
        return RedirectResponse(DISCORD_URL + f'/api/oauth2/authorize'
                                              f'?client_id={self.client_id}'
                                              f'&redirect_uri={self.redirect_uri}'
                                              f'&response_type=code'
                                              f'&scope={self.scopes}')

    def session(self, code) -> DiscordOAuthSession:
        return DiscordOAuthSession(
            code=code,
            client_id=self.client_id,
            client_secret=self.client_secret,
            scope=self.scopes,
            redirect_uri=self.redirect_uri,
        )

    async def login(self, code):
        """Shorthand for session setup + identify()"""
        async with self.session(code) as session:
            user = await session.identify()
        return user
