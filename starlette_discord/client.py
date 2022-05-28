from oauthlib.common import generate_token
from starlette.responses import RedirectResponse

from .models import Connection, Guild, User
from .oauth import OAuth2Session

DISCORD_URL = "https://discord.com"
API_URL = DISCORD_URL + "/api/v9"


class DiscordOAuthSession(OAuth2Session):
    """Session containing data for a single authorized user. Handles authorization internally.

    .. warning::
        It is recommended to not construct this class directly.
        Use `DiscordOAuthClient.session` or `DiscordOAuthClient.session_from_token` instead.

    .. note::
        Either the 'code' or 'token' parameter must be provided, but not both.

    Parameters
    ----------
    code: Optional[:class:`str`]
        Authorization code included with user request after redirect from Discord.
    token: Optional[Dict[:class:`str`, Union[:class:`str`, :class`int`, :class:`float`]]]
        A previously generated, valid, access token to use instead of the OAuth code exchange
    client_id: :class:`str`
        Your Discord application client ID.
    scope: :class:`str`
        Discord authorization scopes separated by %20.
    redirect_uri: :class:`str`
        Your Discord application redirect URI.
    code: Optional[:class:`str`]
        Authorization code included with user request after redirect from Discord.
    token: Optional[Dict[:class:`str`, Union[:class:`str`, :class:`int`, :class`float`]]]
        A previously generated, valid, access token to use instead of the OAuth code exchange
    """

    def __init__(self, client_id, client_secret, scope, redirect_uri, *, code, token):
        if (not (code or token)) or (code and token):
            raise ValueError(
                "Either 'code' or 'token' parameter must be provided, but not both."
            )
        elif token:
            if not isinstance(token, dict):
                raise TypeError(
                    "Parameter 'token' must be an instance of dict with at least the 'access_token' key.'"
                )
            if "access_token" not in token:
                raise ValueError("Parameter 'token' requires 'access_token' key.")
            elif "token_type" not in token:  # this is not required for the discord class but for the parent class
                token["token_type"] = "Bearer"

        self._discord_auth_code = code
        self._discord_client_secret = client_secret
        self.token = token
        self._cached_user = None
        self._cached_guilds = None
        self._cached_connections = None

        super().__init__(
            client_id=client_id, scope=scope, redirect_uri=redirect_uri, token=token
        )

    @property
    def token(self):
        """Dict[:class:`str`, Union[:class:`str`, :class:`int`, :class:`float`]]: The session's current OAuth token, if one exists."""
        # this is pretty much just for documentation purposes.
        return super().token

    @token.setter
    def token(self, value):
        # stolen from oauth.py to allow the client to set this still.
        self._client.token = value
        self._client.populate_token_attributes(value)

    @property
    def cached_user(self):
        """:class:`dict`: The session's cached user, if an `identify()` request has previously been made."""
        return self._cached_user

    @property
    def cached_guilds(self):
        """List[:class:`dict`]: The session's cached guilds, if a `guilds()` request has previously been made."""
        return self._cached_guilds

    @property
    def cached_connections(self):
        """List[:class:`dict`]: The session's cached account connections, if a `connections()` request has previously been made."""
        return self._cached_connections

    def new_state(self):
        """Generate a new state string for verifying authorizations.

        Returns
        -------
        :class:`str`
            The state string that was generated.
        """
        return generate_token()

    async def _discord_request(self, url_fragment, method="GET"):
        if not self.token:  # DEV NOTE: do we actually need to fetch the token here?
            url = API_URL + "/oauth2/token"
            self.token = t = await self.fetch_token(
                url,
                code=self._discord_auth_code,
                client_secret=self._discord_client_secret,
            )

        access_token = self.token["access_token"]
        url = API_URL + url_fragment
        headers = {"Authorization": "Authorization: Bearer " + access_token}
        async with self.request(method, url, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def identify(self):
        """Identify a user.

        Returns
        -------
        :class:`User`
            The user who authorized the application.
        """
        data_user = await self._discord_request("/users/@me")
        user = User(data=data_user)
        self._cached_user = user
        return user

    async def guilds(self):
        """Fetch a user's guild list.

        Returns
        -------
        List[:class:`Guild`]
            The user's guild list.
        """
        data_guilds = await self._discord_request("/users/@me/guilds")
        guilds = [Guild(data=g) for g in data_guilds]
        self._cached_guilds = guilds
        return guilds

    async def connections(self):
        """Fetch a user's linked 3rd-party accounts.

        Returns
        -------
        List[:class:`Connection`]
            The user's connections.
        """
        data_connections = await self._discord_request("/users/@me/connections")
        connections = [Connection(data=c) for c in data_connections]
        self._cached_connections = connections
        return connections

    async def join_guild(self, guild_id, user_id=None):
        """Add a user to a guild.

        Parameters
        ----------
        guild_id: :class:`int`
            The ID of the guild to add the user to.
        user_id: Optional[:class:`int`]
            ID of the user, if known. If not specified, will first identify the user.
        """
        if not user_id:
            user = await self.identify()
            user_id = user.id
        return await self._discord_request(
            f"/guilds/{guild_id}/members/{user_id}", method="PUT"
        )

    async def join_group_dm(self, dm_channel_id, user_id=None):
        """Add a user to a group DM.

        Parameters
        ----------
        dm_channel_id: :class:`int`
            The ID of the DM channel to add the user to.
        user_id: Optional[:class:`int`]
            ID of the user, if known. If not specified, will first identify the user.
        """
        if not user_id:
            user = await self.identify()
            user_id = user.id
        return await self._discord_request(
            f"/channels/{dm_channel_id}/recipients/{user_id}", method="PUT"
        )


class DiscordOAuthClient:
    """Client for Discord Oauth2.

    Parameters
    ----------
    client_id: Union[:class:`str`, :class:`int`]
        Discord application client ID.
    client_secret: :class:`str`
        Discord application client secret.
    redirect_uri: :class:`str`
        Discord application redirect URI.
    scopes: Tuple[:class:`str`]
        Discord authorization scopes.
    """

    def __init__(self, client_id, client_secret, redirect_uri, scopes=("identify",)):
        self.client_id = str(client_id)
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = " ".join(scope for scope in scopes)

    def redirect(self, state=None, prompt=None, redirect_uri=None):
        """Returns a RedirectResponse that directs to Discord login.

        Parameters
        ----------
        state: Optional[:class:`str`]
            Optional state parameter for Discord redirect URL.
            Docs can be found `here <https://discord.com/developers/docs/topics/oauth2#state-and-security>`_.
        prompt: Optional[:class:`str`]
            Optional prompt parameter for Discord redirect URL.
            If ``consent``, user is prompted to re-approve authorization. If ``none``, skips authorization if user has already authorized.
            Defaults to ``consent``.
        redirect_uri: Optional[:class:`str`]
            Optional redirect URI to pass to Discord. Defaults to the client's redirect URI.
        """
        client_id = f"client_id={self.client_id}"
        redirect_uri = f"redirect_uri={redirect_uri or self.redirect_uri}"
        scopes = f"scope={self.scope}"
        response_type = "response_type=code"
        url = (
            DISCORD_URL
            + f"/api/oauth2/authorize?{client_id}&{redirect_uri}&{scopes}&{response_type}"
        )
        if state:
            url += f"&state={state}"
        if prompt:
            url += f"&prompt={prompt}"
        return RedirectResponse(url)

    def session(self, code) -> DiscordOAuthSession:
        """Create a new DiscordOAuthSession from an authorization code.

        Parameters
        ----------
        code: :class:`str`
            The OAuth2 code provided by the Discord API.

        Returns
        -------
        :class:`DiscordOAuthSession`
            A new OAuth session.
        """
        return DiscordOAuthSession(
            code=code,
            token=None,
            client_id=self.client_id,
            client_secret=self.client_secret,
            scope=self.scope,
            redirect_uri=self.redirect_uri,
        )

    def session_from_token(self, token) -> DiscordOAuthSession:
        """Create a new DiscordOAuthSession from an existing token.

        Parameters
        ----------
        token: Dict[:class:`str`, Union[:class:`str`, :class:`int`, :class:`float`]]
            An existing (valid) access token to use instead of the OAuth code exchange.

        Returns
        -------
        :class:`DiscordOAuthSession`
            A new OAuth session.
        """
        return DiscordOAuthSession(
            code=None,
            token=token,
            client_id=self.client_id,
            client_secret=self.client_secret,
            scope=self.scope,
            redirect_uri=self.redirect_uri,
        )

    async def login(self, code):
        """Shorthand for session setup + identify.

        Parameters
        ----------
        code: :class:`str`
            The OAuth2 code provided by the authorization request.

        Returns
        -------
        :class:`User`
            The user who authorized the application.
        """
        async with self.session(code) as session:
            user = await session.identify()
        return user

    # TODO: decide if I want to keep this. not a fan of the method name.
    async def login_return_token(self, code):
        """Shorthand for session setup + identify. Returns user and token.

        Parameters
        ----------
        code: :class:`str`
            The OAuth2 code provided by the authorization request.

        Returns
        -------
        Tuple[user, token]
        user: :class:`User`
            The user who authorized the application.
        token: Dict[:class:`str`, Union[:class:`str`, :class:`int`, :class:`float`]]
            The access token provided by the Discord API.
        """
        async with self.session(code) as session:
            user = await session.identify()
        return user, session.token
