from typing import List, Optional

import discord


class DiscordObject:
    """Represents a Discord object. This library's equivalent to discord.Object.

    Attributes
    ----------
    id: :class:`int`
        The Discord object's unique ID.
    """

    def __init__(self, data):
        self._json_data = data
        self.id = int(data["id"])

    @classmethod
    def from_id(cls, id_: int):
        """Initializes a new DiscordObject with the given ID.

        .. note::
            Most people will never have to use this method.
            It is provided for cases where you only need an object with a specific ID.

        Parameters
        ----------
        id_: :class:`int`
            The ID of the object to create.
        """
        return cls({"id": str(id_)})

    def __eq__(self, other) -> bool:
        return other.id == self.id

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return self.id >> 22

    def json(self):
        """Returns the original JSON data for this model."""
        return self._json_data


class User(DiscordObject):
    """A `user`_ model from Discord. Returned by ``session.identify()``.

    Attributes
    ----------
    id: :class:`int`
        The user's unique ID.
    username: :class:`str`
        The user's username.
    discriminator: :class:`str`
        The user's discriminator.
    avatar: :class:`str`
        The user's avatar hash.
    flags: :class:`int`
        The `flags`_ on the user's account
    public_flags: :class:`int`
        The public `flags`_ on the user's account.
    banner: :class:`str`
        The user's banner hash.
    banner_color: :class:`str`
        The user's banner color.
    accent_color: :class:`int`
        The user's banner color: represented as the int form of the color's hex code.
    locale: :class:`str`
        The user's language locale.
    mfa_enabled: :class:`bool`
        Whether the user has multi-factor authentication enabled.
    email: :class:`str`
        The user's email address. Only provided if the ``email`` scope is authorized.
    verified: :class:`str`
        Whether the user's email address has been verified.


    .. _user: https://discord.com/developers/docs/resources/user
    .. _flags: https://discord.com/developers/docs/resources/user#user-object-user-flags
    """

    __slots__ = (
        "_json_data",
        "id",
        "username",
        "discriminator",
        "avatar",
        "flags",
        "public_flags" "banner",
        "banner_color" "accent_color",
        "locale",
        "mfa_enabled",
        "email",
        "verified",
    )

    _json_data: dict
    id: int
    username: str
    discriminator: str
    avatar: Optional[str]
    flags: int
    public_flags: int
    banner: Optional[str]
    banner_color: Optional[int]
    accent_color: Optional[int]
    locale: Optional[str]
    mfa_enabled: bool
    email: Optional[str]
    verified: bool

    def __init__(self, *, data):
        super().__init__(data)
        self._update(data)

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r} discriminator={self.discriminator!r}>"

    def __str__(self) -> str:
        return f"{self.username}#{self.discriminator}"

    def _update(self, data) -> None:
        # these are defined in super().__init__
        # self._json_data = data
        # self.id = int(data['id'])
        self.username = data["username"]
        self.discriminator = data["discriminator"]
        self.avatar = data["avatar"]
        self.flags = data["flags"]
        self.public_flags = data.get("public_flags", 0)
        self.banner = data.get("banner", None)
        self.banner_color = data.get("banner_color", None)
        self.accent_color = data.get("accent_color", None)
        self.locale = data.get("locale", None)
        self.mfa_enabled = data.get("mfa_enabled", None)
        self.email = data.get("email", None)
        self.verified = data.get("verified", None)

    async def to_dpy(self, client):
        """Tries to convert this User to a ``discord.User``.

        This is just a shortcut for ``client.get_user(id)`` followed by ``client.fetch_user(id)``,
        returning ``None`` if not found.

        .. note::
            A discord.py ``Client`` or ``Bot`` object must be passed into this function.

        Parameters
        ----------
        client: :class:`discord.Client`
            The bot client to use to create the object.

        Returns
        -------
        :class:`discord.User`
            The discord.py User object, if it could be found.
        """
        user = client.get_user(self.id)
        if not user:
            try:
                user = await client.fetch_user(self.id)
            except discord.HTTPException:
                return None
        return user


