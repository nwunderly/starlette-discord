# Starlette-Discord Changelog


## v0.2.0
- Add a changelog. (this one!)
- Add discord.py-like models. (API calls no longer return JSON data)
  - DiscordObject (generic base class, shouldn't be used)
  - [User](../models.html#user)
  - [Guild](../models.html#guild)
  - [Connection](../models.html#guild)
- Add new [DiscordOAuthClient](../api.html#starlette_discord.DiscordOAuthClient) methods to make token handling slightly easier.
  - [DiscordOAuthClient.login_return_token](../api.html#starlette_discord.DiscordOAuthClient.login_return_token)
  - [DiscordOAuthClient.session_from_token](../api.html#starlette_discord.DiscordOAuthClient.session_from_token)
