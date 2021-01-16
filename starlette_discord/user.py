import discord


class StarletteDiscordUser(discord.User):
    @property
    def guilds(self):
        try:
            return self._guilds
        except AttributeError:
            return None

    @guilds.setter
    def guilds(self, value):
        self._guilds = value
