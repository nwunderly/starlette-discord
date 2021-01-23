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
        self._cached_user = None
        self._cached_guilds = None
        self._cached_connections = None

    async def __aenter__(self):
        await super().__aenter__()

        url = API_URL + '/oauth2/token'

        self._discord_token = await self.fetch_token(
            url,
            code=self._discord_auth_code,
            client_secret=self._discord_client_secret
        )

        return self

    async def _discord_request(self, url_fragment, method='GET'):
        auth = self._discord_token
        token = auth['access_token']
        url = API_URL + url_fragment
        headers = {
            'Authorization': 'Authorization: Bearer ' + token
        }
        async with self.request(method, url, headers=headers) as resp:
            return await resp.json()

    async def identify(self):
        """Identify a user.

        Returns
        -------
        :class:`dict`
            The user who authorized the application.
        """
        if self._cached_user:
            return self._cached_user
        user = await self._discord_request('/users/@me')
        self._cached_user = user
        return user

    async def guilds(self):
        """Fetch a user's guild list.

        Returns
        -------
        :class:`list`
            The user's guild list.
        """
        if self._cached_guilds:
            return self._cached_guilds
        guilds = await self._discord_request('/users/@me/guilds')
        self._cached_guilds = guilds
        return guilds

    async def connections(self):
        """Fetch a user's linked 3rd-party accounts.

        Returns
        -------
        :class:`list`
            The user's connections.
        """
        if self._cached_connections:
            return self._cached_connections
        connections = await self._discord_request('/users/@me/connections')
        self._cached_connections = connections
        return connections

    async def join_guild(self, guild_id, user_id=None):
        """Add a user to a guild.

        Parameters
        ----------
        guild_id: :class:`int`
            The ID of the guild to add the user to.
        user_id: :class:`Optional[int]`
            ID of the user, if known. If not specified, will first identify the user.
        """
        if not user_id:
            user = await self.identify()
            user_id = user['id']
        return await self._discord_request(f'/guilds/{guild_id}/members/{user_id}', method='PUT')

    async def join_group_dm(self, dm_channel_id, user_id=None):
        """Add a user to a group DM.

        Parameters
        ----------
        dm_channel_id: :class:`int`
            The ID of the DM channel to add the user to.
        user_id: :class:`Optional[int]`
            ID of the user, if known. If not specified, will first identify the user.
        """
        if not user_id:
            user = await self.identify()
            user_id = user['id']
        return await self._discord_request(f'/channels/{dm_channel_id}/recipients/{user_id}', method='PUT')


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
        client_id = f'client_id={self.client_id}'
        redirect_uri = f'redirect_uri={self.redirect_uri}'
        scopes = f'scope={self.scopes}'
        response_type = 'response_type=code'
        return RedirectResponse(
            DISCORD_URL + f'/api/oauth2/authorize?{client_id}&{redirect_uri}&{scopes}&{response_type}'
        )

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
