import typing as t

import hikari

from config import Config
import models


class OAuth2():
    def __init__(self, app: models.App) -> None:
        self.app = app
        self.rest_app = hikari.RESTApp()
        self.client_id = Config.env('CLIENT_ID')
        self.client_secret = Config.env('CLIENT_SECRET')
        self.redirect_uri = Config.env('REDIRECT_URI')

    async def authorize_tokens(self, code: str) -> tuple[str, int]:
        async with self.rest_app.acquire() as client:
            tokens = await client.authorize_access_token(self.client_id, self.client_secret, code, self.redirect_uri)
            return tokens.access_token, tokens.refresh_token

    async def fetch_my_guilds(self, access_token: str) -> tuple[list[hikari.OwnGuild], ...]:
        async with self.rest_app.acquire(access_token) as client:
            guilds = [guild for guild in await client.fetch_my_guilds() if guild.my_permissions & hikari.Permissions.MANAGE_GUILD]
            invite: list[hikari.OwnGuild] = []
            for guild in guilds:
                if await self.app.pool.fetch_value('SELECT guild_id FROM guilds WHERE guild_id = $1', guild.id) is None:
                    invite.append(guild)
            print(invite)
            return guilds, invite

    async def fetch_guild(self, guild_id: t.Union[str, int]) -> hikari.RESTGuild:
        async with self.rest_app.acquire(Config.env('TOKEN'), hikari.TokenType.BOT) as client:
            return await client.fetch_guild(hikari.Snowflake(guild_id))