class Guild(DiscordObject):
    """A partial `guild`_ model from Discord. Returned by ``session.guilds()``.

    Attributes
    ----------
    id: :class:`int`
        The guild's unique ID.
    name: :class:`str`
        The guild's name.
    icon: :class:`str`
        The guild's icon hash.
    owner: :class:`bool`
        Whether the authorized user is owner of this guild.
    permissions: :class:`int`
        The authorized user's `permissions`_ in this guild.
    features: List[:class:`str`]
        The guild's enabled `features`_.


    .. _guild: https://discord.com/developers/docs/resources/guild
    .. _features: https://discord.com/developers/docs/resources/guild#guild-object-guild-features
    .. _permissions: https://discord.com/developers/docs/topics/permissions
    """

    __slots__ = (
        "_json_data",
        "id",
        "name",
        "icon",
        "owner",
        "permissions",
        "features",
    )

    _json_data: dict
    id: int
    name: str
    icon: Optional[str]
    owner: bool
    permissions: int
    features: List[str]

    def __init__(self, *, data):
        self._update(data)
        super().__init__(data)

    def __repr__(self) -> str:
        return f"<Guild id={self.id} name={self.name!r}>"

    def __str__(self) -> str:
        return self.__repr__()

    def _update(self, data) -> None:
        # these are defined in super().__init__
        # self._json_data = data
        # self.id = int(data['id'])
        self.name = data["name"]
        self.icon = data.get("icon", None)
        self.owner = data["owner"]
        self.permissions = int(data["permissions"])
        self.features = data["features"]

    async def to_dpy(self, client):
        """Tries to convert this Guild to a ``discord.Guild``.

        This is just a shortcut for ``client.get_guild(id)`` followed by ``client.fetch_guild(id)``,
        returning ``None`` if not found.

        .. note::
            A discord.py ``Client`` or ``Bot`` object must be passed into this function.

        Parameters
        ----------
        client: :class:`discord.Client`
            The bot client to use to create the object.

        Returns
        -------
        :class:`discord.Guild`
            The discord.py Guild object, if the guild could be found.
        """
        guild = client.get_guild(self.id)
        if not guild:
            try:
                guild = await client.fetch_guild(self.id)
            except discord.HTTPException:
                return None
        return guild


class Connection:
    """An account `connection`_ model from Discord.

    Attributes
    ----------
    type: :class:`str`
        The connection type.
    id: :class:`str`
        The connected account's ID.
    name: :class:`str`
        The connected account's username.
    visibility: :class:`int`
        The connected account's `visibility`_.
    friend_sync: :class:`bool`
        Whether friend sync is enabled for this connected account.
    show_activity: :class:`bool`
        Whether activities related to this connection will be shown in presence updates.
    verified: :class:`bool`
        Whether this connected account is verified.


    .. _connection: https://discord.com/developers/docs/resources/user#connection-object
    .. _visibility: https://discord.com/developers/docs/resources/user#connection-object-visibility-types
    """

    __slots__ = (
        "_json_data",
        "type",
        "id",
        "name",
        "visibility",
        "friend_sync",
        "show_activity",
        "verified",
    )

    _json_data: dict
    type: str
    id: str
    name: str
    visibility: int
    friend_sync: bool
    show_activity: bool
    verified: bool

    def __init__(self, *, data):
        self._update(data)

    def __repr__(self) -> str:
        return f"<Connection type={self.type}>"

    def __str__(self) -> str:
        return self.__repr__()

    def _update(self, data) -> None:
        self._json_data = data
        self.type = data["type"]
        self.id = data["id"]
        self.name = data["name"]
        self.visibility = data["visibility"]
        self.friend_sync = data["friend_sync"]
        self.show_activity = data["show_activity"]
        self.verified = data["verified"]

    def json(self):
        """Returns the original JSON data for this model."""
        return self._json_data
