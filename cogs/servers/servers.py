from discord import Message
from discord.ext.commands import Cog, group, has_permissions

import config

from helpers.bleed import Bleed
from helpers.managers import Context


class Servers(Cog):
    def __init__(self, bot: Bleed) -> None:
        self.bot: Bleed = bot

    @group(
        name="prefix",
        invoke_without_command=True,
    )
    async def prefix(self, ctx: Context) -> Message:
        """
        View guild prefix
        """

        prefix = (
            await self.bot.db.fetchval(
                """
            SELECT prefix FROM config
            WHERE guild_id = $1
            """,
                ctx.guild.id,
            )
            or config.prefix
        )
        if prefix == "disabled":
            return await ctx.warn(
                f"Your guild doesn't have a **prefix set!** Set it using `@{self.bot.user} prefix add (prefix)`"
            )

        return await ctx.neutral(f"Guild Prefix: `{prefix}`")

    @prefix.command(
        name="remove",
        aliases=[
            "delete",
            "del",
            "clear",
        ],
    )
    @has_permissions(administrator=True)
    async def prefix_remove(self, ctx: Context) -> Message:
        """
        Remove command prefix for guild
        """

        await self.bot.db.execute(
            """
            UPDATE config SET
                prefix = $2
            WHERE guild_id = $1
            """,
            ctx.guild.id,
            "disabled",
        )

        return await ctx.approve(
            f"Your guild's prefix has been **removed**. You can set a **new prefix** using `@{self.bot.user} prefix add (prefix)`"
        )

    @prefix.command(
        name="set",
        usage="(prefix)",
        example="!",
        aliases=["add"],
    )
    @has_permissions(administrator=True)
    async def prefix_set(self, ctx: Context, prefix: str) -> Message:
        """
        Set command prefix for guild
        """

        if len(prefix) > 10:
            return await ctx.warn(
                "Your **prefix** cannot be longer than **10 characters**!"
            )

        await self.bot.db.execute(
            """
            INSERT INTO config (
                guild_id,
                prefix
            ) VALUES ($1, $2)
            ON CONFLICT (guild_id)
            DO UPDATE SET
                prefix = EXCLUDED.prefix;
            """,
            ctx.guild.id,
            prefix.lower(),
        )

        return await ctx.approve(
            f"{'Set' if prefix == config.prefix else 'Replaced'} your current guild's prefix to `{prefix.lower()}`"
        )
