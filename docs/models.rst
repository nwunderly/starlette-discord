.. currentmodule:: starlette_discord


Discord Models
==============

This page provides a breakdown of the Discord data classes used by starlette_discord.


DiscordObject
-------------

.. autoclass:: DiscordObject
    :members:


Converting to Discord.py Objects
++++++++++++++++++++++++++++++++

DiscordObject subclasses (User and Guild) can be converted to ``discord.X`` objects with the ``to_dpy`` method.
While discord.py is not a dependency of this library, the client passed into this method should be a valid discord.py
client. Specifically, it needs to implement the ``get_X`` and ``fetch_X`` methods.

This method is, and should remain, compatible with both discord.py 1.X and 2.X.


User
----

.. autoclass:: User
    :members:


Guild
-----

.. autoclass:: Guild
    :members:


Connection
----------

.. autoclass:: Connection
    :members: