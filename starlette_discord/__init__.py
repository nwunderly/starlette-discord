"""
starlette-discord
-----------------
"Login with Discord" support for Starlette and FastAPI.

:copyright: (c) 2021 nwunderly
:license: MIT, see LICENSE for more details.
"""

__title__ = "starlette-discord"
__author__ = "nwunderly"
__license__ = "MIT"
__copyright__ = "Copyright 2021 nwunderly"
__version__ = "0.2.1"

from .models import Connection, DiscordObject, Guild, User
from .oauth import DiscordOAuth2Client, DiscordOAuth2Session
