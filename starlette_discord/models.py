from typing import Optional, List


class DiscordObject:
    def __init__(self, data):
        self._json_data = data
        self.id = data['id']

    def __eq__(self, other) -> bool:
        return other.id == self.id

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return self.id >> 22

    def json(self):
        """Returns the original JSON data for this model."""
        return self._json_data

    def to_dpy(self, client):
        """Converts this DiscordObject to a discord.Object"""
        raise NotImplementedError


class User(DiscordObject):
    """A user model from Discord. Returned by ``session.identify()``."""

    __slots__ = (
        '_json_data',
        'id',
        'username',
        'discriminator',
        'avatar',
        'flags',
        'public_flags'
        'banner',
        'banner_color'
        'accent_color',
        'locale',
        'mfa_enabled',
        'email',
        'verified',
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
        self._update(data)

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r} discriminator={self.discriminator!r}>"

    def __str__(self) -> str:
        return f'{self.username}#{self.discriminator}'

    def _update(self, data) -> None:
        self._json_data = data
        self.id = int(data['id'])
        self.username = data['username']
        self.discriminator = data['discriminator']
        self.avatar = data['avatar']
        self.flags = data['flags']
        self.public_flags = data.get('public_flags', 0)
        self.banner = data.get('banner', None)
        self.banner_color = data.get('banner_color', None)
        self.accent_color = data.get('accent_color', None)
        self.locale = data.get('locale', None)
        self.mfa_enabled = data.get('mfa_enabled', None)
        self.email = data.get('email', None)
        self.verified = data.get('verified', None)

    def to_dpy(self, client):
        """Converts this User to a discord.User object."""
        raise NotImplementedError


class Guild(DiscordObject):
    """A partial guild model from Discord. Returned by ``session.guilds()``."""

    __slots__ = (
        '_json_data',
        'id',
        'name',
        'icon',
        'owner',
        'permissions',
        'features',
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

    def __repr__(self) -> str:
        return f"<Guild id={self.id} name={self.name!r}>"

    def __str__(self) -> str:
        return self.__repr__()

    def _update(self, data) -> None:
        self._json_data = data
        self.id = int(data['id'])
        self.name = data['name']
        self.icon = data.get('icon', None)
        self.owner = data['owner']
        self.permissions = data['permissions']
        self.features = data['features']

    def to_dpy(self, client):
        """Converts this Guild to a discord.Guild object."""
        raise NotImplementedError


class Connection:
    """An account connection model from Discord."""
    
    __slots__ = (
        '_json_data',
        'type',
        'id',
        'name',
        'visibility',
        'friend_sync',
        'show_activity',
        'verified',
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
        self.type = data['type']
        self.id = data['id']
        self.name = data['name']
        self.visibility = data['visibility']
        self.friend_sync = data['friend_sync']
        self.show_activity = data['show_activity']
        self.verified = data['verified']

    def json(self):
        """Returns the original JSON data for this model."""
        return self._json_data
